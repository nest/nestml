# -*- coding: utf-8 -*-
#
# ast_clone_test.py
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

from pynestml.meta_model.ast_nestml_compilation_unit import ASTNestMLCompilationUnit
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


class ASTCloneTest(unittest.TestCase):

    @classmethod
    def setUp(cls):
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedFunctions.register_functions()
        PredefinedVariables.register_variables()
        SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
        Logger.init_logger(LoggingLevel.INFO)

    @classmethod
    def _test_single_input_path(cls, input_path):
        print('Start creating AST for ' + input_path + ' ...'),
        input_file = FileStream(input_path)
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
        assert isinstance(ast, ASTNestMLCompilationUnit)

        # now, do the actual test for clone()
        ast_copy = ast.clone()
        assert str(ast) == str(ast_copy)
        ast.get_neuron_list()[0].name = "foo"
        ast_copy.get_neuron_list()[0].name = "bar"
        assert str(ast) != str(ast_copy)
        ast_copy.get_neuron_list()[0].name = "foo"
        assert str(ast) == str(ast_copy)

    @classmethod
    def test(cls):
        input_paths = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "nest_tests", "resources", "iaf_psc_exp_multisynapse.nestml"))),
                       os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "ExpressionCollection.nestml")))]
        for input_path in input_paths:
            cls._test_single_input_path(input_path)


if __name__ == '__main__':
    unittest.main()
