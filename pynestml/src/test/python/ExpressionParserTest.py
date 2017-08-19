import unittest
from antlr4 import *
import os
from pynestml.src.main.grammars.org.PyNESTMLLexer import PyNESTMLLexer
from pynestml.src.main.grammars.org.PyNESTMLParser import PyNESTMLParser


class ExpressionParsingTest(unittest.TestCase):
    def test(self):
        inputFile = FileStream(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                               'ExpressionCollection.nestml'))
        lexer = PyNESTMLLexer(inputFile)
        # create a token stream
        stream = CommonTokenStream(lexer)
        # parse the file
        parser = PyNESTMLParser(stream)
        tree = parser.nestmlCompilationUnit()

        if __name__ == '__main__':
            unittest.main()
