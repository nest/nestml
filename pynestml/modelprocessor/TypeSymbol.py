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
from copy import copy

from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.Symbol import Symbol
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
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
        """
        wrapper around isinstance to make things more readable/intuitive.
        instance checks abound for all members of the TypeSymbol hierarchy,
        (specifically the operator functions) though i have tried to
        limit them to situations that would otherwise have been covered
        by function overloading in e.g. Java -ptraeder
        """
        return isinstance(self, _other)

    @abstractmethod
    def __init__(self, _name=None):
        from pynestml.modelprocessor.Symbol import SymbolKind
        super(TypeSymbol, self).__init__(_referenced_object=None, _scope=None,
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

    def __mul__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('*', other)

    def __mod__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('%', other)

    def __truediv__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('/', other)

    def __neg__(self):
        self.unary_operation_not_defined_error('-')

    def __pos__(self):
        self.unary_operation_not_defined_error('+')

    def __invert__(self):
        self.unary_operation_not_defined_error('~')

    def __pow__(self, power, modulo=None):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if isinstance(power, ErrorTypeSymbol):
            return power
        self.binary_operation_not_defined_error('**', power)

    def negate(self):
        self.unary_operation_not_defined_error('not ')

    def __add__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('+', other)

    def __sub__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('-', other)

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

    def differs_only_in_magnitude_or_is_equal_to(self, _otherType=None):
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
        unitA = self.astropy_unit
        unitB = _otherType.astropy_unit
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

    @abstractmethod
    def is_castable_to(self, _other_type):
        """
        Indicates whether typeA can be casted to type b. E.g., in Nest, a unit is always casted down to real, thus
        a unit where unit is expected is allowed.
        :return: True if castable, otherwise False
        :rtype: bool
        """
        pass

    def binary_operation_not_defined_error(self, _operator, _other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        result = ErrorTypeSymbol()
        code, message = Messages.get_binary_operation_not_defined(_lhs=self, _operator=_operator, _rhs=_other)
        Logger.logMessage(_code=code, _message=message, _errorPosition=self.referenced_object.getSourcePosition(),
                          _logLevel=LOGGING_LEVEL.ERROR)
        return result

    def unary_operation_not_defined_error(self, _operator):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        result = ErrorTypeSymbol()
        code, message = Messages.get_unary_operation_not_defined(_operator,
                                                                 self.print_symbol())
        Logger.logMessage(_code=code, _message=message, _errorPosition=self.referenced_object.getSourcePosition(),
                          _logLevel=LOGGING_LEVEL.ERROR)
        return result

    def inverse_of_unit(self, _other):
        """
        :param other: the unit to invert
        :type other: UnitTypeSymbol
        :return: UnitTypeSymbol
        """
        result = PredefinedTypes.getTypeIfExists(1 / _other.astropy_unit)
        return result

    def warn_implicit_cast_from_to(self, _from, _to):
        code, message = Messages.getImplicitCastRhsToLhs(_to.print_symbol(), _from.print_symbol())
        Logger.logMessage(_code=code, _message=message, _errorPosition=self.referenced_object.getSourcePosition(),
                          _logLevel=LOGGING_LEVEL.WARNING)
        return _to
