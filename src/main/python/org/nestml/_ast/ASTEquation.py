"""
TODO header
@author kperun
"""
import ASTDerivative
import ASTExpr


class ASTEquation:
    """
    This class is used to store ast equations, e.g., V_m' = 10mV + V_m.
    """
    __lhs = None
    __rhs = None

    def __init__(self, _lhs: ASTDerivative = None, _rhs: ASTExpr = None):
        """
        Standard constructor.
        :param _lhs: an object of type ASTDerivative
        :type _lhs: ASTDerivative
        :param _rhs: an object of type ASTExpr
        :type _rhs: ASTExpr
        """
        self.__lhs = _lhs
        self.__rhs = _rhs

    @classmethod
    def makeASTEquation(cls, _lhs: ASTDerivative = None, _rhs: ASTExpr = None):
        """
        A factory method used to generate new ASTEquation.
        :param _lhs: an object of type ASTDerivative
        :type _lhs: ASTDerivative
        :param _rhs: an object of type ASTExpr
        :type _rhs: ASTExpr
        """
        return cls(_lhs, _rhs)

    def getLhs(self) -> ASTDerivative:
        """
        Returns the left-hand side of the equation.
        :return: an object of the ast-derivative class.
        :rtype: ASTDerivative
        """
        return self.__lhs

    def getRhs(self) -> ASTExpr:
        """
        Returns the left-hand side of the equation.
        :return: an object of the ast-expr class.
        :rtype: ASTExpr
        """
        return self.__rhs
