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

    def __init__(self, _isTimesOp=False, _isDivOp=False, _isModuloOp=False, _isPlusOp=False, _isMinusOp=False,
                 _isPowOp=False):
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
    def makeASTArithmeticOperator(cls, _isTimesOp=False, _isDivOp=False, _isModuloOp=False,
                                  _isPlusOp=False, _isMinusOp=False, _isPowOp=False):
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
        assert (_isTimesOp or _isDivOp or _isModuloOp or _isPlusOp or _isMinusOp or _isPowOp), \
            '(PyNESTML.AST) Type of arithmetic operator not specified.'
        return cls(_isTimesOp, _isDivOp, _isModuloOp, _isPlusOp, _isMinusOp, _isPowOp)

    def isTimesOp(self):
        """
        Returns whether it is a times operator or not.
        :return: True if times operator, otherwise False.
        :rtype: bool
        """
        return self.__isTimesOp

    def isDivOp(self):
        """
        Returns whether it is a div operator or not.
        :return: True if div operator, otherwise False.
        :rtype: bool
        """
        return self.__isDivOp

    def isModuloOp(self):
        """
        Returns whether it is a modulo operator or not.
        :return: True if modulo operator, otherwise False.
        :rtype: bool
        """
        return self.__isModuloOp

    def isPlusOp(self):
        """
        Returns whether it is a plus operator or not.
        :return: True if plus operator, otherwise False.
        :rtype: bool
        """
        return self.__isPlusOp

    def isMinusOp(self):
        """
        Returns whether it is a minus operator or not.
        :return: True if minus operator, otherwise False.
        :rtype: bool
        """
        return self.__isMinusOp

    def isPowOp(self):
        """
        Returns whether it is a power operator or not.
        :return: True if power operator, otherwise False.
        :rtype: bool
        """
        return self.__isPowOp

    def printAST(self):
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
