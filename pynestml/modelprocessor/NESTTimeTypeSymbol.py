#
# NESTTimeTypeSymbol.py
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
from pynestml.modelprocessor.TypeSymbol import TypeSymbol


class NESTTimeTypeSymbol(TypeSymbol):
    def isNumeric(self):
        return False

    def isPrimitive(self):
        return False

    def __init__(self, _name=None):
        super().__init__(_name='time')

    def print_symbol(self):
        result = 'time'
        if self.is_buffer:
            result += ' buffer'
        return result

    def _get_concrete_nest_type(self):
        return 'nest::Time'

    def __mul__(self, other):
        return self.operation_not_defined_error('*', other)

    def __mod__(self, other):
        return self.operation_not_defined_error('%', other)

    def __truediv__(self, other):
        return self.operation_not_defined_error('/', other)

