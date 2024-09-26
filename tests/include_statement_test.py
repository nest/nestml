# -*- coding: utf-8 -*-
#
# include_statement_test.py
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
import os

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.FileStream import FileStream
from antlr4.error.ErrorStrategy import BailErrorStrategy

from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.generated.PyNestMLParser import PyNestMLParser


class TestIncludeStatement:
    def test_include_statement(self):
        input = os.path.realpath(os.path.join(os.path.dirname("__file__"), "resources", "IncludeStatementTest.nestml"))

        input_file = FileStream(input)
        lexer = PyNestMLLexer(input_file)
        lexer._errHandler = BailErrorStrategy()
        lexer._errHandler.reset(lexer)
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNestMLParser(stream)
        parser._errHandler = BailErrorStrategy()
        parser._errHandler.reset(parser)
        compilation_unit = parser.nestMLCompilationUnit()
        assert compilation_unit is not None
