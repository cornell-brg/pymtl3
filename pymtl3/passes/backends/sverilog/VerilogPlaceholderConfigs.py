#=========================================================================
# VerilogPlaceholderConfigs.py
#=========================================================================
# Author : Peitian Pan
# Date   : Jul 28, 2019
"""Configuration of Verilog placeholders."""

from copy import deepcopy
import os

from pymtl3.passes.PassConfigs import Checker
from pymtl3.passes.PlaceholderConfigs import PlaceholderConfigs, expand


class VerilogPlaceholderConfigs( PlaceholderConfigs ):

  VerilogOptions = {
    # Parameters
    # Map the names of parameters to their values
    # If {} is provided, use the parameters inferred from `construct` instead
    "params" : {},

    # Port name mapping
    # Map PyMTL port names to external port names
    "port_map" : {},

    # Expects the name of the top component in external source files
    # "" to use name of the current component to be imported
    "top_module" : "",

    # Expects path of the file that contains the top module
    "src_file" : "",

    # -f
    # Expects the path to the flist file; "" to disable this option
    "v_flist" : "",

    # -I ( alias of -y and +incdir+ )
    # Expects a list of include paths; [] to disable this option
    "v_include" : [],
  }

  VerilogCheckers = {
    ("params", "port_map") : Checker( lambda v: isinstance(v, dict), "expects a dict"),

    "top_module": Checker( lambda v: isinstance(v, str) and v, "expects a non-empty string"),

    "src_file": Checker( lambda v: isinstance(v, str) and (os.path.isfile(expand(v)) or not v),
                "src_file should be a path to a file or an empty string!" ),

    "v_flist": Checker( lambda v: isinstance(v, str) and os.path.isfile(expand(v)) or v == "",
                         "expects a path to a file" ),

    "v_include": Checker( lambda v: isinstance(v, list) and all(os.path.isdir(expand(p)) for p in v),
                            "expects a list of paths to directory"),
  }

  PassName = 'VerilogPlaceholderConfigs'

  def __new__( cls, *args, **kwargs ):
    inst = super().__new__( cls )
    assert len(args) == 0, "We only accept keyword arguments here."

    cls.Options  = deepcopy( PlaceholderConfigs.Options )
    cls.Checkers = deepcopy( PlaceholderConfigs.Checkers )

    for key, val in cls.VerilogOptions.items():
      assert key not in cls.Options,\
        f'config {key} is duplicated between PlaceholderConfigs and VerilogPlaceholderConfigs'
      cls.Options[key] = val

    all_checkers = inst._get_all_checker_configs( cls )

    for cfgs, chk in cls.VerilogCheckers.items():
      if isinstance( cfgs, tuple ):
        for cfg in cfgs:
          inst._add_to_checkers( cls.Checkers, cfg, chk )
      elif isinstance( cfgs, str ):
        inst._add_to_checkers( cls.Checkers, cfgs, chk )

    return inst

  # Override
  def check( s ):
    super().check()

    # Exactly one of src_file and v_flist should be non-empty
    if (s.v_flist and os.path.isfile(expand(s.src_file))) or \
       (not s.v_flist and not os.path.isfile(expand(s.src_file))):
      raise InvalidPassOptionValue( 'src_file', s.src_file, s.PassName,
          'exactly one of src_file and v_flist should be non-emtpy!' )

  def get_port_map( s ):
    pmap = s.port_map
    return lambda name: pmap[name] if name in pmap else name

  def _get_all_checker_configs( s, cls ):
    ret = []
    for cfgs in cls.Checkers.keys():
      if isinstance( cfgs, tuple ):
        for cfg in cfgs:
          ret.append( cfg )
      elif isinstance( cfgs, str ):
        ret.append( cfgs )
    return ret

  def _add_to_checkers( s, checkers, cfg, chk ):
    assert cfg not in checkers,\
      f'config {cfg} is duplicated between PlaceholderConfigs!'
    checkers[cfg] = chk