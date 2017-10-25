#
# SpecialBlockParserBuilderTest.py
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
from pynestml.generated.PyNESTMLLexer import PyNESTMLLexer
from pynestml.generated.PyNESTMLParser import PyNESTMLParser
from pynestml.nestml.ASTBuilderVisitor import ASTBuilderVisitor
from pynestml.nestml.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
from pynestml.nestml.ASTSourcePosition import ASTSourcePosition
from pynestml.nestml.CoCosManager import CoCosManager
from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.PredefinedUnits import PredefinedUnits
from pynestml.nestml.PredefinedVariables import PredefinedVariables
from pynestml.nestml.SymbolTable import SymbolTable
from pynestml.nestml.CommentsInsertionListener import CommentsInsertionListener
from pynestml.utils.Logger import LOGGING_LEVEL, Logger

# setups the infrastructure
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedFunctions.registerPredefinedFunctions()
PredefinedVariables.registerPredefinedVariables()
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
Logger.initLogger(LOGGING_LEVEL.NO)
CoCosManager.initializeCoCosManager()


class SpecialBlockParserBuilderTest(unittest.TestCase):
    """
    This text is used to check the parsing of special blocks, i.e. for and while-blocks, is executed as expected
    and the corresponding AST built correctly.
    """

    def test(self):
        # print('Start special block parsing and AST-building test...'),
        inputFile = FileStream(
            os.path.join(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                                      'BlockTest.nestml')))
        lexer = PyNESTMLLexer(inputFile)
        # create a token stream
        stream = CommonTokenStream(lexer)
        # parse the file
        parser = PyNESTMLParser(stream)
        # print('done')
        # process the comments
        compilationUnit = parser.nestmlCompilationUnit()
        commentsInsertionListener = CommentsInsertionListener(stream.tokens)
        parseTreeWalker = ParseTreeWalker()
        parseTreeWalker.walk(commentsInsertionListener, compilationUnit)

        astBuilderVisitor = ASTBuilderVisitor()
        ast = astBuilderVisitor.visit(compilationUnit)
        # print('done')
        return isinstance(ast, ASTNESTMLCompilationUnit)


if __name__ == '__main__':
    unittest.main()
