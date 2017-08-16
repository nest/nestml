"""
@author kperun
TODO header
"""
from pynestml.src.main.python.org.nestml.ast.ASTExpression import ASTExpression


class ASTReturnStmt:
    """
    This class is used to store a return statement.
        A ReturnStmt Models the return statement in a function.
        @attribute minus An optional sing
        @attribute definingVariable Name of the variable
        Grammar:
            returnStmt : 'return' expr?;       
    """
    __expression = None

    def __init__(self, _expression=None):
        """
        Standard constructor.
        :param _expression: an expression.
        :type _expression: ASTExpression
        """
        self.__expression = _expression

    @classmethod
    def makeASTReturnStmt(cls, _expression=None):
        """
        Factory method of the ASTReturnStmt class.
        :param _expression: an optional return expression.
        :type _expression: ASTExpression
        :return: a new ASTReturnStmt object.
        :rtype: ASTReturnStmt
        """
        assert (_expression is None or isinstance(_expression, ASTExpression))
        return cls(_expression)

    def hasExpr(self):
        """
        Returns whether the return statement has an expression or not.
        :return: True if has expression, otherwise False.
        :rtype: bool
        """
        return self.__expression is not None

    def getExpr(self):
        """
        Returns the expression.
        :return: an expression.
        :rtype: ASTExpression
        """
        return self.__expression
