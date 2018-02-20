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
from abc import ABCMeta, abstractmethod

from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.Symbol import Symbol
from pynestml.utils.Messages import Messages


class TypeSymbol(Symbol):
    """
    This class is used to represent a single type symbol which represents the type of a element, e.g., a variable.
    
        Attributes:
        is_buffer          Indicates whether it is a buffer symbol.
    
    """
    __metaclass__ = ABCMeta
    is_buffer = False

    def is_instance_of(self, _other):
        return isinstance(self, _other)

    @abstractmethod
    def __init__(self, _name=None):
        from pynestml.modelprocessor.Symbol import SymbolKind
        super().__init__(_elementReference=None, _scope=None,
                         _name=_name, _symbolKind=SymbolKind.TYPE)
        return

    @property
    def nest_type(self):
        if self.is_buffer:
            return 'nest::RingBuffer'
        else:
            return self._get_concrete_nest_type()

    @abstractmethod
    def _get_concrete_nest_type(self):
        pass

    @abstractmethod
    def print_symbol(self):
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

    @abstractmethod
    def isPrimitive(self):
        """
        Returns whether this symbol represents a primitive type.
        :return: true if primitive, otherwise false.
        :rtype: bool
        """
        pass

    @abstractmethod
    def isNumeric(self):
        """
        Returns whether this symbol represents a numeric type.
        :return: True if numeric, otherwise False.
        :rtype: bool
        """
        # return self.isInteger() or self.isReal() or self.isUnit()
        pass

    @abstractmethod
    def __mul__(self, other):
        pass

    @abstractmethod
    def __truediv__(self, other):
        pass

    @abstractmethod
    def __mod__(self, other):
        pass

    def isNumericPrimitive(self):
        """
        Returns whether this symbol represents a primitive numeric type, i.e., real or integer.
        :return: True if numeric primitive, otherwise False.
        :rtype: bool
        """
        return self.isNumeric() and self.isPrimitive()

    def equals(self, _other=None):
        """
        Checks if the handed over type symbol object is equal to this (value-wise).
        :param _other: a type symbol object.
        :type _other: Symbol or subclass.
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if isinstance(_other, self.__class__) and isinstance(self, _other.__class__):
            return self.is_buffer == _other.is_buffer

        return False

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
        from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol
        if not (isinstance(self, UnitTypeSymbol) and isinstance(_otherType, UnitTypeSymbol)):
            return False
        # if it represents the same unit, if we disregard the prefix and simplify it
        unitA = self.unit.getUnit()
        unitB = _otherType.unit.getUnit()
        # if isinstance(unitA,)
        from astropy import units
        # TODO: consider even more complex cases which can be resolved to the same unit?
        if (isinstance(unitA, units.Unit) or isinstance(unitA, units.PrefixUnit) or isinstance(unitA,
                                                                                               units.CompositeUnit)) \
                and (isinstance(unitB, units.Unit) or isinstance(unitB, units.PrefixUnit) or isinstance(unitB,
                                                                                                        units.CompositeUnit)) \
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
        from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol
        from pynestml.modelprocessor.RealTypeSymbol import RealTypeSymbol
        from pynestml.modelprocessor.BooleanTypeSymbol import BooleanTypeSymbol
        from pynestml.modelprocessor.IntegerTypeSymbol import IntegerTypeSymbol
        if isinstance(self, UnitTypeSymbol) and isinstance(_otherType, RealTypeSymbol):
            return True
        elif isinstance(self, BooleanTypeSymbol) and isinstance(_otherType, RealTypeSymbol):
            return True
        elif isinstance(self, RealTypeSymbol) and isinstance(_otherType, BooleanTypeSymbol):
            return True
        elif isinstance(self, IntegerTypeSymbol) and isinstance(_otherType, RealTypeSymbol):
            return True
        elif isinstance(self, RealTypeSymbol) and isinstance(_otherType, IntegerTypeSymbol):
            return True
        else:
            return False

    def operation_not_defined_error(self, _operator, _other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        code, message = Messages.get_operation_not_defined(self.print_symbol(),
                                                           _operator,
                                                           _other.print_symbol())
        return ErrorTypeSymbol(code, message)

    def inverse_of_unit(self, other):
        """
        :param other: the unit to invert
        :type other: UnitTypeSymbol
        :return: UnitTypeSymbol
        """
        other_unit = other.unit.getUnit()
        return PredefinedTypes.getTypeIfExists(1 / other_unit)
