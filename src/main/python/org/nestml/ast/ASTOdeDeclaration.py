"""
TODO header
@author kperun
"""
from src.main.python.org.nestml.ast.ASTEquation import ASTEquation
from src.main.python.org.nestml.ast.ASTShape import ASTShape
from src.main.python.org.nestml.ast.ASTOdeFunction import ASTOdeFunction


class ASTOdeDeclaration:
    """
    This class is used to store an arbitrary ODE declaration, e.g., a shape.
    """
    __equations = None
    __shapes = None
    __odeFunctions = None

    def __init__(self, _equations: list = list(), _shapes: list = list(),
                 _odeFunctions: list = list()):
        """
        Standard constructor.
        :param _equations: a list of ASTEquation elements.
        :type _equations: list(ASTEquation)
        :param _shapes: a list of ASTShape elements.
        :type _shapes: list(ASTShape)
        :param _odeFunctions: a list of ASTOdeFunction elements.
        :type _odeFunctions: list(ASTOdeFunction).
        """
        self.__equations = _equations
        self.__shapes = _shapes
        self.__odeFunctions = _odeFunctions

    @classmethod
    def makeASTOdeDeclaration(cls, _equations: list = list(), _shapes: list = list(),
                              _odeFunctions: list = list()):
        """
        A factory method used to generate new ASTOdeDeclaration.
        :param _equations: a list of ASTEquation elements.
        :type _equations: list(ASTEquation)
        :param _shapes: a list of ASTShape elements.
        :type _shapes: list(ASTShape)
        :param _odeFunctions: a list of ASTOdeFunction elements.
        :type _odeFunctions: list(ASTOdeFunction).
        """
        return cls(_equations, _shapes, _odeFunctions)

    def getEquations(self):
        """
        Returns the list of stored equation objects.
        :return: a list of ASTEquation objects.
        :rtype: list(ASTEquation)
        """
        return self.__equations

    def getShapes(self):
        """
        Returns the list of stored shape objects.
        :return: a list of ASTShape objects.
        :rtype: list(ASTShape)
        """
        return self.__shapes

    def getOdeFunction(self):
        """
        Returns the list of stored ode function objects.
        :return: a list of ASTShape objects.
        :rtype: list(ASTOdeFunction)
        """
        return self.__odeFunctions
