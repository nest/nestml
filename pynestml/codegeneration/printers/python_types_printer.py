# -*- coding: utf-8 -*-
#
# python_types_printer.py
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

from pynestml.codegeneration.printers.types_printer import TypesPrinter
from pynestml.symbols.type_symbol import TypeSymbol
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.boolean_type_symbol import BooleanTypeSymbol
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.string_type_symbol import StringTypeSymbol
from pynestml.symbols.void_type_symbol import VoidTypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol


class PythonTypesPrinter(TypesPrinter):
    r"""
    Returns a Python syntax version of the handed over type.
    """

    def convert(self, type_symbol: TypeSymbol) -> str:
        r"""
        Converts the name of the type symbol to a corresponding Python syntax representation.
        :param type_symbol: a single type symbol
        :return: the corresponding string representation.
        """
        assert isinstance(type_symbol, TypeSymbol)

        if isinstance(type_symbol, RealTypeSymbol):
            return "float"

        if isinstance(type_symbol, BooleanTypeSymbol):
            return "bool"

        if isinstance(type_symbol, IntegerTypeSymbol):
            return "int"

        if isinstance(type_symbol, StringTypeSymbol):
            return "str"

        if isinstance(type_symbol, VoidTypeSymbol):
            return ""

        if isinstance(type_symbol, UnitTypeSymbol):
            return "float"

        if isinstance(type_symbol, ErrorTypeSymbol):
            return "ERROR"

        raise Exception("Unknown NEST type")
