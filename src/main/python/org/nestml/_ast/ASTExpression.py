"""
@autor kperun
TODO header
"""


class ASTExpr:
    """
    ASTExpr, i.e., several subexpressions combined by one or more operators, e.g., 10mV + V_m - (V_reset * 2)/ms ....
    or a simple expression, e.g. 10mV.
    Grammar: 
      expression : leftParentheses='(' expression rightParentheses=')'
             | <assoc=right> base=expression powOp='**' exponent=expression
             | unaryOperator term=expression
             | left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
             | left=expression (plusOp='+'  | minusOp='-') right=expression
             | left=expression bitOperator right=expression
             | left=expression comparisonOperator right=expression
             | logicalNot='not' expression
             | left=expression logicalOperator right=expression
             | condition=expression '?' ifTrue=expression ':' ifNot=expression
             | simpleExpression
             ;
    """
    # encapsulated
    __hasLeftParentheses = False
    __hasRightParentheses = False
    # exponent expression
    __base = None
    __exponent = None
    # a term
    __unaryOperator = None
    __term = None
    # lhs and rhs combined by an operator
    __arithmeticOperator = None
    __bitOperator = None
    __comparisonOperator = None
    __logicalOperator = None
    __lhs = None
    __rhs = None
    # a negated expression
    __isLogicalNot = False
    __negatedExpression = None
    # ternary operator
    __condition = None
    __ifTrue = None
    __ifNot = None
    # the simplest case: a simple expression, e.g. 10mV
    __simpleExpression = None


