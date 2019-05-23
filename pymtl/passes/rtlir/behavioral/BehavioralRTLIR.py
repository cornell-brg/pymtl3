#=========================================================================
# BehavioralRTLIR.py
#=========================================================================
"""Provide behavioral RTLIR AST node types.

This file is automatically generated by BehavioralRTLIRImplGen.py.
"""

class BaseBehavioralRTLIR( object ):
  """Base class for all behavioral RTLIR AST nodes."""
  def __eq__( s, other ):
    return type(s) is type(other)

  def __ne__( s, other ):
    return not s.__eq__( other )

class CombUpblk( BaseBehavioralRTLIR ):
  def __init__( s, name, body ):
    s.name = name
    s.body = body

  def __eq__( s, other ):
    if not isinstance(other, CombUpblk) or s.name != other.name:
      return False
    for x, y in zip( s.body, other.body ):
      if x != y:
        return False
    return True

class SeqUpblk( BaseBehavioralRTLIR ):
  def __init__( s, name, body ):
    s.name = name
    s.body = body

  def __eq__( s, other ):
    if not isinstance(other, SeqUpblk) or s.name != other.name:
      return False
    for x, y in zip( s.body, other.body ):
      if x != y:
        return False
    return True

class Assign( BaseBehavioralRTLIR ):
  def __init__( s, target, value ):
    s.target = target
    s.value = value

  def __eq__( s, other ):
    return isinstance(other, Assign) and s.target == other.target and s.value == other.value

class AugAssign( BaseBehavioralRTLIR ):
  def __init__( s, target, op, value ):
    s.target = target
    s.op = op
    s.value = value

  def __eq__( s, other ):
    return isinstance(other, AugAssign) and s.target == other.target and s.op == other.op and s.value == other.value

class If( BaseBehavioralRTLIR ):
  def __init__( s, cond, body, orelse ):
    s.cond = cond
    s.body = body
    s.orelse = orelse

  def __eq__( s, other ):
    if not isinstance(other, If) or s.cond != other.cond:
      return False
    for x, y in zip( s.body, other.body ):
      if x != y:
        return False
    for x, y in zip( s.orelse, other.orelse ):
      if x != y:
        return False
    return True

class For( BaseBehavioralRTLIR ):
  def __init__( s, var, start, end, step, body ):
    s.var = var
    s.start = start
    s.end = end
    s.step = step
    s.body = body

  def __eq__( s, other ):
    if not isinstance(other, For) or s.var != other.var or s.start != other.start or s.end != other.end or s.step != other.step:
      return False
    for x, y in zip( s.body, other.body ):
      if x != y:
        return False
    return True

class Number( BaseBehavioralRTLIR ):
  def __init__( s, value ):
    s.value = value

  def __eq__( s, other ):
    return isinstance(other, Number) and s.value == other.value

class Concat( BaseBehavioralRTLIR ):
  def __init__( s, values ):
    s.values = values

  def __eq__( s, other ):
    if not isinstance(other, Concat):
      return False
    for x, y in zip( s.values, other.values ):
      if x != y:
        return False
    return True

class ZeroExt( BaseBehavioralRTLIR ):
  def __init__( s, nbits, value ):
    s.nbits = nbits
    s.value = value

  def __eq__( s, other ):
    return isinstance(other, ZeroExt) and s.nbits == other.nbits and s.value == other.value

class SignExt( BaseBehavioralRTLIR ):
  def __init__( s, nbits, value ):
    s.nbits = nbits
    s.value = value

  def __eq__( s, other ):
    return isinstance(other, SignExt) and s.nbits == other.nbits and s.value == other.value

class Reduce( BaseBehavioralRTLIR ):
  def __init__( s, op, value ):
    s.op = op
    s.value = value

  def __eq__( s, other ):
    return isinstance(other, Reduce) and s.op == other.op and s.value == other.value

class SizeCast( BaseBehavioralRTLIR ):
  def __init__( s, nbits, value ):
    s.nbits = nbits
    s.value = value

  def __eq__( s, other ):
    return isinstance(other, SizeCast) and s.nbits == other.nbits and s.value == other.value

class StructInst( BaseBehavioralRTLIR ):
  def __init__( s, struct, values ):
    s.struct = struct
    s.values = values

  def __eq__( s, other ):
    if not isinstance(other, StructInst) or s.struct != other.struct:
      return False
    for x, y in zip( s.values, other.values ):
      if x != y:
        return False
    return True

class IfExp( BaseBehavioralRTLIR ):
  def __init__( s, cond, body, orelse ):
    s.cond = cond
    s.body = body
    s.orelse = orelse

  def __eq__( s, other ):
    return isinstance(other, IfExp) and s.cond == other.cond and s.body == other.body and s.orelse == other.orelse

class UnaryOp( BaseBehavioralRTLIR ):
  def __init__( s, op, operand ):
    s.op = op
    s.operand = operand

  def __eq__( s, other ):
    return isinstance(other, UnaryOp) and s.op == other.op and s.operand == other.operand

