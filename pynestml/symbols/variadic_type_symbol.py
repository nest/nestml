# -*- coding: utf-8 -*-
#
# variadic_type_symbol.py
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


class VariadicTypeSymbol(TypeSymbol):
    r"""Variadic type symbol for a variadic parameters list (variable-length list of parameters)."""

    def __init__(self):
        super(VariadicTypeSymbol, self).__init__(name='__variadic__')

    def is_numeric(self):
        return False

    def is_primitive(self):
        return False

    def print_nestml_type(self):
        return '<variadic>'

    def is_castable_to(self, _other_type):
        return False

    def __eq__(self, other):
        if isinstance(other, VariadicTypeSymbol):
            return True

        return False
