"""
@autor kperun
TODO header
"""


class ASTExpr:
    """
    This class is used to store compound expressions.
    
    ASTExpr, i.e., several subexpressions combined by one or more
    operators, e.g., 10mV + V_m - (V_reset * 2)/ms ....
    or a simple expression, e.g. 10mV.
    Grammar:
          expr : leftParentheses='(' expr rightParentheses=')'
                 | <assoc=right> base=expr powOp='**' exponent=expr
                 | unaryOperator term=expr
                 | left=expr (timesOp='*' | divOp='/' | moduloOp='%') right=expr
                 | left=expr (plusOp='+'  | minusOp='-') right=expr
                 | left=expr bitOperator right=expr
                 | left=expr comparisonOperator right=expr
                 | logicalNot='not' expr
                 | left=expr logicalOperator right=expr
                 | condition=expr '?' ifTrue=expr ':' ifNot=expr
                 | simpleExpr
                 ;
    """
    TODO = "TODO"
