#
# CommentTest.py
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
Logger.initLogger(LOGGING_LEVEL.ERROR)
CoCosManager.initializeCoCosManager()


class CommentTest(unittest.TestCase):
    def test(self):
        return
        # print('Start creating AST for ' + filename + ' ...'),
        inputFile = FileStream(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'CommentTest.nestml'))
        lexer = PyNESTMLLexer(inputFile)
        # create a token stream
        stream = CommonTokenStream(lexer)
        # parse the file
        parser = PyNESTMLParser(stream)
        # process the comments
        compilationUnit = parser.nestmlCompilationUnit()
        commentsInsertionListener = CommentsInsertionListener(stream.tokens)
        parseTreeWalker = ParseTreeWalker()
        parseTreeWalker.walk(commentsInsertionListener, compilationUnit )
        # now build the ast
        astBuilderVisitor = ASTBuilderVisitor()
        ast = astBuilderVisitor.visit(compilationUnit )
        neuronBodyElements = ast.getNeuronList()[0].getBody().getBodyElements()
        # check if init values comment is correctly detected
        assert (neuronBodyElements[0].getComment() == 'init_values comment ok')
        # check that all declaration comments are detected
        comments = neuronBodyElements[0].getDeclarations()[0].getComment()
        assert (comments[0] == 'pre comment 1 ok')
        assert (comments[1] == 'pre comment 2 ok')
        assert (comments[2] == 'inline comment ok')
        assert (comments[3] == 'post comment 1 ok')
        assert (comments[4] == 'post comment 1 ok')
        assert ('pre comment not ok' not in comments)
        assert ('post comment not ok' not in comments)
        # check that equation block comment is detected
        assert (neuronBodyElements[1].getComment() == 'equations comment ok')
        # check that parameters block comment is detected
        assert (neuronBodyElements[2].getComment() == 'parameters comment ok')
        # check that internals block comment is detected
        assert (neuronBodyElements[3].getComment() == 'internals comment ok')
        # check that intput comment is detected
        assert (neuronBodyElements[4].getComment() == 'input comment ok')
        # check that output comment is detected
        assert (neuronBodyElements[4].getComment() == 'output comment ok')
        # check that update comment is detected
        assert (neuronBodyElements[5].getComment() == 'update comment ok')

if __name__ == '__main__':
    unittest.main()
