"""
@author kperun
TODO header
"""


class ASTArithmeticOperator:
    """
    This class is used to store a single arithmetic operator, e.g. +.
    No grammar. This part is defined outside the grammar to make processing and storing of models easier and 
    comprehensible.
    """
    __isTimesOp = False
    __isDivOp = False
    __isModuloOp = False
    __isPlusOp = False
    __isMinusOp = False
    __isPowOp = False

    def __init__(self, _isTimesOp: bool = False, _isDivOp: bool = False, _isModuloOp: bool = False,
                 _isPlusOp: bool = False, _isMinusOp: bool = False, _isPowOp: bool = False):
        """
        Standard constructor.
        :param _isTimesOp: is the times operator.
        :type _isTimesOp: bool
        :param _isDivOp: is div operator.
        :type _isDivOp: bool
        :param _isModuloOp: is the modulo operator.
        :type _isModuloOp: bool
        :param _isPlusOp: is the plus operator.
        :type _isPlusOp: bool
        :param _isMinusOp: is the minus operator.
        :type _isMinusOp: bool
        :param _isPowOp: is a power operator.
        :type _isPowOp: bool
        """
        self.__isTimesOp = _isTimesOp
        self.__isDivOp = _isDivOp
        self.__isModuloOp = _isModuloOp
        self.__isPlusOp = _isPlusOp
        self.__isMinusOp = _isMinusOp
        self.__isPowOp = _isPowOp

    @classmethod
    def makeASTArithmeticOperator(cls, _isTimesOp: bool = False, _isDivOp: bool = False, _isModuloOp: bool = False,
                                  _isPlusOp: bool = False, _isMinusOp: bool = False, _isPowOp: bool = False):
        """
        The factory method of the ASTArithmeticOperator class.
        :param _isTimesOp: is the times operator.
        :type _isTimesOp: bool
        :param _isDivOp: is div operator.
        :type _isDivOp: bool
        :param _isModuloOp: is the modulo operator.
        :type _isModuloOp: bool
        :param _isPlusOp: is the plus operator.
        :type _isPlusOp: bool
        :param _isMinusOp: is the minus operator.
        :type _isMinusOp: bool
        :param _isPowOp: is a power operator.
        :type _isPowOp: bool
        :return: a new ASTArithmeticOperator object.
        :rtype: ASTArithmeticOperator
        """
        return cls(_isTimesOp, _isDivOp, _isModuloOp, _isPlusOp, _isMinusOp, _isPowOp)

    def isTimesOp(self) -> bool:
        """
        Returns whether it is a times operator or not.
        :return: True if times operator, otherwise False.
        :rtype: bool
        """
        return self.__isTimesOp

    def isDivOp(self) -> bool:
        """
        Returns whether it is a div operator or not.
        :return: True if div operator, otherwise False.
        :rtype: bool
        """
        return self.__isDivOp

    def isModuloOp(self) -> bool:
        """
        Returns whether it is a modulo operator or not.
        :return: True if modulo operator, otherwise False.
        :rtype: bool
        """
        return self.__isModuloOp

    def isPlusOp(self) -> bool:
        """
        Returns whether it is a plus operator or not.
        :return: True if plus operator, otherwise False.
        :rtype: bool
        """
        return self.__isPlusOp

    def isMinusOp(self) -> bool:
        """
        Returns whether it is a minus operator or not.
        :return: True if minus operator, otherwise False.
        :rtype: bool
        """
        return self.__isMinusOp

    def isPowOp(self) -> bool:
        """
        Returns whether it is a power operator or not.
        :return: True if power operator, otherwise False.
        :rtype: bool
        """
        return self.__isPowOp

    def print(self) -> str:
        """
        Returns the string representation of the operator.
        :return: the operator as a string.
        :rtype: str
        """
        if self.__isTimesOp:
            return ' * '
        elif self.__isDivOp:
            return ' / '
        elif self.__isModuloOp:
            return ' % '
        elif self.__isPlusOp:
            return ' + '
        elif self.__isMinusOp:
            return ' - '
        elif self.__isPowOp:
            return ' ** '
        else:
            raise Exception("(NESTML) Arithmetic operator not specified.")
