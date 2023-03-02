# -*- coding: utf-8 -*-
#
# nest_cpp_type_symbol_printer.py
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

from pynestml.codegeneration.printers.cpp_type_symbol_printer import CppTypeSymbolPrinter
from pynestml.symbols.type_symbol import TypeSymbol


class NESTCppTypeSymbolPrinter(CppTypeSymbolPrinter):
    """
    Returns a C++ syntax version of the handed over type.
    """

    def print(self, type_symbol: TypeSymbol) -> str:
        """
        Converts the name of the type symbol to a corresponding nest representation.
        :param type_symbol: a single type symbol
        :return: the corresponding string representation.
        """
        assert isinstance(type_symbol, TypeSymbol)

        if type_symbol.is_buffer:
            return "nest::RingBuffer"

        return super().print(type_symbol)
