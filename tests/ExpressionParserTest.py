#
# ExpressionParsingTest.py
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

from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.generated.PyNestMLParser import PyNestMLParser
from pynestml.modelprocessor.ASTBuilderVisitor import ASTBuilderVisitor
from pynestml.modelprocessor.ASTNestMLCompilationUnit import ASTNestMLCompilationUnit
from pynestml.modelprocessor.ASTSourceLocation import ASTSourceLocation
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.utils.Logger import LoggingLevel, Logger

# setups the infrastructure
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedFunctions.register_predefined_functions()
PredefinedVariables.register_predefined_variables()
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
Logger.init_logger(LoggingLevel.NO)


class ExpressionParsingTest(unittest.TestCase):
    """
    This text is used to check the parsing of the rhs sub-language.
    """

    def test(self):
        # print('Start Expression Parser Test...'),
        input_file = FileStream(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'ExpressionCollection.nestml'))
        lexer = PyNestMLLexer(input_file)
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNestMLParser(stream)
        compilation_unit = parser.nestMLCompilationUnit()
        # print('done')
        ast_builder_visitor = ASTBuilderVisitor(stream.tokens)
        ast = ast_builder_visitor.visit(compilation_unit)
        # print('done')
        assert isinstance(ast, ASTNestMLCompilationUnit)


if __name__ == '__main__':
    unittest.main()
