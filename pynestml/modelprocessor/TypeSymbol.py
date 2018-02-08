#
# TypeSymbol.py
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
from pynestml.modelprocessor.Symbol import Symbol


class TypeSymbol(Symbol):
    """
    This class is used to represent a single type symbol which represents the type of a element, e.g., a variable.
    
        Attributes:
        __unit              Stores an optional unit used to represent the type of this type symbol.
        __isInteger         Indicates whether it is an integer typed type symbol.
        __isReal            Indicates whether it is a real typed type symbol.
        __isVoid            Indicates whether it is a void typed type symbol.
        __isBoolean         Indicates whether it is a boolean typed type symbol.
        __isString          Indicates whether it is a string typed type symbol.
        __isBuffer          Indicates whether it is a buffer symbol.
    
    """
    __unit = None
    __isInteger = False
    __isReal = False
    __isVoid = False
    __isBoolean = False
    __isString = False
    is_buffer = False

    def __init__(self, _elementReference=None, _scope=None, _name=None,
                 _unit=None, _isInteger=False, _isReal=False, _isVoid=False,
                 _isBoolean=False, _isString=False, _isBuffer=False):
        """
        Standard constructor.
        :param _elementReference: a reference to the first element where this type has been used/defined
        :type _elementReference: Object (or None, if predefined)
        :param _name: the name of the type symbol
        :type _name: str
        :param _scope: the scope in which this type is defined in 
        :type _scope: Scope
        :param _unit: a unit object.
        :type _unit: UnitType
        :param _isInteger: indicates whether this is an integer symbol type.
        :type _isInteger: bool
        :param _isReal: indicates whether this is a  real symbol type.
        :type _isReal: bool
        :param _isVoid: indicates whether this is a void symbol type.
        :type _isVoid: bool
        :param _isBoolean: indicates whether this is a boolean symbol type.
        :type _isBoolean: bool
        :param _isString: indicates whether this is a string symbol type.
        :type _isString: bool
        :param _isBuffer: indicates whether this symbol represents a buffer of a certain type, e.g. integer.
        """
        from pynestml.modelprocessor.UnitType import UnitType
        from pynestml.modelprocessor.Symbol import SymbolKind
        assert (_unit is None or isinstance(_unit, UnitType)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of unit provided (%s)!' % type(_unit)
        assert (isinstance(_isInteger, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-integer provided (%s)!' % type(_isInteger)
        assert (isinstance(_isReal, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-real provided (%s)!' % type(_isReal)
        assert (isinstance(_isVoid, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-void provided (%s)!' % type(_isVoid)
        assert (isinstance(_isBoolean, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-boolean provided (%s)!' % type(_isBoolean)
        assert (isinstance(_isString, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-string provided (%s)!' % type(_isString)
        assert (isinstance(_isBuffer, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-buffer provided (%s)!' % type(_isBuffer)
        assert (_unit is not None or _isInteger or _isReal or _isVoid or _isBoolean or _isString), \
            '(PyNestML.SymbolTable.TypeSymbol) Type of symbol not specified!'
        assert (_isInteger + _isReal + _isVoid + _isBoolean + _isString + (_unit is not None) == 1), \
            '(PyNestML.SymbolTable.TypeSymbol) Type of symbol over-specified!'
        super(TypeSymbol, self).__init__(_elementReference=_elementReference, _scope=_scope,
                                         _name=_name, _symbolKind=SymbolKind.TYPE)
        self.__unit = _unit
        self.__isInteger = _isInteger
        self.__isReal = _isReal
        self.__isVoid = _isVoid
        self.__isBoolean = _isBoolean
        self.__isString = _isString
        self.is_buffer = _isBuffer
        return

    def printSymbol(self):
        """
        Returns a string representation of this symbol.
        :return: a string representation.
        :rtype: str
        """
        if self.isInteger():
            elemType = 'integer'
        elif self.isReal():
            elemType = 'real'
        elif self.isVoid():
            elemType = 'void'
        elif self.isBoolean():
            elemType = 'boolean'
        elif self.isString():
            elemType = 'string'
        else:
            elemType = self.getUnit().printUnit()
        if self.is_buffer:
            elemType += ' buffer'
        return elemType

    def getUnit(self):
        """
        Returns the unit of this type symbol
        :return: a single unit object.
        :rtype: UnitType
        """
        return self.__unit

    def isUnit(self):
        """
        Returns whether this type symbol's type is represented by a unit. 
        :return: True if unit, False otherwise.
        :rtype: bool
        """
        from pynestml.modelprocessor.UnitType import UnitType
        return self.__unit is not None and isinstance(self.__unit, UnitType)

    def getEncapsulatedUnit(self):
        """
        Returns the sympy unit as encapsulated in the unit type object.
        :return: a single unit in the used type system: currently AstroPy.Units.
        :rtype: Symbol (AstroPy.Units)
        """
        return self.__unit.getUnit()

    def isPrimitive(self):
        """
        Returns whether this symbol represents a primitive type.
        :return: true if primitive, otherwise false.
        :rtype: bool
        """
        return self.__isString or self.__isBoolean or self.__isVoid or self.__isReal or self.__isInteger

    def isNumeric(self):
        """
        Returns whether this symbol represents a numeric type.
        :return: True if numeric, otherwise False.
        :rtype: bool
        """
        return self.isInteger() or self.isReal() or self.isUnit()

    def isNumericPrimitive(self):
        """
        Returns whether this symbol represents a primitive numeric type, i.e., real or integer.
        :return: True if numeric primitive, otherwise False.
        :rtype: bool
        """
        return self.isInteger() or self.isReal()

    def isInteger(self):
        """
        Indicates whether this is an integer typed symbol.
        :return: True if integer, otherwise False.
        :rtype: bool
        """
        return self.__isInteger

    def isReal(self):
        """
        Indicates whether this is a real typed symbol.
        :return: True if real, otherwise False.
        :rtype: bool
        """
        return self.__isReal

    def isVoid(self):
        """
        Indicates whether this is a real typed symbol.
        :return: True if void, otherwise False.
        :rtype: bool
        """
        return self.__isVoid

    def isBoolean(self):
        """
        Indicates whether this is a boolean typed symbol.
        :return: True if boolean, otherwise False.
        :rtype: bool
        """
        return self.__isBoolean

    def isString(self):
        """
        Indicates whether this is a string typed symbol.
        :return: True if string, otherwise False.
        :rtype: bool
        """
        return self.__isString

    def equals(self, _other=None):
        """
        Checks if the handed over type symbol object is equal to this (value-wise).
        :param _other: a type symbol object.
        :type _other: Symbol or subclass.
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, TypeSymbol):
            return False

        # deferr comparison of units to sympy library
        if self.isUnit() and _other.isUnit():
            selfUnit = self.getEncapsulatedUnit()
            otherUnit = _other.getEncapsulatedUnit()
            return selfUnit == otherUnit

        return self.isInteger() == _other.isInteger() and \
               self.isReal() == _other.isReal() and \
               self.isVoid() == _other.isVoid() and \
               self.isBoolean() == _other.isBoolean() and \
               self.isString() == _other.isString() and \
               self.is_buffer == _other.is_buffer and \
               (self.getUnit().equals(_other.getUnit()) if self.isUnit() and _other.isUnit() else True) and \
               self.getReferencedObject() == _other.getReferencedObject() and \
               self.getSymbolName() == _other.getSymbolName() and \
               self.getCorrespondingScope() == _other.getCorrespondingScope()

    def differsOnlyInMagnitudeOrIsEqualTo(self, _otherType=None):
        """
        Indicates whether both type represent the same unit but with different magnitudes. This
        case is still valid, e.g., mV can be assigned to volt.
        :param _typeA: a type
        :type _typeA:  TypeSymbol
        :param _otherType: a type
        :type _otherType: TypeSymbol
        :return: True if both elements equal or differ in magnitude, otherwise False.
        :rtype: bool
        """
        assert (_otherType is not None and isinstance(_otherType, TypeSymbol)), \
            '(NESTML.TypeSymbol) No or wrong type of target type provided (%s)!' % type(_otherType)

        if self.equals(_otherType):
            return True
        # in the case that we don't deal with units, there are no magnitudes
        if not (self.isUnit() and _otherType.isUnit()):
            return False
        # if it represents the same unit, if we disregard the prefix and simplify it
        unitA = self.getUnit().getUnit()
        unitB = _otherType.getUnit().getUnit()
        # if isinstance(unitA,)
        from astropy import units
        # TODO: consider even more complex cases which can be resolved to the same unit?
        if (isinstance(unitA, units.Unit) or isinstance(unitA, units.PrefixUnit) or isinstance(unitA, units.CompositeUnit))\
                and (isinstance(unitB, units.Unit) or isinstance(unitB, units.PrefixUnit) or isinstance(unitB, units.CompositeUnit)) \
                and unitA.physical_type == unitB.physical_type:
            return True
        return False

    def isCastableTo(self, _otherType=None):
        """
        Indicates whether typeA can be casted to type b. E.g., in Nest, a unit is always casted down to real, thus
        a unit where unit is expected is allowed.
        :return: True if castable, otherwise False
        :rtype: bool
        """
        assert (_otherType is not None and isinstance(_otherType, TypeSymbol)), \
            '(PyNestML.Utils) No or wrong type of target type provided (%s)!' % type(_otherType)
        # we can always cast from unit to real
        if self.isUnit() and _otherType.isReal():
            return True
        elif self.isBoolean() and _otherType.isReal():
            return True
        elif self.isReal() and _otherType.isBoolean():
            return True
        elif self.isInteger() and _otherType.isReal():
            return True
        elif self.isReal() and _otherType.isInteger():
            return True
        else:
            return False
