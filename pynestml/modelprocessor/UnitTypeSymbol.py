#
# UnitTypeSymbol.py
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


class UnitTypeSymbol(TypeSymbol):
    unit = None

    def isNumeric(self):
        return True

    def isPrimitive(self):
        return False

    def __init__(self, _unit):
        self.unit = _unit
        super().__init__(_name=str(_unit.getUnit()))

    def print_symbol(self):
        result = self.unit.printUnit()
        if self.is_buffer:
            result += ' buffer'
        return result

    def _get_concrete_nest_type(self):
        return 'double'

    def equals(self, _other=None):
        basic_equals = super().equals(_other)

        # defer comparison of units to sympy library
        if basic_equals is True:
            self_unit = self.unit.getUnit()
            other_unit = _other.unit.getUnit()
            # TODO: astropy complains this is deprecated
            return self_unit == other_unit

        return False
