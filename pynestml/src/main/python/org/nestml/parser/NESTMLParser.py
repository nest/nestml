"""
@author kperun
TODO header
"""
from pynestml.src.main.python.org.nestml.visitor import ASTBuilderVisitor
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
        return ASTBuilderVisitor.ASTBuilderVisitor().visit(parser.nestmlCompilationUnit())
