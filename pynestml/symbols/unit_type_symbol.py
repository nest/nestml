# -*- coding: utf-8 -*-
#
# unit_type_symbol.py
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

from pynestml.symbols.type_symbol import TypeSymbol
from pynestml.utils.unit_type import UnitType


class UnitTypeSymbol(TypeSymbol):
    r"""
    Type symbol for a physical type.

    The type of a physical quantity is determined only by its dimension: two unit type symbols are equal if and only if their units are dimensionally equivalent. For example, ``mV`` and ``V`` (and the quantity ``"voltage"``) are all the same type, whereas ``mV`` and ``pA`` are not. The magnitude of a unit (the factor 1E-3 in ``mV``) is not part of the type; it belongs to the value of a literal such as ``-70 mV``.
    """

    @property
    def astropy_unit(self):
        return self.unit.get_unit()

    def is_numeric(self):
        return True

    def is_primitive(self):
        return False

    def __init__(self, unit):
        assert isinstance(unit, UnitType)
        self.unit = unit
        super(UnitTypeSymbol, self).__init__(name=unit.name)

    def print_nestml_type(self):
        return self.unit.print_unit()

    def equals(self, other=None):
        basic_equals = super(UnitTypeSymbol, self).equals(other)
        if basic_equals is True:
            return self.is_dimensionally_equivalent_to(other)

        return False

    def is_dimensionally_equivalent_to(self, other: "UnitTypeSymbol") -> bool:
        r"""
        Returns True if and only if both units have the same physical dimension, irrespective of their magnitude.
        """
        try:
            return self.astropy_unit.is_equivalent(other.astropy_unit)
        except BaseException:
            return False

    def __mul__(self, other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(UnitTypeSymbol):
            return self.multiply_by(other)
        if other.is_numeric_primitive():
            return self
        return self.binary_operation_not_defined_error("*", other)

    def multiply_by(self, other):
        from pynestml.symbols.predefined_types import PredefinedTypes
        return PredefinedTypes.get_type(self.astropy_unit * other.astropy_unit)

    def __truediv__(self, other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(UnitTypeSymbol):
            return self.divide_by(other)
        if other.is_numeric_primitive():
            return self
        return self.binary_operation_not_defined_error("/", other)

    def __div__(self, other):
        return self.__truediv__(other)

    def divide_by(self, other):
        from pynestml.symbols.predefined_types import PredefinedTypes
        return PredefinedTypes.get_type(self.astropy_unit / other.astropy_unit)

    def __neg__(self):
        return self

    def __pos__(self):
        return self

    def __invert__(self):
        return self.unary_operation_not_defined_error("~")

    def __pow__(self, power, modulo=None):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if isinstance(power, ErrorTypeSymbol):
            return power
        if isinstance(power, int) \
                or isinstance(power, float):
            return self.to_the_power_of(power)
        return self.binary_operation_not_defined_error("**", power)

    def to_the_power_of(self, power):
        from pynestml.symbols.predefined_types import PredefinedTypes
        return PredefinedTypes.get_type(self.astropy_unit ** power)

    def __add__(self, other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        from pynestml.symbols.string_type_symbol import StringTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(StringTypeSymbol):
            return other
        if other.is_numeric_primitive():
            return self.warn_implicit_cast_from_to(other, self)
        if other.is_instance_of(UnitTypeSymbol):
            return self.add_or_sub_another_unit(other)
        return self.binary_operation_not_defined_error("+", other)

    def __sub__(self, other):
        from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_numeric_primitive():
            return self.warn_implicit_cast_from_to(other, self)
        if other.is_instance_of(UnitTypeSymbol):
            return self.add_or_sub_another_unit(other)
        return self.binary_operation_not_defined_error("-", other)

    def add_or_sub_another_unit(self, other):
        if self.is_dimensionally_equivalent_to(other):
            return self

        return self.binary_operation_not_defined_error("+/-", other)

    def is_castable_to(self, _other_type):
        if super(UnitTypeSymbol, self).is_castable_to(_other_type):
            return True
        from pynestml.symbols.real_type_symbol import RealTypeSymbol
        if _other_type.is_instance_of(RealTypeSymbol):
            # anything can be cast to a real
            return True

        if _other_type.is_instance_of(UnitTypeSymbol):
            return self.is_dimensionally_equivalent_to(_other_type)

        return False
