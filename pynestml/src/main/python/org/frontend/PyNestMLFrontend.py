"""
/*
 *  NestmlFrontend.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
@author kperun
"""
import os, sys
import argparse  # used for parsing of input arguments
from pynestml.src.main.python.org.nestml.parser.NESTMLParser import NESTMLParser
from pynestml.src.main.python.org.nestml.parser.NESTMParserExceptions import InvalidPathException


def main(args):
    parser = argparse.ArgumentParser(
        description='NESTML is a domain specific language that supports the specification of neuron models in a precise'
                    'and concise syntax, based on the syntax of Python. Model equations can either be given as a simple'
                    ' string of mathematical notation or as an algorithm written in the built-in procedural language.'
                    ' The equations are analyzed by NESTML to compute an exact solution'
                    ' if possible or use an appropriate numeric solver otherwise.')
    parser.add_argument('-path', type=str, nargs='+',
                        help='Path to a single file or a directory containing the source models.')
    parser.add_argument('-target', metavar='Target', type=str, nargs='?',
                        help='Path to a target directory where models should be generated to.')
    # now parse the handed over args
    parsed_args = parser.parse_args(args)

    if parsed_args.path is None:
        # check if the mandatory path arg has been handed over, just terminate
        raise InvalidPathException('(NESTML) No path to source model/s provided. See -h for more details.')

    # now first check if it is a single file or a dir
    if os.path.isfile(parsed_args.path[0]):
        NESTMLParser.parseModel(parsed_args.path[0])
    elif os.path.isdir(parsed_args.path[0]):
        for filename in os.listdir(parsed_args.path[0]):
            print(filename)
            if filename.endswith(".nestml"):
                NESTMLParser.parseModel(parsed_args.path[0] + filename)
    else:
        raise InvalidPathException('(NESTML) Provided path is invalid. See -h for more details.')


if __name__ == '__main__':
    main(sys.argv[1:])
