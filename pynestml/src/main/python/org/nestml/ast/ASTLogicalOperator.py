"""
@author kperun
TODO header
"""


class ASTLogicalOperator:
    """
    This class is used to store a single logical operator.
    Grammar:
        logicalOperator : (logicalAnd='and' | logicalOr='or');
    """
    __isLogicalAnd = False
    __isLogicalOr = False

    def __init__(self, _isLogicalAnd=False, _isLogicalOr=False):
        """
        Standard constructor.
        :param _isLogicalAnd: is logical and.
        :type _isLogicalAnd: bool
        :param _isLogicalOr: is logical or.
        :type _isLogicalOr: bool
        """
        assert _isLogicalAnd ^ _isLogicalOr, "(NESTML) Only one operator allowed."
        self.__isLogicalAnd = _isLogicalAnd
        self.__isLogicalOr = _isLogicalOr

    @classmethod
    def makeASTLogicalOperator(cls, _isLogicalAnd=False, _isLogicalOr=False):
        """
        The factory method of the ASTLogicalOperator class.
        :param _isLogicalAnd: is logical and.
        :type _isLogicalAnd: bool
        :param _isLogicalOr: is logical or.
        :type _isLogicalOr: bool
        :return: a new ASTLogicalOperator object.
        :rtype: ASTLogicalOperator
        """
        return cls(_isLogicalAnd, _isLogicalOr)

    def isAnd(self):
        """
        Returns whether it is an AND operator.
        :return: True if AND, otherwise False.
        :rtype: bool
        """
        return self.__isLogicalAnd

    def isOr(self):
        """
        Returns whether it is an OR operator.
        :return: True if OR, otherwise False.
        :rtype: bool
        """
        return self.__isLogicalOr

    def print(self):
        """
        Returns a string representing the operator.
        :return: a string representing the operator
        :rtype: str
        """
        if self.__isLogicalAnd:
            return ' and '
        else:
            return ' or '
