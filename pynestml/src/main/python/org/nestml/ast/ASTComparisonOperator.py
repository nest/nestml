"""
@author kperun
TODO header
"""


class ASTComparisonOperator:
    """
    This class is used to store a single comparison operator.
    Grammar:
        comparisonOperator : (lt='<' | le='<=' | eq='==' | ne='!=' | ne2='<>' | ge='>=' | gt='>');
    """
    __isLt = False
    __isLe = False
    __isEq = False
    __isNe = False
    __isNe2 = False
    __isGe = False
    __isGt = False

    def __init__(self, _isLt=False, _isLe=False, _isEq=False, _isNe=False, _isNe2=False,
                 _isGe=False, _isGt=False):
        """
        Standard constructor.
        :param _isLt: is less than operator.
        :type _isLt: bool
        :param _isLe: is less equal operator.
        :type _isLe: bool
        :param _isEq: is equality operator.
        :type _isEq: bool
        :param _isNe: is not equal operator.
        :type _isNe: bool
        :param _isNe2: is not equal operator (alternative syntax).
        :type _isNe2: bool
        :param _isGe: is greater equal operator.
        :type _isGe: bool
        :param _isGt: is greater than operator.
        :type _isGt: bool
        """
        self.__isGt = _isGt
        self.__isGe = _isGe
        self.__isNe2 = _isNe2
        self.__isNe = _isNe
        self.__isEq = _isEq
        self.__isLe = _isLe
        self.__isLt = _isLt

    @classmethod
    def makeASTComparisonOperator(cls, _isLt=False, _isLe=False, _isEq=False, _isNe=False, _isNe2=False,
                                  _isGe=False, _isGt=False):
        """
        The factory method of the ASTComparisonOperator class.
        :param _isLt: is less than operator.
        :type _isLt: bool
        :param _isLe: is less equal operator.
        :type _isLe: bool
        :param _isEq: is equality operator.
        :type _isEq: bool
        :param _isNe: is not equal operator.
        :type _isNe: bool
        :param _isNe2: is not equal operator (alternative syntax).
        :type _isNe2: bool
        :param _isGe: is greater equal operator.
        :type _isGe: bool
        :param _isGt: is greater than operator.
        :type _isGt: bool
        :return: a new ASTComparisonOperator object.
        :rtype: ASTComparisonOperator
        """
        return cls(_isLt, _isLe, _isEq, _isNe, _isNe2, _isGe, _isGt)

    def isLt(self):
        """
        Returns whether it is the less than operator.
        :return: True if less than operator, otherwise False
        :rtype: bool
        """
        return self.__isLt

    def isLe(self):
        """
        Returns whether it is the less equal operator.
        :return: True if less equal operator, otherwise False
        :rtype: bool
        """
        return self.__isLe

    def isEq(self):
        """
        Returns whether it is the equality operator.
        :return: True if less equality operator, otherwise False
        :rtype: bool
        """
        return self.__isEq

    def isNe(self):
        """
        Returns whether it is the not equal operator.
        :return: True if not equal operator, otherwise False
        :rtype: bool
        """
        return self.__isNe

    def isNe2(self):
        """
        Returns whether it is the not equal operator.
        :return: True if not equal operator, otherwise False
        :rtype: bool
        """
        return self.__isNe2

    def isGe(self):
        """
        Returns whether it is the greater equal operator.
        :return: True if less greater operator, otherwise False
        :rtype: bool
        """
        return self.__isGe

    def isGt(self):
        """
        Returns whether it is the greater than operator.
        :return: True if less greater than, otherwise False
        :rtype: bool
        """
        return self.__isGt

    def printAST(self):
        """
        Returns the string representation of the operator.
        :return: the operator as a string.
        :rtype: str
        """
        if self.__isLt:
            return ' < '
        elif self.__isLe:
            return ' <= '
        elif self.__isEq:
            return ' == '
        elif self.__isNe:
            return ' != '
        elif self.__isNe2:
            return ' <> '
        elif self.__isGe:
            return ' >= '
        elif self.__isGt:
            return ' > '
        else:
            raise Exception("(NESTML) Comparison operator not specified.")
