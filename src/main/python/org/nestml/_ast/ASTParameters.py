"""
@author kperun
TODO header
"""
import ASTParameter


class ASTParameters:
    """
    This class is used to store a set of parameters.
    ASTParameters models parameter list in function declaration.
    @attribute parameters List with parameters.
    Grammar:
        parameters : parameter (',' parameter)*;
    """
    __parameterList = None

    def __init__(self, _parameterList: list = list()):
        """
        Standard constructor.
        :param _parameterList: a list of parameter objects. 
        :type _parameterList: list(ASTParameter)
        """
        self.__parameterList = _parameterList

    @classmethod
    def makeASTParameters(cls,_parameterList: list = list()):
        """
        Factory method of the ASTParameters class.
        :param _parameterList: a list of parameter objects. 
        :type _parameterList: list(ASTParameter)
        :return: a new ASTParameters object.
        :rtype: ASTParameters
        """

    def getParametersList(self):
        """
        Returns the list of parameters.
        :return: a list of parameter objects.
        :rtype: list(ASTParameter)
        """
        return self.__parameterList
