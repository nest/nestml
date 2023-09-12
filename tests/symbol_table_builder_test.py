# -*- coding: utf-8 -*-
#
# symbol_table_builder_test.py
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

from pynestml.meta_model.ast_nestml_compilation_unit import ASTNestMLCompilationUnit
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.generated.PyNestMLParser import PyNestMLParser
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.visitors.ast_builder_visitor import ASTBuilderVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

# setups the infrastructure
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedFunctions.register_functions()
PredefinedVariables.register_variables()
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
Logger.init_logger(LoggingLevel.INFO)


class SymbolTableBuilderTest(unittest.TestCase):
    def test(self):
        for filename in glob.glob(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "models", "**", "*.nestml")),
                                  recursive=True):
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

            # process the comments
            compilation_unit = parser.nestMLCompilationUnit()

            # create a new visitor and return the new AST
            ast_builder_visitor = ASTBuilderVisitor(stream.tokens)
            ast = ast_builder_visitor.visit(compilation_unit)

            # update the corresponding symbol tables
            SymbolTable.initialize_symbol_table(ast.get_source_position())
            symbol_table_visitor = ASTSymbolTableVisitor()
            for neuron in ast.get_neuron_list():
                neuron.accept(symbol_table_visitor)
                SymbolTable.add_neuron_scope(name=neuron.get_name(), scope=neuron.get_scope())
            self.assertTrue(isinstance(ast, ASTNestMLCompilationUnit))


if __name__ == '__main__':
    unittest.main()
