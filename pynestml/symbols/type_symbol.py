# -*- coding: utf-8 -*-
#
# type_symbol.py
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

from pynestml.symbols.symbol import Symbol
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class TypeSymbol(Symbol):
    """
    This class is used to represent a single type symbol which represents the type of a element, e.g., a variable.
    Attributes:
        is_buffer          Indicates whether it is a buffer symbol.
    """
    __metaclass__ = ABCMeta

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
    def __init__(self, name):
        from pynestml.symbols.symbol import SymbolKind
        super(TypeSymbol, self).__init__(element_reference=None, scope=None,
                                         name=name, symbol_kind=SymbolKind.TYPE)
        self.is_buffer = False
        return

    @abstractmethod
    def print_nestml_type(self):
        pass

    def print_symbol(self):
        """
        Returns a string representation of this symbol.
        :return: a string representation.
        :rtype: str
        """
        elem_type = self.print_nestml_type()
        if self.is_buffer:
            elem_type += ' buffer'
        return elem_type

    @abstractmethod
    def is_primitive(self):
        """
        Returns whether this symbol represents a primitive type.
        :return: true if primitive, otherwise false.
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_numeric(self):
        """
        Returns whether this symbol represents a numeric type.
        :return: True if numeric, otherwise False.
        :rtype: bool
        """
        # return self.isInteger() or self.isReal() or self.isUnit()
        pass

    def __mul__(self, other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('*', other)

    def __mod__(self, other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('%', other)

    def __truediv__(self, other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('/', other)

    def __div__(self, other):
        return self.__truediv__(other)

    def __neg__(self):
        self.unary_operation_not_defined_error('-')

    def __pos__(self):
        self.unary_operation_not_defined_error('+')

    def __invert__(self):
        self.unary_operation_not_defined_error('~')

    def __pow__(self, power, modulo=None):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if isinstance(power, ErrorTypeSymbol):
            return power
        self.binary_operation_not_defined_error('**', power)

    def negate(self):
        self.unary_operation_not_defined_error('not ')

    def __add__(self, other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('+', other)

    def __sub__(self, other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        self.binary_operation_not_defined_error('-', other)

    def is_numeric_primitive(self):
        """
        Returns whether this symbol represents a primitive numeric type, i.e., real or integer.
        :return: True if numeric primitive, otherwise False.
        :rtype: bool
        """
        return self.is_numeric() and self.is_primitive()

    def equals(self, other):
        """
        Checks if the handed over type symbol object is equal to this (value-wise).
        :param other: a type symbol object.
        :type other: Symbol or subclass.
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if isinstance(other, self.__class__) and isinstance(self, other.__class__):
            return self.is_buffer == other.is_buffer
        return False

    def differs_only_in_magnitude(self, other_type):
        """
        Indicates whether both type represent the same unit but with different magnitudes. This
        case is still valid, e.g., mV can be assigned to volt.
        :param other_type: a type
        :type other_type: TypeSymbol
        :return: True if both elements equal or differ in magnitude, otherwise False.
        :rtype: bool
        """
        if self.equals(other_type):
            return True
        # in the case that we don't deal with units, there are no magnitudes
        from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
        if not (isinstance(self, UnitTypeSymbol) and isinstance(other_type, UnitTypeSymbol)):
            return False
        # if it represents the same unit, if we disregard the prefix and simplify it
        unit_a = self.astropy_unit
        unit_b = other_type.astropy_unit
        # if isinstance(unit_a,)
        from astropy import units
        # TODO: consider even more complex cases which can be resolved to the same unit?
        if (isinstance(unit_a, units.Unit) or isinstance(unit_a, units.PrefixUnit) or isinstance(unit_a, units.CompositeUnit)) \
            and (isinstance(unit_b, units.Unit) or isinstance(unit_b, units.PrefixUnit)
                 or isinstance(unit_b, units.CompositeUnit)) and unit_a.physical_type == unit_b.physical_type:
            return True
        return False

    @abstractmethod
    def is_castable_to(self, _other_type):
        """Test castability of this SymbolType to `_other_type`.

        The implementation of this function in `TypeSymbol` takes care of casting to `TemplateTypeSymbol`s, hence, any children that override this function need to always call the parent implementation, before doing their own castability checks.
        :return: True if castable, otherwise False
        :rtype: bool
        """
        from pynestml.symbols.template_type_symbol import TemplateTypeSymbol
        if isinstance(_other_type, TemplateTypeSymbol):
            return True
        return False

    def binary_operation_not_defined_error(self, _operator, _other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        result = ErrorTypeSymbol()
        code, message = Messages.get_binary_operation_not_defined(
            lhs=self.print_nestml_type(), operator=_operator, rhs=_other.print_nestml_type())
        Logger.log_message(code=code, message=message, error_position=self.referenced_object.get_source_position(),
                           log_level=LoggingLevel.ERROR)
        return result

    def unary_operation_not_defined_error(self, _operator):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        result = ErrorTypeSymbol()
        code, message = Messages.get_unary_operation_not_defined(_operator,
                                                                 self.print_symbol())
        Logger.log_message(code=code, message=message, error_position=self.referenced_object.get_source_position(),
                           log_level=LoggingLevel.ERROR)
        return result

    @classmethod
    def inverse_of_unit(cls, other):
        """
        :param other: the unit to invert
        :type other: UnitTypeSymbol
        :return: UnitTypeSymbol
        """
        from pynestml.symbols.predefined_types import PredefinedTypes
        result = PredefinedTypes.get_type(1 / other.astropy_unit)
        return result

    def warn_implicit_cast_from_to(self, _from, _to):
        code, message = Messages.get_implicit_cast_rhs_to_lhs(_to.print_symbol(), _from.print_symbol())
        Logger.log_message(code=code, message=message,
                           error_position=self.get_referenced_object().get_source_position(),
                           log_level=LoggingLevel.WARNING)
        return _to
