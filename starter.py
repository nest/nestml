import sys
from antlr4 import *
sys.path.append('build/src/main/grammars/org')
from PyNESTMLLexer import PyNESTMLLexer
from PyNESTMLParsr import PyNESTMLParser



def main(argv):
    input = FileStream("models/izhikevich.nestml")
    lexer = SimpleExpressionGrammerLexer(input)
    stream = CommonTokenStream(lexer)
    parser = SimpleExpressionGrammerParser(stream)
    tree = parser.astNeuron()
    

if __name__ == '__main__':
    main(sys.argv)
