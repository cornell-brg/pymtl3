
from pymtl import *
from BasePass import BasePass
from pymtl.model import Const
import py, ast
from collections import defaultdict

class GenDAGPass( BasePass ):

  def __call__( self, top ):
    top.check()
    self._generate_net_blocks( top )
    self._process_constraints( top )

  def _generate_net_blocks( self, top ):
    """ _generate_net_blocks:
    Each net is an update block. Readers are actually "written" here.
      >>> s.net_reader1 = s.net_writer
      >>> s.net_reader2 = s.net_writer """

    nets = top.get_all_nets()

    top.genblks = set()
    top.genblk_reads  = {}
    top.genblk_writes = {}
    top.genblk_src    = {}

    for writer, readers in nets:
      if not readers:
        continue # Aha, the net is dummy

      wr_lca  = writer.get_host_component()
      rd_lcas = [ x.get_host_component() for x in readers ]
      print wr_lca, rd_lcas

      # Find common ancestor: iteratively go to parent level and check if
      # at the same level all objects' ancestors are the same

      mindep  = min( wr_lca.get_component_level(),
                     min( [ x.get_component_level() for x in rd_lcas ] ) )

      # First navigate all objects to the same level deep

      for i in xrange( mindep, wr_lca.get_component_level() ):
        wr_lca = wr_lca.get_parent_object()

      for i, x in enumerate( rd_lcas ):
        for j in xrange( mindep, x.get_component_level() ):
          x = x.get_parent_object()
        rd_lcas[i] = x

      # Then iteratively check if their ancestor is the same

      while wr_lca is not top:
        succeed = True
        for x in rd_lcas:
          if x is not wr_lca:
            succeed = False
            break
        if succeed: break

        # Bring up all objects for another level
        wr_lca = wr_lca.get_parent_object()
        for i in xrange( len(rd_lcas) ):
          rd_lcas[i] = rd_lcas[i].get_parent_object()

      # 
      lca     = wr_lca # this is the object we want to insert the block to
      lca_len = len( repr(lca) )
      fanout  = len( readers )
      wstr    = repr(writer) if isinstance( writer, Const ) \
                else ( "s." + repr(writer)[lca_len+1:] )
      rstrs   = [ "s." + repr(x)[lca_len+1:] for x in readers]

      upblk_name = "{}__{}".format(repr(writer), fanout) \
                    .replace( ".", "_" ).replace( ":", "_" ) \
                    .replace( "[", "_" ).replace( "]", "" ) \
                    .replace( "(", "_" ).replace( ")", "" )

      # NO @s.update because I don't want to impair the original model

      # if fanout == 1: # simple mode!
        # gen_src = """
          # def {0}():
            # {1}
          # blk = {0}

        # """.format( upblk_name,"{} = {}".format( rstrs[0], wstr ) )
      # else:
        # gen_src = """
          # def {0}():
            # common_writer = {1}
            # {2}
          # blk = {0}
        # """.format( upblk_name, wstr, "; ".join(
                    # [ "{} = common_writer".format( x ) for x in rstrs] ) )
      gen_src = """
def {0}():
  {1} = {2}
_ret_blk = {0}
      """.format( upblk_name, " = ".join( rstrs ), wstr )

      # Borrow the closure of lca to compile the block
      def compile_upblk( s, src ):
        var = locals()
        var.update( globals() )
        exec py.code.Source( src ).compile() in var
        return _ret_blk

      blk         = compile_upblk( lca, gen_src )
      blk.hostobj = lca

      top.genblks.add( blk )
      top.genblk_reads [ blk ] = [ writer ]
      top.genblk_writes[ blk ] = readers[::]
      top.genblk_src   [ blk ] = ( gen_src, ast.parse( gen_src ) )

  def _process_constraints( self, top ):

    # Query update block metadata from top

    update_on_edge                   = top.get_all_upblk_on_edge()
    upblk_reads, upblk_writes, _ = top.get_all_upblk_metadata()
    genblk_reads, genblk_writes  = top.genblk_reads, top.genblk_writes
    U_U, RD_U, WR_U              = top.get_all_explicit_constraints()

    #---------------------------------------------------------------------
    # Explicit constraint
    #---------------------------------------------------------------------
    # Schedule U1 before U2 when U1 == WR(x) < RD(x) == U2: combinational
    #
    # Explicitly, one should define these to invert the implicit constraint:
    # - RD(x) < U when U == WR(x) --> RD(x) ( == U') < U == WR(x)
    # - WR(x) > U when U == RD(x) --> RD(x) == U < WR(x) ( == U')
    # constraint RD(x) < U1 & U2 reads  x --> U2 == RD(x) <  U1
    # constraint RD(x) > U1 & U2 reads  x --> U1 <  RD(x) == U2 # impl
    # constraint WR(x) < U1 & U2 writes x --> U2 == WR(x) <  U1 # impl
    # constraint WR(x) > U1 & U2 writes x --> U1 <  WR(x) == U2
    # Doesn't work for nested data struct and slice:
    
    read_upblks = defaultdict(set)
    write_upblks = defaultdict(set)

    for data in [ upblk_reads, genblk_reads ]:
      for blk, reads in data.iteritems():
        for rd in reads:
          read_upblks[ rd ].add( blk )

    for data in [ upblk_writes, genblk_writes ]:
      for blk, writes in data.iteritems():
        for wr in writes:
          write_upblks[ wr ].add( blk )

    for typ in [ 'rd', 'wr' ]: # deduplicate code
      if typ == 'rd':
        constraints = RD_U
        equal_blks  = read_upblks
      else:
        constraints = WR_U
        equal_blks  = write_upblks

      # enumerate variable objects
      for obj, constrained_blks in constraints.iteritems():

        # enumerate upblks that has a constraint with x
        for (sign, co_blk) in constrained_blks:

          for eq_blk in equal_blks[ obj ]: # blocks that are U == RD(x)
            if co_blk != eq_blk:
              if sign == 1: # RD/WR(x) < U is 1, RD/WR(x) > U is -1
                # eq_blk == RD/WR(x) < co_blk
                expl_constraints.add( (eq_blk, co_blk) )
              else:
                # co_blk < RD/WR(x) == eq_blk
                expl_constraints.add( (co_blk, eq_blk) )

    #---------------------------------------------------------------------
    # Implicit constraint
    #---------------------------------------------------------------------
    # Synthesize total constraints between two upblks that read/write to
    # the "same variable" (we also handle the read/write of a recursively
    # nested field/slice)
    #
    # Implicitly, WR(x) < RD(x), so when U1 writes X and U2 reads x
    # - U1 == WR(x) & U2 == RD(x) --> U1 == WR(x) < RD(x) == U2

    impl_constraints = set()

    # Collect all objs that write the variable whose id is "read"
    # 1) RD A.b.b     - WR A.b.b, A.b, A
    # 2) RD A.b[1:10] - WR A.b[1:10], A.b, A
    # 3) RD A.b[1:10] - WR A.b[0:5], A.b[6], A.b[8:11]

    # Checking if two slices/indices overlap
    def indices_overlap( x, y ):
      if isinstance( x, int ):
        if isinstance( y, int ):  return x == y
        else:                     return y.start <= x < y.stop
      else: # x is slice
        if isinstance( y, int ):  return x.start <= y < x.stop
        else:
          if x.start <= y.start:  return y.start < x.stop
          else:                   return x.start < y.stop

    for obj, rd_blks in read_upblks.iteritems():
      writers = []

      # Check parents. Cover 1) and 2)
      x = obj
      while x:
        if x in write_upblks:
          writers.append( x )
        x = x._nested

      # Check the sibling slices. Cover 3)
      if obj._slice:
        for x in obj._nested._slices.values():
          if indices_overlap( x._slice, obj._slice ) and x in write_upblks:
            writers.append( x )

      # Add all constraints
      for writer in writers:
        for wr_blk in write_upblks[ writer ]:
          for rd_blk in rd_blks:
            if wr_blk != rd_blk:
              if rd_blk in update_on_edge:
                impl_constraints.add( (rd_blk, wr_blk) ) # rd < wr
              else:
                impl_constraints.add( (wr_blk, rd_blk) ) # wr < rd default

    # Collect all objs that read the variable whose id is "write"
    # 1) WR A.b.b.b, A.b.b, A.b, A (detect 2-writer conflict)
    # 2) WR A.b.b.b   - RD A.b.b, A.b, A
    # 3) WR A.b[1:10] - RD A.b[1:10], A,b, A
    # 4) WR A.b[1:10], A.b[0:5], A.b[6] (detect 2-writer conflict)
    # "WR A.b[1:10] - RD A.b[0:5], A.b[6], A.b[8:11]" has been discovered

    for obj, wr_blks in write_upblks.iteritems():
      readers = []

      # Check parents. Cover 2) and 3). 1) and 4) should be detected in elaboration
      x = obj
      while x:
        if x in read_upblks:
          readers.append( x )
        x = x._nested

      # Add all constraints
      for wr_blk in wr_blks:
        for reader in readers:
          for rd_blk in read_upblks[ reader ]:
            if wr_blk != rd_blk:
              if rd_blk in update_on_edge:
                impl_constraints.add( (rd_blk, wr_blk) ) # rd < wr
              else:
                impl_constraints.add( (wr_blk, rd_blk) ) # wr < rd default

    top.all_constraints = U_U.copy()
    for (x, y) in impl_constraints:
      if (y, x) not in U_U: # no conflicting expl
        top.all_constraints.add( (x, y) )