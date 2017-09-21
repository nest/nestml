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

from __future__ import print_function

import unittest
import os
from antlr4 import *
from pynestml.src.main.grammars.org.PyNESTMLParser import PyNESTMLParser
from pynestml.src.main.grammars.org.PyNESTMLLexer import PyNESTMLLexer
from pynestml.src.main.python.org.nestml.visitor.ASTSymbolTableVisitor import SymbolTableASTVisitor
from pynestml.src.main.python.org.nestml.visitor.ASTBuilderVisitor import ASTBuilderVisitor
from pynestml.src.main.python.org.nestml.symbol_table.SymbolTable import SymbolTable
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedUnits import PredefinedUnits
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedFunctions import PredefinedFunctions
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedVariables import PredefinedVariables
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL


class SymbolTableBuilderTest(unittest.TestCase):
    def test(self):
        PredefinedUnits.registerUnits()
        PredefinedTypes.registerTypes()
        PredefinedFunctions.registerPredefinedFunctions()
        PredefinedVariables.registerPredefinedVariables()
        Logger.initLogger(LOGGING_LEVEL.ERROR)
        for filename in os.listdir(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                 os.path.join('..', '..', '..', '..', 'models')))):
            if filename.endswith(".nestml"):
                inputFile = FileStream(
                    os.path.join(os.path.dirname(__file__), os.path.join(os.path.join('..', '..', '..', '..',
                                                                                      'models'), filename)))
                lexer = PyNESTMLLexer(inputFile)
                # create a token stream
                stream = CommonTokenStream(lexer)
                # parse the file
                parser = PyNESTMLParser(stream)
                # create a new visitor and return the new AST
                astBuilderVisitor = ASTBuilderVisitor()
                ast = astBuilderVisitor.visit(parser.nestmlCompilationUnit())
                # update the corresponding symbol tables
                SymbolTable.initializeSymbolTable(ast.getSourcePosition())
                for neuron in ast.getNeuronList():
                    SymbolTableASTVisitor.updateSymbolTable(neuron)
                    SymbolTable.addNeuronScope(_name=neuron.getName(), _scope=neuron.getScope())
                print(SymbolTable.printSymbolTable())
        return


if __name__ == '__main__':
    unittest.main()
