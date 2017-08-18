import unittest
from antlr4 import *
import os
from pynestml.src.main.grammars.org.PyNESTMLLexer import PyNESTMLLexer
from pynestml.src.main.grammars.org.PyNESTMLParser import PyNESTMLParser


class MyTestCase(unittest.TestCase):
    def test(self):
        print("Start expression parsing..."),
        inputFile = FileStream(os.path.join('..', 'resources', 'ExpressionCollection.nestml'))
        lexer = PyNESTMLLexer(inputFile)
        # create a token stream
        stream = CommonTokenStream(lexer)
        # parse the file
        parser = PyNESTMLParser(stream)
        tree = parser.nestmlCompilationUnit()
        print("done")


if __name__ == '__main__':
    unittest.main()
