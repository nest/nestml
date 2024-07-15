# -*- coding: utf-8 -*-
#
# test__cocos.py
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

from __future__ import print_function

import os
import unittest
from pynestml.frontend.frontend_configuration import FrontendConfiguration

from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.model_parser import ModelParser


class CoCosTest(unittest.TestCase):

    def setUp(self):
        Logger.init_logger(LoggingLevel.INFO)
        SymbolTable.initialize_symbol_table(
            ASTSourceLocation(
                start_line=0,
                start_column=0,
                end_line=0,
                end_column=0))
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedVariables.register_variables()
        PredefinedFunctions.register_functions()
        FrontendConfiguration.target_platform = "NEST_COMPARTMENTAL"

    def test_invalid_cm_variables_declared(self):
        model = ModelParser.parse_file(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'invalid')),
                'CoCoCmVariablesDeclared.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(
            model.get_model_list()[0], LoggingLevel.ERROR)), 5)

    def test_valid_cm_variables_declared(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_file(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'valid')),
                'CoCoCmVariablesDeclared.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(
            model.get_model_list()[0], LoggingLevel.ERROR)), 0)

    # it is currently not enforced for the non-cm parameter block, but cm
    # needs that
    def test_invalid_cm_variable_has_rhs(self):
        model = ModelParser.parse_file(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'invalid')),
                'CoCoCmVariableHasRhs.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(
            model.get_model_list()[0], LoggingLevel.ERROR)), 2)

    def test_valid_cm_variable_has_rhs(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_file(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'valid')),
                'CoCoCmVariableHasRhs.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(
            model.get_model_list()[0], LoggingLevel.ERROR)), 0)

    # it is currently not enforced for the non-cm parameter block, but cm
    # needs that
    def test_invalid_cm_v_comp_exists(self):
        model = ModelParser.parse_file(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'invalid')),
                'CoCoCmVcompExists.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(
            model.get_model_list()[0], LoggingLevel.ERROR)), 4)

    def test_valid_cm_v_comp_exists(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_file(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'valid')),
                'CoCoCmVcompExists.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(
            model.get_model_list()[0], LoggingLevel.ERROR)), 0)
