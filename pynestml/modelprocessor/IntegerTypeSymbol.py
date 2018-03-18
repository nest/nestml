#
# IntegerTypeSymbol.py
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
from copy import copy

from pynestml.modelprocessor.TypeSymbol import TypeSymbol


class IntegerTypeSymbol(TypeSymbol):
    def isNumeric(self):
        return True

    def isPrimitive(self):
        return True

    def __init__(self):
        super(IntegerTypeSymbol, self).__init__(_name='integer')

    def print_symbol(self):
        result = 'integer'
        if self.is_buffer:
            result += ' buffer'
        return result

    def _get_concrete_nest_type(self):
        return 'long'

    def __mul__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol

        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.isNumeric():
            return other
        return self.binary_operation_not_defined_error('*', other)

    def __mod__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol

        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(IntegerTypeSymbol):
            return other
        return self.binary_operation_not_defined_error('%', other)

    def __truediv__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol

        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(UnitTypeSymbol):
            return self.inverse_of_unit(other)
        if other.isNumericPrimitive():
            return other
        return self.binary_operation_not_defined_error('/', other)

    def __neg__(self):
        return self

    def __pos__(self):
        return self

    def __invert__(self):
        return self

    def __pow__(self, power, modulo=None):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        from pynestml.modelprocessor.RealTypeSymbol import RealTypeSymbol

        if power.is_instance_of(ErrorTypeSymbol):
            return power
        if power.is_instance_of(IntegerTypeSymbol):
            return self
        if power.is_instance_of(RealTypeSymbol):
            return power
        return self.binary_operation_not_defined_error('**', power)

    def __add__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        from pynestml.modelprocessor.StringTypeSymbol import StringTypeSymbol
        from pynestml.modelprocessor.RealTypeSymbol import RealTypeSymbol
        from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(StringTypeSymbol):
            return other
        if other.is_instance_of(IntegerTypeSymbol):
            return other
        if other.is_instance_of(RealTypeSymbol):
            return other
        if other.is_instance_of(UnitTypeSymbol):
            return self.warn_implicit_cast_from_to(other, self)
        return self.binary_operation_not_defined_error('+', other)

    def __sub__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        from pynestml.modelprocessor.RealTypeSymbol import RealTypeSymbol
        from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol
        if other.is_instance_of(ErrorTypeSymbol):
            return other
        if other.is_instance_of(IntegerTypeSymbol):
            return other
        if other.is_instance_of(RealTypeSymbol):
            return other
        if other.is_instance_of(UnitTypeSymbol):
            return self.warn_implicit_cast_from_to(self, other)
        return self.binary_operation_not_defined_error('-', other)

    def is_castable_to(self, _other_type):
        from pynestml.modelprocessor.RealTypeSymbol import RealTypeSymbol
        if _other_type.is_instance_of(RealTypeSymbol):
            return True
        else:
            return False
