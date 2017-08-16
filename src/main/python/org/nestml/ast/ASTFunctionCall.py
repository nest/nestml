"""
@author kperun
TODO header
"""
from src.main.python.org.nestml.ast.ASTExpression import *


class ASTFunctionCall:
    """
    This class is used to store a single function call.
    ASTFunctionCall Represents a function call, e.g. myFun("a", "b").
    @attribute name The (qualified) name of the function
    @attribute args Comma separated list of expressions representing parameters.
    Grammar:
        functionCall : calleeName=NAME '(' (args=arguments)? ')';
    """
    __calleeName = None
    __args = None

    def __init__(self, _calleeName: str = None, _args: list = None):
        """
        Standard constructor.
        :param _calleeName: the name of the function which is called.
        :type _calleeName: str
        :param _args: (Optional) List of arguments
        :type _args: list(ASTExpression)
        """
        assert _calleeName is not None, "(NESTML) Name of called function must not be None"
        self.__calleeName = _calleeName
        self.__args = _args

    @classmethod
    def makeASTFunctionCall(cls, _calleeName: str = None, _args: list = None):
        """
        Factory method of the ASTFunctionCall class.
        :param _calleeName: the name of the function which is called.
        :type _calleeName: str
        :param _args: (Optional) List of arguments
        :type _args: list(ASTExpression)
        :return: a new ASTFunctionCall object.
        :rtype: ASTFunctionCall
        """
        return cls(_calleeName, _args)

    def getName(self) -> str:
        """
        Returns the name of the called function.
        :return: the name of the function.
        :rtype: str.
        """
        return self.__calleeName

    def hasArgs(self) -> bool:
        """
        Returns whether function call has arguments or not.
        :return: True if has arguments, otherwise False.
        :rtype: bool
        """
        return (self.__args is not None) and len(self.__args) > 0

    def getArgs(self):
        """
        Returns the list of arguments.
        :return: the list of arguments.
        :rtype: list(ASTExpression)
        """
        return self.__args

    def print(self) -> str:
        """
        Returns the string representation of the function call.
        :return: the function call as a string.
        :rtype: str
        """
        ret = str(self.__calleeName) + '('
        for i in range(0, len(self.__args)):
            ret += self.__args[i].print()
            if i < len(self.__args):  # in the case that it is not the last arg, print also a comma
                ret += ','
        ret += ')'
        return ret
