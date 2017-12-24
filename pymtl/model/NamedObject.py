#=========================================================================
# NamedObject.py
#=========================================================================
# This is the very base class of PyMTL objects. I put it to enable all
# pymtl components to share the functionality of recursively collecting
# objects and tagging objects with the full name.
#
# We bookkeep name hierarchy for error message and other purposes.
# For example, s.x[0][3].y[2].z[1:3] is stored as
# ( ["top","x","y","z"], [ [], [0,3], [2], [slice(1,3,0)] ] )
# Note that len(name) == len(idx)-1 only when the variable ends with slice

from errors import NotElaboratedError

class NamedObject(object):

  def __new__( cls, *args, **kwargs ):
    inst = super( NamedObject, cls ).__new__( cls )

    # save parameters

    inst._args   = args
    inst._kwargs = kwargs

    return inst

  #-----------------------------------------------------------------------
  # Private methods
  #-----------------------------------------------------------------------

  def __setattr_for_elaborate__( s, name, obj ):

    def recursive_expand( child, indices ):

      if   isinstance( child, NamedObject ):
        child._parent_obj  = (s, )
        child._my_name_idx = ( name, indices )

        sname, sidx          = s._full_name_idx
        child._full_name_idx = ( sname + [name], sidx + [indices] )

        child.construct( *child._args, **child._kwargs )

      # ONLY LIST IS SUPPORTED, SORRY.
      # I don't want to support any iterable object because later "Wire"
      # can be infinitely iterated and cause infinite loop. Special casing
      # Wire will be a mess around everywhere.

      elif isinstance( child, list ):
        for i, obj in enumerate( child ):
          recursive_expand( obj, indices + [i] )

    if not name.startswith("_"):
      recursive_expand( obj, [] )

    super( NamedObject, s ).__setattr__( name, obj )

  # Filter objects

  def _recursive_collect( s, filt=lambda x: isinstance( NamedObject, x ) ):

    def _expand( child ):

      # Jump back to main function when it's another named object
      if   isinstance( child, NamedObject ):
        _collect( child )

      # ONLY LIST IS SUPPORTED
      elif isinstance( child, list ):
        for i, o in enumerate( child ):
          _expand( o )

    # If the id is string, it is a normal children field. Otherwise it
    # should be an tuple that represents a slice

    def _collect( m ):

      if filt( m ):
        ret.add( m )

      # Jump to the expand function to check the type of child object
      for name, obj in m.__dict__.iteritems():

        if   isinstance( name, basestring ): # python2 specific
          if not name.startswith("_"): # filter private variables
            _expand( obj )

        elif isinstance( name, tuple ): # name = [1:3]
          _expand( obj )

    ret = set()
    _collect( s )
    return ret

  # Developers should use repr(x) everywhere to get the name

  def __repr__( s ):
    if not s._full_name_idx: # if not tagged, go with class & address ...
      return super( NamedObject, s ).__repr__()

    name, idx = s._full_name_idx
    name_len = len(name)
    idx_len  = len(idx)

    ret = ".".join( [ "{}{}".format( name[i],
                                     "".join([ "[{}]".format(x)
                                                for x in idx[i] ]) )
                      for i in xrange(name_len) ] )

    if name_len == idx_len: return ret

    # The only place we allow slicing is the end
    assert name_len == idx_len-1

    # Only one slice allowed
    last_idx = idx[-1]
    assert len(last_idx) == 1

    return ret + "[{}:{}]".format( last_idx[0].start, last_idx[0].stop )

  def elaborate( s ):

    # Initialize the top level

    s._parent_obj = None
    s._full_name_idx = ( ["s"], [ [] ] )
    s._my_name_idx   = ( "s", [] )

    # Override setattr for elaboration, and then remove it

    NamedObject.__setattr__ = NamedObject.__setattr_for_elaborate__
    s.construct( *s._args, **s._kwargs )
    del NamedObject.__setattr__

  def construct( s ):
    pass

  #-----------------------------------------------------------------------
  # Public APIs (only can be called after elaboration)
  #-----------------------------------------------------------------------

  def get_parent_object( s ):
    try:
      return s._parent_obj
    except AttributeError:
      raise NotElaboratedError()
