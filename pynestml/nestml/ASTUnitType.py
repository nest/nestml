#
# ASTUnitType.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


from pynestml.nestml.ASTElement import ASTElement


class ASTUnitType(ASTElement):
    """
    This class stores information regarding unit types and their properties.
    ASTUnitType. Represents an unit datatype. It can be a plain datatype as 'mV' or a
    complex data type as 'mV/s'
  
    unitType : leftParentheses='(' unitType rightParentheses=')'
               | base=unitType powOp='**' exponent=INTEGER
               | left=unitType (timesOp='*' | divOp='/') right=unitType
               | unitlessLiteral=INTEGER divOp='/' right=unitType
               | unit=NAME;
    """
    # encapsulated or not
    __hasLeftParentheses = False
    __hasRightParentheses = False
    __compoundUnit = None
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

    def __init__(self, _leftParentheses=False, _compoundUnit=None, _rightParentheses=False, _base=None, _isPow=False,
                 _exponent=None, _lhs=None, _rhs=None, _isDiv=False, _isTimes=False, _unit=None, _sourcePosition=None):
        """
        Standard constructor of ASTUnitType.
        :param _leftParentheses: contains a left parenthesis
        :type _leftParentheses: bool
        :param _compoundUnit: a unit encapsulated in brackets
        :type _compoundUnit: ASTUnitType
        :param _rightParentheses: contains a right parenthesis 
        :type _rightParentheses: bool
        :param _base: the base expression 
        :type _base: ASTUnitType
        :param _isPow: is a power expression
        :type _isPow: bool
        :param _exponent: the exponent expression
        :type _exponent: int
        :param _lhs: the left-hand side expression
        :type _lhs: ASTUnitType or Integer
        :param _rhs: the right-hand side expression
        :type _rhs: ASTUnitType
        :param _isDiv: is a division expression
        :type _isDiv: bool
        :param _isTimes: is a times expression
        :type _isTimes: bool
        :param _unit: is a single unit, e.g. mV
        :type _unit: string
        """
        assert (isinstance(_base, ASTUnitType) or isinstance(_base, str) or _base is None), \
            '(PyNestML.AST.UnitType) Wrong type of base expression provided (%s)!' % type(_base)
        assert (isinstance(_exponent, int) or _exponent is None), \
            '(PyNestML.AST.UnitType) Wrong type of exponent provided, expected integer, provided (%s)!' \
            % type(_exponent)
        assert (isinstance(_lhs, ASTUnitType) or isinstance(_lhs, str) or isinstance(_lhs, int) or _lhs is None), \
            '(PyNestML.AST.UnitType) Wrong type of left-hand side expression provided (%s)!' % type(_lhs)
        assert (isinstance(_rhs, ASTUnitType) or isinstance(_rhs, str) or _rhs is None), \
            '(PyNestML.AST.UnitType) Wrong type of right-hand side expression provided (%s)!' % type(_rhs)
        assert (isinstance(_compoundUnit, ASTUnitType) or isinstance(_compoundUnit, str) or _compoundUnit is None), \
            '(PyNestML.AST.UnitType) Wrong type of encapsulated unit expression provided (%s)!' % type(_compoundUnit)
        assert (_leftParentheses is not None and isinstance(_leftParentheses, bool)), \
            '(PyNestML.AST.UnitType) Wrong type of left-bracket provided (%s)!' % type(_leftParentheses)
        assert (_rightParentheses is not None and isinstance(_rightParentheses, bool)), \
            '(PyNestML.AST.UnitType) Wrong type of right-bracket provided (%s)!' % type(_rightParentheses)
        assert ((_rightParentheses + _leftParentheses) % 2 == 0), \
            '(PyNestML.AST.UnitType) Brackets not consistent!'
        assert (_isTimes is not None and isinstance(_isTimes, bool)), \
            '(PyNestML.AST.UnitType) Wrong type of is-times provided (%s)!' % type(_isTimes)
        assert (_isDiv is not None and isinstance(_isDiv, bool)), \
            '(PyNestML.AST.UnitType) Wrong type of is-div provided (%s)!' % type(_isDiv)
        assert (_isPow is not None and isinstance(_isPow, bool)), \
            '(PyNestML.AST.UnitType) Wrong type of is-pow provided (%s)!' % type(_isPow)
        assert (_unit is None or isinstance(_unit, str)), \
            '(PyNestML.AST.UnitType) Wrong type of unit provided (%s)!' % type(_unit)
        super(ASTUnitType, self).__init__(_sourcePosition)
        self.__hasLeftParentheses = _leftParentheses
        self.__compoundUnit = _compoundUnit
        self.__hasRightParentheses = _rightParentheses
        self.__base = _base
        self.__isPow = _isPow
        self.__exponent = _exponent
        self.__lhs = _lhs
        self.__isTimes = _isTimes
        self.__isDiv = _isDiv
        self.__rhs = _rhs
        self.__unit = _unit
        return

    @classmethod
    def makeASTUnitType(cls, _leftParentheses=False, _compoundUnit=None, _rightParentheses=False, _base=None,
                        _isPow=False, _exponent=None, _lhs=None, _rhs=None, _isDiv=False, _isTimes=False,
                        _unit=None, _sourcePosition=None):
        """
        Factory method used to create new instances of the class.
        :param _leftParentheses: contains a left parenthesis
        :type _leftParentheses: bool
        :param _compoundUnit: a unit encapsulated in brackets
        :type _compoundUnit: ASTUnitType
        :param _rightParentheses: contains a right parenthesis 
        :type _rightParentheses: bool
        :param _base: the base expression 
        :type _base: ASTUnitType
        :param _isPow: is a power expression
        :type _isPow: bool
        :param _exponent: the exponent power, e.g. 2
        :type _exponent: int
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
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return a new ASTUnitType object.
        :rtype ASTUnitType
        """
        return cls(_leftParentheses, _compoundUnit, _rightParentheses, _base, _isPow, _exponent, _lhs, _rhs, _isDiv,
                   _isTimes, _unit, _sourcePosition)

    def isEncapsulated(self):
        """
        Returns whether the expression is encapsulated in parametrises, e.g., (1mV - 0.5mV)
        :return: True if encapsulated, otherwise False. 
        :rtype: bool
        """
        return self.__hasRightParentheses and self.__hasLeftParentheses

    def isPowerExpression(self):
        """
        Returns whether the expression is a combination of a base and exponent, e.g., mV**2
        :return: True if power expression, otherwise False.
        :rtype: bool
        """
        return self.__isPow and self.__base is not None and self.__exponent is not None

    def isSimpleUnit(self):
        """
        Returns whether the expression is a simple unit, e.g., mV.
        :return: True if simple unit, otherwise False.
        :rtype: bool
        """
        return self.__unit is not None

    def isArithmeticExpression(self):
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
        :return: Integer if present, otherwise None.
        :rtype: int
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

    def isDiv(self):
        """
        Returns whether the expression is combined by division operator, e.g., mV/mS.
        :return: True if combined by the division operator, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isDiv, bool) and self.__isDiv

    def isTimes(self):
        """
        Returns whether the expression is combined by times operator, e.g., mV*mS.
        :return: True if combined by the division operator, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isTimes, bool) and self.__isTimes

    def getSimpleUnit(self):
        """
        Returns the simple unit, e.g. mV.
        :return: string if present, otherwise None. 
        :rtype: string
        """
        return self.__unit

    def getCompoundUnit(self):
        """
        Returns the unit encapsulated in brackets, e.g.(10mV)
        :return: a unit object.
        :rtype: ASTUnitType
        """
        return self.__compoundUnit

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.isEncapsulated():
            if self.getCompoundUnit() is _ast:
                return self
            elif self.getCompoundUnit().getParent(_ast) is not None:
                return self.getCompoundUnit().getParent(_ast)

        if self.isPowerExpression():
            if self.getBase() is _ast:
                return self
            elif self.getBase().getParent(_ast) is not None:
                return self.getBase().getParent(_ast)
        if self.isArithmeticExpression():
            if isinstance(self.getLhs(), ASTUnitType):
                if self.getLhs() is _ast:
                    return self
                elif self.getLhs().getParent(_ast) is not None:
                    return self.getLhs().getParent(_ast)
            if self.getRhs() is _ast:
                return self
            elif self.getRhs().getParent(_ast) is not None:
                return self.getRhs().getParent(_ast)
        return None

    def printAST(self):
        """
        Returns a string representation of the unit type.
        :return: a string representation.
        :rtype: str
        """
        if self.isEncapsulated():
            return '(' + self.getCompoundUnit().printAST() + ')'
        elif self.isPowerExpression():
            return self.getBase().printAST() + '**' + str(self.getExponent())
        elif self.isArithmeticExpression():
            tLhs = (self.getLhs().printAST() if isinstance(self.getLhs(), ASTUnitType) else self.getLhs())
            if self.isTimes():
                return str(tLhs) + '*' + self.getRhs().printAST()
            else:
                return str(tLhs) + '/' + self.getRhs().printAST()
        else:
            return self.getSimpleUnit()

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTUnitType):
            return False
        if self.isEncapsulated() + _other.isEncapsulated() == 1:
            return False
        if self.isEncapsulated() and _other.isEncapsulated() and not self.getCompoundUnit().equals(
                _other.getCompoundUnit()):
            return False
        if self.isPowerExpression() + _other.isPowerExpression() == 1:
            return False
        if self.isPowerExpression() and _other.isPowerExpression() and \
                not (self.getBase().equals(_other.getBase()) and self.getExponent() == _other.getExponent()):
            return False
        if self.isArithmeticExpression() + _other.isArithmeticExpression() == 1:
            return False
        if self.isArithmeticExpression() and _other.isArithmeticExpression() and \
                not (self.getLhs().equals(_other.getLhs()) and self.getRhs().equals(_other.getRhs()) and
                             self.isTimes() == _other.isTimes() and self.isDiv() == _other.isDiv()):
            return False
        if self.isSimpleUnit() + _other.isSimpleUnit() == 1:
            return False
        if self.isSimpleUnit() and _other.isSimpleUnit() and not self.getSimpleUnit() == _other.getSimpleUnit():
            return False
        return True
