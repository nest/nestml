# -*- coding: utf-8 -*-
#
# comment_test.py
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
import unittest

from antlr4 import *

from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.generated.PyNestMLParser import PyNestMLParser
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.visitors.ast_builder_visitor import ASTBuilderVisitor

# setups the infrastructure
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedFunctions.register_functions()
PredefinedVariables.register_variables()
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
Logger.init_logger(LoggingLevel.ERROR)


class CommentTest(unittest.TestCase):
    def test(self):
        # print('Start creating AST for ' + filename + ' ...'),
        input_file = FileStream(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'CommentTest.nestml'))
        lexer = PyNestMLLexer(input_file)
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNestMLParser(stream)
        # process the comments
        compilation_unit = parser.nestMLCompilationUnit()
        # now build the meta_model
        ast_builder_visitor = ASTBuilderVisitor(stream.tokens)
        ast = ast_builder_visitor.visit(compilation_unit)
        neuron_body_elements = ast.get_neuron_list()[0].get_body().get_body_elements()
        # check if init values comment is correctly detected
        assert (neuron_body_elements[0].get_comment()[0] == 'init_values comment ok')
        # check that all declaration comments are detected
        comments = neuron_body_elements[0].get_declarations()[0].get_comment()
        assert (comments[0] == 'pre comment 1 ok')
        assert (comments[1] == 'pre comment 2 ok')
        assert (comments[2] == 'inline comment ok')
        assert (comments[3] == 'post comment 1 ok')
        assert (comments[4] == 'post comment 2 ok')
        assert ('pre comment not ok' not in comments)
        assert ('post comment not ok' not in comments)
        # check that equation block comment is detected
        self.assertEqual(neuron_body_elements[1].get_comment()[0], 'equations comment ok')
        # check that parameters block comment is detected
        self.assertEqual(neuron_body_elements[2].get_comment()[0], 'parameters comment ok')
        # check that internals block comment is detected
        self.assertEqual(neuron_body_elements[3].get_comment()[0], 'internals comment ok')
        # check that input comment is detected
        self.assertEqual(neuron_body_elements[4].get_comment()[0], 'input comment ok')
        # check that output comment is detected
        self.assertEqual(neuron_body_elements[5].get_comment()[0], 'output comment ok')
        # check that update comment is detected
        self.assertEqual(neuron_body_elements[6].get_comment()[0], 'update comment ok')


if __name__ == '__main__':
    unittest.main()