class BoolOp( BaseBehavioralRTLIR ):
  def __init__( s, op, values ):
    s.op = op
    s.values = values

  def __eq__( s, other ):
    if not isinstance(other, BoolOp) or s.op != other.op:
      return False
    for x, y in zip( s.values, other.values ):
      if x != y:
        return False
    return True

class BinOp( BaseBehavioralRTLIR ):
  def __init__( s, left, op, right ):
    s.left = left
    s.op = op
    s.right = right

  def __eq__( s, other ):
    return isinstance(other, BinOp) and s.left == other.left and s.op == other.op and s.right == other.right

class Compare( BaseBehavioralRTLIR ):
  def __init__( s, left, op, right ):
    s.left = left
    s.op = op
    s.right = right

  def __eq__( s, other ):
    return isinstance(other, Compare) and s.left == other.left and s.op == other.op and s.right == other.right

class Attribute( BaseBehavioralRTLIR ):
  def __init__( s, value, attr ):
    s.value = value
    s.attr = attr

  def __eq__( s, other ):
    return isinstance(other, Attribute) and s.value == other.value and s.attr == other.attr

class Index( BaseBehavioralRTLIR ):
  def __init__( s, value, idx ):
    s.value = value
    s.idx = idx

  def __eq__( s, other ):
    return isinstance(other, Index) and s.value == other.value and s.idx == other.idx

class Slice( BaseBehavioralRTLIR ):
  def __init__( s, value, lower, upper ):
    s.value = value
    s.lower = lower
    s.upper = upper

  def __eq__( s, other ):
    return isinstance(other, Slice) and s.value == other.value and s.lower == other.lower and s.upper == other.upper

class Base( BaseBehavioralRTLIR ):
  def __init__( s, base ):
    s.base = base

  def __eq__( s, other ):
    return isinstance(other, Base) and s.base == other.base

class LoopVar( BaseBehavioralRTLIR ):
  def __init__( s, name ):
    s.name = name

  def __eq__( s, other ):
    return isinstance(other, LoopVar) and s.name == other.name

class FreeVar( BaseBehavioralRTLIR ):
  def __init__( s, name, obj ):
    s.name = name
    s.obj = obj

  def __eq__( s, other ):
    return isinstance(other, FreeVar) and s.name == other.name and s.obj == other.obj

class TmpVar( BaseBehavioralRTLIR ):
  def __init__( s, name, upblk_name ):
    s.name = name
    s.upblk_name = upblk_name

  def __eq__( s, other ):
    return isinstance(other, TmpVar) and s.name == other.name and s.upblk_name == other.upblk_name

class LoopVarDecl( BaseBehavioralRTLIR ):
  def __init__( s, name ):
    s.name = name

  def __eq__( s, other ):
    return isinstance(other, LoopVarDecl) and s.name == other.name

class Invert( BaseBehavioralRTLIR ):
  pass

class Not( BaseBehavioralRTLIR ):
  pass

class UAdd( BaseBehavioralRTLIR ):
  pass

class USub( BaseBehavioralRTLIR ):
  pass

class And( BaseBehavioralRTLIR ):
  pass

class Or( BaseBehavioralRTLIR ):
  pass

class Add( BaseBehavioralRTLIR ):
  pass

class Sub( BaseBehavioralRTLIR ):
  pass

class Mult( BaseBehavioralRTLIR ):
  pass

class Div( BaseBehavioralRTLIR ):
  pass

class Mod( BaseBehavioralRTLIR ):
  pass

class Pow( BaseBehavioralRTLIR ):
  pass

class ShiftLeft( BaseBehavioralRTLIR ):
  pass

class ShiftRightLogic( BaseBehavioralRTLIR ):
  pass

class BitAnd( BaseBehavioralRTLIR ):
  pass

class BitOr( BaseBehavioralRTLIR ):
  pass

class BitXor( BaseBehavioralRTLIR ):
  pass

class Eq( BaseBehavioralRTLIR ):
  pass

class NotEq( BaseBehavioralRTLIR ):
  pass

class Lt( BaseBehavioralRTLIR ):
  pass

class LtE( BaseBehavioralRTLIR ):
  pass

class Gt( BaseBehavioralRTLIR ):
  pass

class GtE( BaseBehavioralRTLIR ):
  pass

class BehavioralRTLIRNodeVisitor( object ):
  """Class for behavioral RTLIR AST visitors."""
  def visit( self, node, *args ):
    method = 'visit_' + node.__class__.__name__
    visitor = getattr( self, method, self.generic_visit )
    return visitor( node, *args )

  def generic_visit( self, node, *args ):
    for field, value in vars(node).iteritems():
      if isinstance( value, list ):
        for item in value:
          if isinstance( item, BaseBehavioralRTLIR ):
            self.visit( item, *args )
      elif isinstance( value, BaseBehavioralRTLIR ):
        self.visit( value, *args )
