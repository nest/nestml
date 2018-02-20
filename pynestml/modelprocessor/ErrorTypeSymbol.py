#
# ErrorTypeSymbol.py
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


class ErrorTypeSymbol(TypeSymbol):
    code = None
    message = None

    def isNumeric(self):
        return False

    def print_symbol(self):
        return 'error'

    def isPrimitive(self):
        return False

    def __init__(self, _code, _message):
        super().__init__(name='error')
        self.message = _message

    def _get_concrete_nest_type(self):
        return 'ERROR'

    def __mul__(self, other):
        return copy(self)

    def __mod__(self, other):
        return copy(self)

    def __truediv__(self, other):
        return copy(self)

