"""
========================================================================
SimpleSchedulePass.py
========================================================================
Generate a simple schedule (no Mamba techniques here) based on the
DAG generated by some previous pass.

Author : Shunning Jiang
Date   : Dec 26, 2018
"""

from pymtl3.dsl.errors import UpblkCyclicError

from .BasePass import BasePass, PassMetadata
from .errors import PassOrderError


def make_double_buffer_func( s ):

  strs = [ f"{repr(x)}._flip()" for x in s._dsl.all_signals if x._dsl.needs_double_buffer ]

  if not strs:
    def no_double_buffer():
      pass
    return no_double_buffer

  src = """
  def double_buffer():
    {}
  """.format( "\n    ".join(strs) )

  import py
  # print(src)
  local = locals()
  exec(py.code.Source( src ).compile(), local)
  return local['double_buffer']

class SimpleSchedulePass( BasePass ):
  def __call__( self, top ):
    if not hasattr( top._dag, "all_constraints" ):
      raise PassOrderError( "all_constraints" )

    top._sched = PassMetadata()

    top._sched.schedule = self.schedule( top )

  def schedule( self, top ):

    # Construct the graph

    V   = top._dag.final_upblks - top.get_all_update_ff()
    E   = top._dag.all_constraints
    Es  = { v: [] for v in V }
    InD = { v: 0  for v in V }

    import os
    if 'MAMBA_DAG' in os.environ:
      dump_dag( top, V, E )

    for (u, v) in E: # u -> v
      InD[v] += 1
      Es [u].append( v )

    # Perform topological sort for a serial schedule.

    update_schedule = []

    Q = [ v for v in V if not InD[v] ]

    import random
    while Q:
      random.shuffle(Q)
      u = Q.pop()
      update_schedule.append( u )
      for v in Es[u]:
        InD[v] -= 1
        if not InD[v]:
          Q.append( v )

    check_schedule( top, update_schedule, V, E, InD )

    schedule = list(top._dsl.all_update_ff)
    schedule.append( make_double_buffer_func( top ) )
    schedule.extend( update_schedule )

    return schedule

def dump_dag( top, V, E ):
  from graphviz import Digraph
  from pymtl3.dsl import CalleePort
  dot = Digraph()
  dot.graph_attr["rank"] = "same"
  dot.graph_attr["ratio"] = "compress"
  dot.graph_attr["margin"] = "0.1"

  for x in V:
    x_name = repr(x) if isinstance( x, CalleePort ) else x.__name__
    try:
      x_host = repr(x.get_parent_object() if isinstance( x, CalleePort )
                    else top.get_update_block_host_component(x))
    except:
      x_host = ""
    dot.node( x_name +"\\n@" + x_host, shape="box")

  for (x, y) in E:
    x_name = repr(x) if isinstance( x, CalleePort ) else x.__name__
    try:
      x_host = repr(x.get_parent_object() if isinstance( x, CalleePort )
                    else top.get_update_block_host_component(x))
    except:
      x_host = ""
    y_name = repr(y) if isinstance( y, CalleePort ) else y.__name__
    try:
      y_host = repr(y.get_parent_object() if isinstance( y, CalleePort )
                    else top.get_update_block_host_component(y))
    except:
      y_host = ""

    dot.edge( x_name+"\\n@"+x_host, y_name+"\\n@"+y_host )
  dot.render( "/tmp/upblk-dag.gv", view=True )

def check_schedule( top, schedule, V, E, in_degree ):

  if len(schedule) != len(V):
    V_leftovers = {  v for v in V if in_degree[v]  }
    E_leftovers = {  (x,y) for (x,y) in E
                         if x in V_leftovers and y in V_leftovers  }
    dump_dag( top, V_leftovers, E_leftovers )

    raise UpblkCyclicError( """
Update blocks have cyclic dependencies.
* Please consult update dependency graph for details."
    """)
