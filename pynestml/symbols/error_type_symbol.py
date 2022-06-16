# -*- coding: utf-8 -*-
#
# error_type_symbol.py
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


class ErrorTypeSymbol(TypeSymbol):
    """
    Originally intended to only be a 'Null type' for the TypeSymbol hierarchy,
    it is now also a device to communicate errors and warnings back to a place where they can be properly logged
    (we cant do that here because we don't know t he source-position).
    Thought about using Exceptions but that would lead to loads of code duplication in the
    visitors responsible for expression typing.
    In the end a little bit of ugliness here saves us a lot throughout the project -ptraeder

    p.s. could possibly resolve this by associating type-symbol objects with expressions they belong to.
    The field for that is already present from Symbol and we already instantiate types for every expression
    anyways
    """

    def is_numeric(self):
        return False

    def print_nestml_type(self):
        return 'error'

    def is_primitive(self):
        return False

    def __init__(self):
        super(ErrorTypeSymbol, self).__init__(name='error')

    def __mul__(self, other):
        return self

    def __mod__(self, other):
        return self

    def __truediv__(self, other):
        return self

    def __div__(self, other):
        return self

    def __neg__(self):
        return self

    def __pos__(self):
        return self

    def __invert__(self):
        return self

    def __pow__(self, power, modulo=None):
        return self

    def negate(self):
        return self

    def __add__(self, other):
        return self

    def __sub__(self, other):
        return self

    def is_castable_to(self, _other_type):
        return False
