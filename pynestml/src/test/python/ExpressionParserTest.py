"""
/*
 *  ExpressionParsingTest.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
 @author kperun
"""

import unittest
from antlr4 import *
import os
from pynestml.src.main.grammars.org.PyNESTMLLexer import PyNESTMLLexer
from pynestml.src.main.grammars.org.PyNESTMLParser import PyNESTMLParser


class ExpressionParsingTest(unittest.TestCase):
    """
    This text is used to check the parsing of the expression sub-language.
    """

    def test(self):
        print('Start Expression Parser Test...'),
        inputFile = FileStream(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                         'ExpressionCollection.nestml'))
        lexer = PyNESTMLLexer(inputFile)
        # create a token stream
        stream = CommonTokenStream(lexer)
        # parse the file
        parser = PyNESTMLParser(stream)
        parser.nestmlCompilationUnit()
        print('done')
        return


if __name__ == '__main__':
    unittest.main()
