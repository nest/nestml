import sys
from antlr4 import *

sys.path.append('../../../../build/src/main/grammars/org')
from PyNESTMLLexer import PyNESTMLLexer
from PyNESTMLParser import PyNESTMLParser


def main(argv):
    input = FileStream("models/izhikevich.nestml")
    # inpute the file
    lexer = PyNESTMLLexer(input)
    # create a token stream
    stream = CommonTokenStream(lexer)
    # parse the file
    parser = PyNESTMLParser(stream)
    tree = parser.nestmlCompilationUnit()


if __name__ == '__main__':
    main(sys.argv)
