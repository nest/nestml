# -*- coding: utf-8 -*-
#
# spinnaker_types_printer.py
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
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.type_symbol import TypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol


class SpinnakerTypesPrinter(TypesPrinter):
    @classmethod
    def convert(cls, type_symbol: TypeSymbol):
        """
        Converts from NESTML type to SpiNNaker type
        :param type_symbol:
        :return:
        """
        # if type_symbol.is_buffer:
        #     return "nest::RingBuffer"

        if isinstance(type_symbol, RealTypeSymbol):
            return "accum"

        # if isinstance(type_symbol, BooleanTypeSymbol):
        #     return "bool"

        if isinstance(type_symbol, IntegerTypeSymbol):
            return "unsigned int"

        # if isinstance(type_symbol, StringTypeSymbol):
        #     return "std::string"
        #
        # if isinstance(type_symbol, VoidTypeSymbol):
        #     return "void"

        if isinstance(type_symbol, UnitTypeSymbol):
            return "accum"

        # if isinstance(type_symbol, NESTTimeTypeSymbol):
        #     return "nest::Time"

        if isinstance(type_symbol, ErrorTypeSymbol):
            return "ERROR"

        raise Exception("Unknown SpiNNaker type")
