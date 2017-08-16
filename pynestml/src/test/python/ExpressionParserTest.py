import unittest
import os
import sys
from antlr4 import *
sys.path.append('../../build/src/main/grammars/org')
from PyNESTMLLexer import PyNESTMLLexer
from PyNESTMLParser import PyNESTMLParser


class MyTestCase(unittest.TestCase):
    def test(self):
        print("Start expression parsing..."),
        input = FileStream("../resources/ExpressionCollection.nestml")
        lexer = PyNESTMLLexer(input)
        # create a token stream
        stream = CommonTokenStream(lexer)
        # parse the file
        parser = PyNESTMLParser(stream)
        tree = parser.nestmlCompilationUnit()
        print("done")


if __name__ == '__main__':
    unittest.main()