from PyMTLObject     import PyMTLObject
from pymtl.datatypes.Bits import mk_bits
import inspect2

class Connectable(object):

  def __new__( cls, *args, **kwargs ):
    inst = object.__new__( cls )

    # Use disjoint set to resolve connections
    inst._root      = inst
    inst._connected = [ inst ]

    return inst

  def _find_root( s ): # Disjoint set path compression
    if s._root == s:  return s
    s._root = s._root._find_root()
    return s._root

  def _connect( s, other ):
    assert isinstance( other, Connectable ), "Unconnectable object!"

    x = s._find_root()
    y = other._find_root()
    assert x != y, "Two nets are already unionized!"
    # assert x == s, "One net signal cannot have two drivers. \n%s" % \
                   # "Please check if the left side signal is already at left side in another connection."

    # merge myself to the other
    y._connected.extend( x._connected )
    x._connected = []
    x._root = y

  def __ior__( s, other ):
    s._connect( other )
    return s

  def collect_nets( s, varid_net ):
    root = s._find_root()
    if len( root._connected ) > 1: # has actual connection
      if id(root) not in varid_net:
        varid_net[ id(root) ] = root._connected
    else:
      assert root == s, "It doesn't make sense ..."

# Checking if two slices/indices overlap
def overlap( x, y ):
  if isinstance( x, int ):
    if isinstance( y, int ):  return x == y
    else:                     return y.start <= x < y.stop
  else: # x is slice
    if isinstance( y, int ):  return x.start <= y < x.stop
    else:
      if x.start <= y.start:  return y.start < x.stop
      else:                   return x.start < y.stop
  assert False, "What the hell?"
  
class Wire(Connectable, PyMTLObject):

  def __init__( s, type_ ):
    s._type = type_
    s._parent = None # None means it's the top level Wire(msgtype)
    s._slice  = None # None means it's not a slice of some wire
    s._attrs  = {}
    s._slices = {}

  def __getattr__( s, name ):
    if name.startswith("_"): # private variable
      return s.__dict__[ name ]

    if name not in s._attrs:
      x = Wire( getattr(s._type, name) )
      x._parent        = s
      s._attrs[ name ] = x

    return s._attrs[ name ]

  def __setitem__( s, addr, v ):
    pass # I have to override this to support a[0:1] |= b

  def __getitem__( s, addr ):
    # Turn index into a slice
    if isinstance( addr, int ):
      sl = slice( addr, addr+1 )
    elif isinstance( addr, slice ):
      sl = addr
    else: assert False, "What the hell?"

    sl_tuple = (sl.start, sl.stop)

    if sl_tuple not in s._slices:
      x = Wire( mk_bits( sl.stop - sl.start) )
      x._parent = s
      x._slice  = sl
      s._slices[ sl_tuple ] = x
    return s._slices[ sl_tuple ]

  # The getattr and getitem are overriden, so we need to rewrite these
  # reflection loop
  def _recursive_elaborate( s ):
    for name, obj in s._attrs.iteritems():
      s._recursive_expand( obj )
    for name, obj in s._slices.iteritems():
      s._recursive_expand( obj )

  def _recursive_tag_name( s ):
    for name, obj in s._attrs.iteritems():
      s._recursive_tag_expand( name, obj, [] )
    for name, obj in s._slices.iteritems():
      s._recursive_tag_expand( "", obj, [obj._slice] )

  # Override
  def collect_nets( s, varid_net ):
    super( Wire, s ).collect_nets( varid_net )
    if not s._attrs and not s._slices:
      return

    for name, obj in s._attrs.iteritems():
      obj.collect_nets( varid_net )
    for name, obj in s._slices.iteritems():
      obj.collect_nets( varid_net )

  def default_value( s ):
    return s._type()

  # Override
  def __ior__( s, other ):
    if isinstance( other, Wire ):
      s._connect( other )
    else:
      assert False, other
    return s

class ValuePort(Wire):
  pass

class MethodPort(Connectable, PyMTLObject):

  def __init__( self, *args ):
    self._has_method = False
    assert len(args) <= 1
    if args:
      other = args[0]
      assert isinstance( other, MethodPort ), "Cannot connect to %s, which is not a MethodPort."
      self._connect( other )

  def attach_method( self, func ):
    self._func = func
    self._name = func.__name__
    self._has_method = True

  def has_method( self ):
    return self._has_method

  def __call__( self, *args, **kwargs ):
    return self._func( *args, **kwargs )

  # Override
  def _connect( self, other ):
    assert isinstance( other, MethodPort ), "Cannot connect MethodPort to %s" % type(other).__name__
    super( MethodPort, self )._connect( other )

  # Override
  def collect_nets( s, varid_net ):
    pass

class PortBundle(Connectable, PyMTLObject):

  # Override
  def _connect( s, other ):
    # print inspect2.stack()[2][0].f_locals['s'].__dict__

    # Expand the list when needed. Only connect connectables and return,
    # inheritance will figure out what to do with Port/PortBundle

    def recursive_connect( s_obj, other_obj ):
      if   isinstance( s_obj, list ):
        for i in xrange(len(s_obj)):
          recursive_connect( s_obj[i], other_obj[i] )
      elif isinstance( s_obj, Connectable ):
        s_obj._connect( other_obj )

    assert isinstance( other, PortBundle ),  "Invalid connection, %s <> %s." % (type(s).__name__, type(other).__name__)

    if not (type(s) is type(other)):
      assert  s.Type == other.Type, "Invalid connection, %s <> %s." % (type(s).__name__, type(other).__name__)
      print "warning: need to generate adapters for this connection between %s and %s." % (type(s).__name__, type(other).__name__)

    for name, obj in s.__dict__.iteritems():
      if not name.startswith("_"):
        recursive_connect( obj, getattr(other, name) )

  # Override
  def collect_nets( s, varid_net ):

    # Expand the list when needed. Only collect connectables and return
    def recursive_collect( obj, varid_net ):
      if   isinstance( obj, list ):
        for i in xrange(len(obj)):
          recursive_collect( obj[i], varid_net )
      elif isinstance( obj, Connectable ):
        obj.collect_nets( varid_net )

    for name, obj in s.__dict__.iteritems():
      if not name.startswith("_"):
        recursive_collect( obj, varid_net )