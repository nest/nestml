#
# SymbolTableBuilderTest.py
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
from pynestml.modelprocessor.ASTBuilderVisitor import ASTBuilderVisitor
from pynestml.modelprocessor.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.ASTSymbolTableVisitor import ASTSymbolTableVisitor
from pynestml.modelprocessor.CoCosManager import CoCosManager
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.utils.Logger import Logger, LOGGING_LEVEL

# setups the infrastructure
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedFunctions.registerPredefinedFunctions()
PredefinedVariables.registerPredefinedVariables()
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
Logger.initLogger(LOGGING_LEVEL.NO)


class SymbolTableBuilderTest(unittest.TestCase):
    def test(self):
        for filename in os.listdir(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                 os.path.join('..', 'models')))):
            if filename.endswith(".nestml"):
                inputFile = FileStream(
                    os.path.join(os.path.dirname(__file__), os.path.join(os.path.join('..', 'models'), filename)))
                lexer = PyNESTMLLexer(inputFile)
                # create a token stream
                stream = CommonTokenStream(lexer)
                stream.fill()
                # parse the file
                parser = PyNESTMLParser(stream)
                # process the comments
                compilationUnit = parser.nestmlCompilationUnit()
                # create a new visitor and return the new AST
                astBuilderVisitor = ASTBuilderVisitor(stream.tokens)
                ast = astBuilderVisitor.visit(compilationUnit)
                # update the corresponding symbol tables
                SymbolTable.initializeSymbolTable(ast.getSourcePosition())
                for neuron in ast.getNeuronList():
                    ASTSymbolTableVisitor.updateSymbolTable(neuron)
                    SymbolTable.addNeuronScope(_name=neuron.getName(), _scope=neuron.getScope())
                assert isinstance(ast, ASTNESTMLCompilationUnit)
        return


if __name__ == '__main__':
    unittest.main()
