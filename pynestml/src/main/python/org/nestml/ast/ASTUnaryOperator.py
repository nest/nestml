"""
@author kperun
TODO header
"""
from __future__ import print_function


class ASTUnaryOperator:
    """
    This class is used to store a single unary operator, e.g., ~.
    Grammar:
        unaryOperator : (unaryPlus='+' | unaryMinus='-' | unaryTilde='~');
    """
    __isUnaryPlus = False
    __isUnaryMinus = False
    __isUnaryTilde = False

    def __init__(self, _isUnaryPlus=False, _isUnaryMinus=False, _isUnaryTilde=False):
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
    def makeASTUnaryOperator(cls, _isUnaryPlus=False, _isUnaryMinus=False, _isUnaryTilde=False):
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
        assert (_isUnaryTilde or _isUnaryMinus or _isUnaryPlus), '(PyNESTML.AST) Type of unary operator not specified.'
        return cls(_isUnaryPlus, _isUnaryMinus, _isUnaryTilde)

    def isUnaryPlus(self):
        """
        Returns whether it is a unary plus.
        :return: True if unary plus, otherwise False.
        :rtype: bool
        """
        return self.__isUnaryPlus

    def isUnaryMinus(self):
        """
        Returns whether it is a minus plus.
        :return: True if unary minus, otherwise False.
        :rtype: bool
        """
        return self.__isUnaryMinus

    def isUnaryTilde(self):
        """
        Returns whether it is a tilde plus.
        :return: True if unary tilde, otherwise False.
        :rtype: bool
        """
        return self.__isUnaryTilde

    def print(self):
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
