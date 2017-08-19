"""
@author kperun
TODO header
"""

import unittest
import os
from antlr4 import *
from pynestml.src.main.grammars.org.PyNESTMLLexer import PyNESTMLLexer
from pynestml.src.main.grammars.org.PyNESTMLParser import PyNESTMLParser


class LexerParserTest(unittest.TestCase):
    def test(self):
        for filename in os.listdir(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources'))):
            if filename.endswith(".nestml"):
                inputFile = FileStream(os.path.join(os.path.dirname(__file__), '..', 'resources', filename))
                lexer = PyNESTMLLexer(inputFile)
                # create a token stream
                stream = CommonTokenStream(lexer)
                # parse the file
                PyNESTMLParser(stream)


if __name__ == '__main__':
    unittest.main()
