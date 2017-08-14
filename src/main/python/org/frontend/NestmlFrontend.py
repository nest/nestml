"""
@author kperun
TODO header
"""
import sys
import os

sys.path.append('../nestml/_parser/')

import argparse
from NESTMLParser import NESTMLParser
from NESTMParserExceptions import InvalidPathException


def main(args):
    parser = argparse.ArgumentParser(
        description='NESTML is a domain specific language that supports the specification of neuron models in a precise'
                    ' and concise syntax, based on the syntax of Python. Model equations can either be given as a simple'
                    ' string of mathematical notation or as an algorithm written in the built-in procedural language.'
                    ' The equations are analyzed by NESTML to compute an exact solution'
                    ' if possible or use an appropriate numeric solver otherwise.')
    parser.add_argument('-path', type=str, nargs='+',
                        help='Path to a single file or a directory containing the source models.')
    parser.add_argument('-target', metavar='Target', type=str, nargs='?',
                        help='Path to a target directory where models should be generated to.')
    # now parse the handed over args
    parsed_args = parser.parse_args(args)
    # now first check if it is a single file or a dir
    if os.path.isfile(parsed_args.path[0]):
        NESTMLParser.parseModel(parsed_args.path[0])
    elif os.path.isdir(parsed_args.path[0]):
        for filename in os.listdir(parsed_args.path[0]):
            if filename.endswith(".nestml"):
                NESTMLParser.parseModel(filename)
    else:
        raise InvalidPathException()


if __name__ == '__main__':
    main(sys.argv[1:])
