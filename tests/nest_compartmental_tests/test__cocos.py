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

from typing import Optional

import os
import pytest

from pynestml.meta_model.ast_model import ASTModel
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.model_parser import ModelParser


class TestCoCos:

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
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

    def test_invalid_cm_variables_declared(self):
        model = self._parse_and_validate_model(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'invalid')),
                'CoCoCmVariablesDeclared.nestml'))
        assert len(Logger.get_messages(
            model, LoggingLevel.ERROR)) == 6

    def test_valid_cm_variables_declared(self):
        model = self._parse_and_validate_model(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'valid')),
                'CoCoCmVariablesDeclared.nestml'))
        assert len(Logger.get_messages(
            model, LoggingLevel.ERROR)) == 0

    # it is currently not enforced for the non-cm parameter block, but cm
    # needs that
    def test_invalid_cm_variable_has_rhs(self):
        model = self._parse_and_validate_model(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'invalid')),
                'CoCoCmVariableHasRhs.nestml'))
        assert len(Logger.get_messages(
            model, LoggingLevel.ERROR)) == 2

    def test_valid_cm_variable_has_rhs(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = self._parse_and_validate_model(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'valid')),
                'CoCoCmVariableHasRhs.nestml'))
        assert len(Logger.get_messages(
            model, LoggingLevel.ERROR)) == 0

    # it is currently not enforced for the non-cm parameter block, but cm
    # needs that
    def test_invalid_cm_v_comp_exists(self):
        model = self._parse_and_validate_model(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'invalid')),
                'CoCoCmVcompExists.nestml'))
        assert len(Logger.get_messages(
            model, LoggingLevel.ERROR)) == 4

    def test_valid_cm_v_comp_exists(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = self._parse_and_validate_model(
            os.path.join(
                os.path.realpath(
                    os.path.join(
                        os.path.dirname(__file__), 'resources',
                        'valid')),
                'CoCoCmVcompExists.nestml'))
        assert len(Logger.get_messages(
            model, LoggingLevel.ERROR)) == 0

    def _parse_and_validate_model(self, fname: str) -> Optional[str]:
        from pynestml.frontend.pynestml_frontend import generate_target

        Logger.init_logger(LoggingLevel.DEBUG)

        try:
            generate_target(input_path=fname, target_platform="NONE", logging_level="DEBUG")
        except BaseException:
            return None

        ast_compilation_unit = ModelParser.parse_file(fname)
        if ast_compilation_unit is None or len(ast_compilation_unit.get_model_list()) == 0:
            return None

        model: ASTModel = ast_compilation_unit.get_model_list()[0]
        model_name = model.get_name()

        return model_name
