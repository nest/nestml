#
# BooleanTypeSymbol.py
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


class BooleanTypeSymbol(TypeSymbol):
    def isNumeric(self):
        return False

    def isPrimitive(self):
        return True

    def __init__(self):
        super().__init__(_name='boolean')

    def print_symbol(self):
        result = 'boolean'
        if self.is_buffer:
            result += ' buffer'
        return result

    def _get_concrete_nest_type(self):
        return 'bool'

    def negate(self):
        return copy(self)

    def __add__(self, other):
        from pynestml.modelprocessor.StringTypeSymbol import StringTypeSymbol
        if other.is_instance_of(StringTypeSymbol):
            return copy(other)
        return self.binary_operation_not_defined_error('+', other)

    def is_castable_to(self, _other_type):
        from pynestml.modelprocessor.RealTypeSymbol import RealTypeSymbol

        if _other_type.is_instance_of(RealTypeSymbol):
            return True
        else:
            return False
