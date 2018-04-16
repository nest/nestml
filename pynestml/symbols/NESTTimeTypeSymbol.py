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

from pynestml.symbols.TypeSymbol import TypeSymbol


class NESTTimeTypeSymbol(TypeSymbol):
    def is_numeric(self):
        return False

    def is_primitive(self):
        return False

    def __init__(self, name=None):
        super(NESTTimeTypeSymbol, self).__init__(name='time')

    def print_symbol(self):
        result = 'time'
        if self.is_buffer:
            result += ' buffer'
        return result

    def _get_concrete_nest_type(self):
        return 'nest::Time'

    def __add__(self, other):
        from pynestml.symbols.StringTypeSymbol import StringTypeSymbol
        if other.is_instance_of(StringTypeSymbol):
            return other
        return self.binary_operation_not_defined_error('+', other)

    def is_castable_to(self, _other_type):
        return False
