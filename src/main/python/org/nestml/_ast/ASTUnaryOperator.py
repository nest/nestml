"""
@author kperun
TODO header
"""


class ASTUnaryOperator:
    """
    This class is used to store a single unary operator, e.g., ~.
    Grammar:
        unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
    """
    __isUnaryPlus = False
    __isUnaryMinus = False
    __isUnaryTilde = False

    def __init__(self, _isUnaryPlus: bool = False, _isUnaryMinus: bool = False, _isUnaryTilde: bool = False):
        """
        Standard constructor.
        :param _isUnaryPlus: is a unary plus.
        :type _isUnaryPlus: bool
        :param _isUnaryMinus: is a unary minus.
        :type _isUnaryMinus: bool
        :param _isUnaryTilde: is a unary tilde.
        :type _isUnaryTilde: bool
        """
        self.__isUnaryPlus = _isUnaryPlus
        self.__isUnaryMinus = _isUnaryMinus
        self.__isUnaryTilde = _isUnaryTilde

    @classmethod
    def makeASTUnaryOperator(cls, _isUnaryPlus: bool = False, _isUnaryMinus: bool = False, _isUnaryTilde: bool = False):
        """
        The factory method of the ASTUnaryOperator class.
        :param _isUnaryPlus: is a unary plus.
        :type _isUnaryPlus: bool
        :param _isUnaryMinus: is a unary minus.
        :type _isUnaryMinus: bool
        :param _isUnaryTilde: is a unary tilde.
        :type _isUnaryTilde: bool
        :return: a new ASTUnaryOperator object.
        :rtype: ASTUnaryOperator
        """
        return cls(_isUnaryPlus, _isUnaryMinus, _isUnaryTilde)

    def isUnaryPlus(self)->bool:
        """
        Returns whether it is a unary plus.
        :return: True if unary plus, otherwise False.
        :rtype: bool
        """
        return self.__isUnaryPlus

    def isUnaryMinus(self)->bool:
        """
        Returns whether it is a minus plus.
        :return: True if unary minus, otherwise False.
        :rtype: bool
        """
        return self.__isUnaryMinus

    def isUnaryTilde(self)->bool:
        """
        Returns whether it is a tilde plus.
        :return: True if unary tilde, otherwise False.
        :rtype: bool
        """
        return self.__isUnaryTilde

    def print(self) -> str:
        """
        Returns the string representation of the operator.
        :return: the operator as a string.
        :rtype: str
        """
        if self.__isUnaryPlus:
            return '+'
        elif self.__isUnaryMinus:
            return '-'
        elif self.__isUnaryTilde:
            return '~'
        else:
            raise Exception("(NESTML) Unary operator not specified.")