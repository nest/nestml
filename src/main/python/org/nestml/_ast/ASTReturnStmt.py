"""
@author kperun
TODO header
"""
import ASTExpr


class ASTReturnStmt:
    """
    This class is used to store a return statement.
        A ReturnStmt Models the return statement in a function.
        @attribute minus An optional sing
        @attribute definingVariable Name of the variable
        Grammar:
            returnStmt : 'return' expr?;       
    """
    __expr = None

    def __init__(self, _expr: ASTExpr = None):
        """
        Standard constructor.
        :param _expr: an expression.
        :type _expr: ASTExpr
        """
        self.__expr = _expr

    @classmethod
    def makeASTReturnStmt(cls, _expr: ASTExpr = None):
        """
        Factory method of the ASTReturnStmt class.
        :param _expr: an optional return expression.
        :type _expr: ASTExpr
        :return: a new ASTReturnStmt object.
        :rtype: ASTReturnStmt
        """
        return cls(_expr)

    def hasExpr(self) -> bool:
        """
        Returns whether the return statement has an expression or not.
        :return: True if has expression, otherwise False.
        :rtype: bool
        """
        return self.__expr is not None

    def getExpr(self):
        """
        Returns the expression.
        :return: an expression.
        :rtype: ASTExpr
        """
        return self.__expr
