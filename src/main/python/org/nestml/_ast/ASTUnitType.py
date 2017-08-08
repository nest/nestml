"""
TODO Header
@author kperun
"""


class ASTUnitType:
    """
    This class stores information regarding unit types and their properties.
    """
    # encapsulated or not
    __hasLeftParentheses = False
    __hasRightParentheses = False
    # pow expression
    __base = None
    __isPow = False
    __exponent = None
    # arithmetic combination case
    __lhs = None
    __isTimes = False
    __isDiv = False
    __rhs = None
    # simple case, just a name
    __unit = None

    def __init__(self, _leftParentheses: bool = False, _rightParentheses: bool = False,
                 _base=None, _isPow: bool = False, _exponent=None, _lhs=None, _rhs=None,
                 _isDiv: bool = False, _isTimes: bool = False, _unit: str = None):
        """
        Standard constructor of ASTUnitType.
        :param _leftParentheses: contains a left parenthesis
        :type _leftParentheses: bool
        :param _rightParentheses: contains a right parenthesis 
        :type _rightParentheses: bool
        :param _base: the base expression 
        :type _base: ASTUnitType
        :param _isPow: is a power expression
        :type _isPow: bool
        :param _exponent: the exponent expression
        :type _exponent: ASTUnitType
        :param _lhs: the left-hand side expression
        :type _lhs: ASTUnitType
        :param _rhs: the right-hand side expression
        :type _rhs: ASTUnitType
        :param _isDiv: is a division expression
        :type _isDiv: bool
        :param _isTimes: is a times expression
        :type _isTimes: bool
        :param _unit: is a single unit, e.g. mV
        :type _unit: string
        """
        # ensure correct typing
        assert (isinstance(_base, ASTUnitType) is True)
        assert (isinstance(_exponent, ASTUnitType) is True)
        assert (isinstance(_lhs, ASTUnitType) is True)
        assert (isinstance(_rhs, ASTUnitType) is True)
        self.__hasLeftParentheses = _leftParentheses
        self.__hasRightParentheses = _rightParentheses
        self.__base = _base
        self.__isPow = _isPow
        self.__exponent = _exponent
        self.__lhs = _lhs
        self.__isTimes = _isTimes
        self.__isDiv = _isDiv
        self.__rhs = _rhs
        self.__unit = _unit

    @classmethod
    def makeASTUnitType(cls, _leftParentheses: bool = False, _rightParentheses: bool = False,
                        _base=None, _isPow: bool = False, _exponent=None, _lhs=None, _rhs=None,
                        _isDiv: bool = False, _isTimes: bool = False, _unit: str = None):
        """
        Factory method used to create new instances of the class.
        :param _leftParentheses: contains a left parenthesis
        :type _leftParentheses: bool
        :param _rightParentheses: contains a right parenthesis 
        :type _rightParentheses: bool
        :param _base: the base expression 
        :type _base: ASTUnitType
        :param _isPow: is a power expression
        :type _isPow: bool
        :param _exponent: the exponent expression
        :type _exponent: ASTUnitType
        :param _lhs: the left-hand side expression
        :type _lhs: ASTUnitType
        :param _rhs: the right-hand side expression
        :type _rhs: ASTUnitType
        :param _isDiv: is a division expression
        :type _isDiv: bool
        :param _isTimes: is a times expression
        :type _isTimes: bool
        :param _unit: is a single unit, e.g. mV
        :type _unit: string
        """
        return cls(_leftParentheses, _rightParentheses, _base, _isPow, _exponent, _lhs, _rhs, _isDiv, _isTimes, _unit)

    def isEncapsulated(self) -> bool:
        """
        Returns whether the expression is encapsulated in parametrises, e.g., (1mV - 0.5mV)
        :return: True if encapsulated, otherwise False. 
        :rtype: bool
        """
        return self.__hasRightParentheses and self.__hasLeftParentheses

    def isPowerExpression(self) -> bool:
        """
        Returns whether the expression is a combination of a base and exponent, e.g., mV**2
        :return: True if power expression, otherwise False.
        :rtype: bool
        """
        return self.__isPow and self.__base is not None and self.__exponent is not None

    def isSimpleUnit(self) -> bool:
        """
        Returns whether the expression is a simple unit, e.g., mV.
        :return: True if simple unit, otherwise False.
        :rtype: bool
        """
        return self.__unit is not None

    def isArithmeticExpression(self) -> bool:
        """
        Returns whether the expression is a arithmetic combination, e.g, mV/mS.
        :return: True if arithmetic expression, otherwise false.
        :rtype: bool
        """
        return self.__lhs is not None and self.__rhs is not None and (self.__isDiv or self.__isTimes)

    def getBase(self):
        """
        Returns the base expression if present.
        :return: ASTUnitType instance if present, otherwise None.
        :rtype: ASTUnitType
        """
        return self.__base

    def getExponent(self):
        """
        Returns the exponent expression if present.
        :return: ASTUnitType instance if present, otherwise None.
        :rtype: ASTUnitType
        """
        return self.__exponent

    def getLhs(self):
        """
        Returns the left-hand side expression if present.
        :return: ASTUnitType instance if present, otherwise None.
        :rtype: ASTUnitType
        """
        return self.__lhs

    def getRhs(self):
        """
        Returns the right-hand side expression if present.
        :return: ASTUnitType instance if present, otherwise None.
        :rtype: ASTUnitType
        """
        return self.__rhs

    def isDiv(self)-> bool:
        """
        Returns whether the expression is combined by division operator, e.g., mV/mS.
        :return: True if combined by the division operator, otherwise False.
        :rtype: bool
        """
        return self.__isDiv

    def isTimes(self)-> bool:
        """
        Returns whether the expression is combined by times operator, e.g., mV*mS.
        :return: True if combined by the division operator, otherwise False.
        :rtype: bool
        """
        return self.__isTimes

    def getSimpleUnit(self) -> str:
        """
        Returns the simple unit, e.g. mV.
        :return: string if present, otherwise None. 
        :rtype: string
        """
        return self.__unit