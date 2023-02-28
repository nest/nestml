# -*- coding: utf-8 -*-
#
# lexer_parser_test.py
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
import unittest

from antlr4 import *
from antlr4.error.ErrorStrategy import BailErrorStrategy, DefaultErrorStrategy

from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.generated.PyNestMLParser import PyNestMLParser


class LexerParserTest(unittest.TestCase):
    """
    This test is used to test the parser and lexer for correct functionality.
    """

    def test(self):
        model_files = []
        for dir in ["models",
                    os.path.join("tests", "nest_tests", "resources"),
                    os.path.join("tests", "valid")]:
            model_files += glob.glob(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, dir, "*.nestml"))))

        assert len(model_files) > 0

        for filename in model_files:
            print("Processing " + os.path.basename(filename))
            input_file = FileStream(filename)
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


if __name__ == "__main__":
    unittest.main()
