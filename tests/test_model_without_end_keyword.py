# -*- coding: utf-8 -*-
#
# test_model_without_end_keyword.py
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
import glob
import os

import pytest
from antlr4 import FileStream, BailErrorStrategy, CommonTokenStream
from antlr4.error.ErrorListener import ConsoleErrorListener
from pynestml.frontend.pynestml_frontend import generate_nest_target

from pynestml.utils.logger import LoggingLevel, Logger

from pynestml.utils.ast_source_location import ASTSourceLocation

from pynestml.symbols.predefined_variables import PredefinedVariables

from pynestml.symbols.predefined_functions import PredefinedFunctions

from pynestml.symbols.predefined_types import PredefinedTypes

from pynestml.symbol_table.symbol_table import SymbolTable

from pynestml.symbols.predefined_units import PredefinedUnits

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.generated.PyNestMLParser import PyNestMLParser
from pynestml.utils.error_listener import NestMLErrorListener
from pynestml.utils.model_parser import ModelParser


class TestModelWithoutEndKeyword:

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedFunctions.register_functions()
        PredefinedVariables.register_variables()
        SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
        Logger.init_logger(LoggingLevel.INFO)

    def test_model_without_end_keyword(self):
        input_paths = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "models", "neurons")))
        for input_file in glob.glob(input_paths + "/*.nestml"):
            # input_file = FileStream(
            #     os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources")),
            #                  "CommentTest.nestml"))
            print(f"Processing file: {input_file}")
            lexer = PyNestMLLexer()
            lexer._errHandler = BailErrorStrategy()
            lexer._errHandler.reset(lexer)
            lexer.inputStream = FileStream(input_file)

            # create a token stream
            stream = CommonTokenStream(lexer)
            stream.fill()

            # parse the file
            parser = PyNestMLParser(stream)
            parser.removeErrorListeners()
            parser.addErrorListener(ConsoleErrorListener())
            parserErrorListener = NestMLErrorListener()
            parser.addErrorListener(parserErrorListener)
            parser._errHandler = BailErrorStrategy()
            parser._errHandler.reset(parser)
            compilation_unit = parser.nestMLCompilationUnit()
            assert compilation_unit is not None

    def test_model_parser_without_end_keyword(self):
        # input_path = str(os.path.join(
        #     os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "models", "neurons")),
        #     "iaf_psc_exp.nestml"))
        input_paths = os.path.join(
            os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "models", "neurons")))
        for input_file in glob.glob(input_paths + "/*.nestml"):
            generate_nest_target(input_path=input_file,
                                 target_path="target",
                                 logging_level="INFO",
                                 suffix="_nestml")
