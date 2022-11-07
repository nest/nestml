# -*- coding: utf-8 -*-
#
# cpp_types_printer_test.py
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

import unittest

from astropy import units

from pynestml.codegeneration.printers.cpp_types_printer import CppTypesPrinter
from pynestml.symbols.boolean_type_symbol import BooleanTypeSymbol
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.nest_time_type_symbol import NESTTimeTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.string_type_symbol import StringTypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.void_type_symbol import VoidTypeSymbol
from pynestml.utils.unit_type import UnitType


class CppTypesPrinterTest(unittest.TestCase):
    def setUp(self):
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()

    def test_boolean_type(self):
        bts = BooleanTypeSymbol()
        result = CppTypesPrinter().convert(bts)
        self.assertEqual(result, 'bool')
        return

    def test_real_type(self):
        rts = RealTypeSymbol()
        result = CppTypesPrinter().convert(rts)
        self.assertEqual(result, 'double')

    def test_void_type(self):
        vts = VoidTypeSymbol()
        result = CppTypesPrinter().convert(vts)
        self.assertEqual(result, 'void')

    def test_string_type(self):
        sts = StringTypeSymbol()
        result = CppTypesPrinter().convert(sts)
        self.assertEqual(result, 'std::string')

    def test_integer_type(self):
        its = IntegerTypeSymbol()
        result = CppTypesPrinter().convert(its)
        self.assertEqual(result, 'long')

    def test_unit_type(self):
        ms_unit = UnitType(name=str(units.ms), unit=units.ms)
        uts = UnitTypeSymbol(unit=ms_unit)
        result = CppTypesPrinter().convert(uts)
        self.assertEqual(result, 'double')

    def test_buffer_type(self):
        bts = IntegerTypeSymbol()
        bts.is_buffer = True
        result = CppTypesPrinter().convert(bts)
        self.assertEqual(result, 'nest::RingBuffer')

    def test_time_type(self):
        tts = NESTTimeTypeSymbol()
        result = CppTypesPrinter().convert(tts)
        self.assertEqual(result, 'nest::Time')
