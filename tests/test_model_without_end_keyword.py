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
import os

from antlr4 import FileStream, BailErrorStrategy, CommonTokenStream
from antlr4.error.ErrorListener import ConsoleErrorListener
from pynestml.utils.error_listener import NestMLErrorListener

from pynestml.generated.PyNestMLParser import PyNestMLParser

from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from python_gen.Python3Lexer import Python3Lexer
from python_gen.Python3Parser import Python3Parser


class TestModelWithoutEndKeyword():

    def test_model_without_end_keyword(self):
        input_file = FileStream(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'iaf_psc_exp.nestml'))
        lexer = PyNestMLLexer(input_file)
        lexer._errHandler = BailErrorStrategy()
        lexer._errHandler.reset(lexer)

        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()

        # parse the file
        parser = PyNestMLParser(stream)
        # parser._errHandler = BailErrorStrategy()
        # parser._errHandler.reset(parser)
        parser.removeErrorListeners()
        parser.addErrorListener(ConsoleErrorListener())
        parserErrorListener = NestMLErrorListener()
        parser.addErrorListener(parserErrorListener)
        compilation_unit = parser.nestMLCompilationUnit()
        print(compilation_unit.toStringTree(recog=parser))
        assert compilation_unit is not None

    def test_python_grammar(self):
        input_file = FileStream(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir)),
                         'test.py'))
        lexer = Python3Lexer(input_file)
        lexer._errHandler = BailErrorStrategy()
        lexer._errHandler.reset(lexer)

        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()

        # parse the file
        parser = Python3Parser(stream)
        # parser._errHandler = BailErrorStrategy()
        # parser._errHandler.reset(parser)
        parser.removeErrorListeners()
        parser.addErrorListener(ConsoleErrorListener())
        tree = parser.single_input()
        print(tree.toStringTree(recog=parser))
        assert tree is not None
