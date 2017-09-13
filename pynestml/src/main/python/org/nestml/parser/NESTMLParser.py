"""
/*
 *  <the_name_of_this_file>
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
from pynestml.src.main.grammars.org.PyNESTMLParser import PyNESTMLParser
from pynestml.src.main.grammars.org.PyNESTMLLexer import PyNESTMLLexer
from antlr4 import *


class NESTMLParser:
    """
    This class contains several method used to parse handed over models and returns them as one or more AST trees.
    """

    @classmethod
    def parseModel(cls, file_path=None):
        """
        Parses a handed over model and returns the ast representation of it.
        :param file_path: the path to the file which shall be parsed.
        :type file_path: str
        :return: a new ASTNESTMLCompilationUnit object.
        :rtype: ASTNESTMLCompilationUnit
        """
        try:
            inputFile = FileStream(file_path)
        except IOError:
            print('(NESTML) File ' + str(file_path) + ' not found. Processing is stopped!')
            return
        # create a lexer and hand over the input
        lexer = PyNESTMLLexer(inputFile)
        # create a token stream
        stream = CommonTokenStream(lexer)
        # parse the file
        parser = PyNESTMLParser(stream)
        # create a new visitor and return the new AST
        astBuilderVisitor = ASTBuilderVisitor.ASTBuilderVisitor()
        ast = astBuilderVisitor.visit(parser.nestmlCompilationUnit())
        return ast
