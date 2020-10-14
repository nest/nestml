# -*- coding: utf-8 -*-
#
# debug_type_converter.py
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
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.boolean_type_symbol import BooleanTypeSymbol
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.string_type_symbol import StringTypeSymbol
from pynestml.symbols.void_type_symbol import VoidTypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.nest_time_type_symbol import NESTTimeTypeSymbol
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.utils.either import Either


class DebugTypeConverter():
    """
    Convert NESTML types to a string format that is suitable for info/warning/error messages.
    """

    @classmethod
    def convert(cls, type_symbol: TypeSymbol) -> str:
        """
        Converts the name of the type symbol to a corresponding string representation.
        :param type_symbol: a single type symbol
        :return: the corresponding string representation.
        """
        if isinstance(type_symbol, Either):
            if type_symbol.is_value():
                return cls.convert(type_symbol.get_value())
            else:
                assert type_symbol.is_error()
                return type_symbol.get_error()

        if 'is_buffer' in dir(type_symbol) and type_symbol.is_buffer:
            return 'buffer'

        if isinstance(type_symbol, RealTypeSymbol):
            return 'real'

        if isinstance(type_symbol, BooleanTypeSymbol):
            return 'bool'

        if isinstance(type_symbol, IntegerTypeSymbol):
            return 'int'

        if isinstance(type_symbol, StringTypeSymbol):
            return 'str'

        if isinstance(type_symbol, VoidTypeSymbol):
            return 'void'

        if isinstance(type_symbol, UnitTypeSymbol):
            return type_symbol.get_value().unit.unit

        if isinstance(type_symbol, NESTTimeTypeSymbol):
            return 'nest::Time'

        if isinstance(type_symbol, ErrorTypeSymbol):
            return '<Error type>'

        return str(type_symbol)
