# -*- coding: utf-8 -*-
#
# boolean_type_symbol.py
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


class BooleanTypeSymbol(TypeSymbol):
    def is_numeric(self):
        return False

    def is_primitive(self):
        return True

    def __init__(self):
        super(BooleanTypeSymbol, self).__init__(name='boolean')

    def print_nestml_type(self):
        return 'boolean'

    def negate(self):
        return self

    def __add__(self, other):
        from pynestml.symbols.string_type_symbol import StringTypeSymbol
        if other.is_instance_of(StringTypeSymbol):
            return other
        return self.binary_operation_not_defined_error('+', other)

    def is_castable_to(self, _other_type):
        if super(BooleanTypeSymbol, self).is_castable_to(_other_type):
            return True
        from pynestml.symbols.real_type_symbol import RealTypeSymbol

        if _other_type.is_instance_of(RealTypeSymbol):
            return True
        else:
            return False
