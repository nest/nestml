"""
@author kperun
TODO header
"""
import sys
sys.path.append('../../../../../build/src/main/grammars/org')
sys.path.append('../_visitor')
print(sys.path)
from antlr4 import *
from PyNESTMLLexer import PyNESTMLLexer
from PyNESTMLParser import PyNESTMLParser
from ASTBuilderVisitor import *


class NESTMLParser:
    """
    This class contains several method used to parse handed over models and returns them as one or more AST trees.
    """

    @classmethod
    def parseModel(cls, file_path: str = None):
        """
        Parses a handed over model and returns the ast representation of it.
        :param file_path: the path to the file which shall be parsed.
        :type file_path: str
        :return: a new ASTNESTMLCompilationUnit object.
        :rtype: ASTNESTMLCompilationUnit
        """
        try:
            input = open(file_path, 'r')
        except IOError:
            print('(NESTML) File ' + str(file_path) + ' not found. Processing is stopped!')
            return
        # create a lexer and hand over the input
        lexer = PyNESTMLLexer(input)
        # create a token stream
        stream = CommonTokenStream(lexer)
        # parse the file
        parser = PyNESTMLParser(stream)
        # create a new visitor and return the new AST
        return ASTBuilderVisitor().visit(parser.nestmlCompilationUnit())
