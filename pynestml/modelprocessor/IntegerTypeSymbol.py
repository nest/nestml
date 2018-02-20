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
        super().__init__(_name='integer')

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
            return copy(other)
        if other.isNumeric():
            return copy(other)
        return self.binary_operation_not_defined_error('*', other)

    def __mod__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol

        if other.is_instance_of(ErrorTypeSymbol):
            return copy(other)
        if other.is_instance_of(IntegerTypeSymbol):
            return copy(other)
        return self.binary_operation_not_defined_error('%', other)

    def __truediv__(self, other):
        from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
        from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol

        if other.is_instance_of(ErrorTypeSymbol):
            return copy(other)
        if other.is_instance_of(UnitTypeSymbol):
            return self.inverse_of_unit(other)
        if other.isNumericPrimitive():
            return copy(other)
        return self.binary_operation_not_defined_error('/', other)

    def __neg__(self):
        return copy(self)

    def __pos__(self):
        return copy(self)

    def __invert__(self):
        return copy(self)
