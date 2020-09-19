# -*- coding: utf-8 -*-
#
# pynestml_2_nest_type_converter.py
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


class PyNestml2NestTypeConverter(object):
    """
    This class contains a single operation as used to convert nestml types to nest centerpieces.
    """

    @classmethod
    def convert(cls, type_symbol):
        # type: (TypeSymbol) -> str
        """
        Converts the name of the type symbol to a corresponding nest representation.
        :param type_symbol: a single type symbol
        :type type_symbol: TypeSymbol
        :return: the corresponding string representation.
        :rtype: str
        """
        assert isinstance(type_symbol, TypeSymbol)

        if type_symbol.is_buffer:
            return 'nest::RingBuffer'

        if isinstance(type_symbol, RealTypeSymbol):
            return 'double'
        elif isinstance(type_symbol, BooleanTypeSymbol):
            return 'bool'
        elif isinstance(type_symbol, IntegerTypeSymbol):
            return 'long'
        elif isinstance(type_symbol, StringTypeSymbol):
            return 'std::string'
        elif isinstance(type_symbol, VoidTypeSymbol):
            return 'void'
        elif isinstance(type_symbol, UnitTypeSymbol):
            return 'double'
        elif isinstance(type_symbol, NESTTimeTypeSymbol):
            return 'nest::Time'
        elif isinstance(type_symbol, ErrorTypeSymbol):
            return 'ERROR'
        else:
            raise Exception('Unknown NEST type')
