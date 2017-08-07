import unittest
import os
import sys
from antlr4 import *
sys.path.append('../../build/src/main/grammars/org')
from PyNESTMLLexer import PyNESTMLLexer
from PyNESTMLParser import PyNESTMLParser


class MyTestCase(unittest.TestCase):
    def test(self):
        for filename in os.listdir('../../models'):
            if filename.endswith(".nestml"):
                print("Start parsing " + filename + " ... ",end=''),
                input = FileStream("../../models/"+filename)
                lexer = PyNESTMLLexer(input)
                # create a token stream
                stream = CommonTokenStream(lexer)
                # parse the file
                parser = PyNESTMLParser(stream)
                tree = parser.nestmlCompilationUnit()
                print("done")


if __name__ == '__main__':
    unittest.main()
