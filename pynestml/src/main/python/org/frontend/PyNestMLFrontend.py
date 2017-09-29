#
# NestmlFrontend.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


import os, sys
from pynestml.src.main.python.org.nestml.parser.NESTMLParser import NESTMLParser
from pynestml.src.main.python.org.nestml.parser.NESTMLParserExceptions import InvalidPathException
from pynestml.src.main.python.org.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedUnits import PredefinedUnits
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedFunctions import \
    PredefinedFunctions
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedVariables import \
    PredefinedVariables
from pynestml.src.main.python.org.codegeneration.NestCodeGenerator import NestCodeGenerator
from pynestml.src.main.python.org.nestml.cocos.CoCosManager import CoCosManager

def main(args):
    configuration = None
    try:
        FrontendConfiguration.config(args)
    except InvalidPathException:
        print('Invalid path provided (%s)!' % configuration.getPath())
    # The handed over parameters seem to be correct, proceed with the main routine
    # initialize the predefined elements
    PredefinedUnits.registerUnits()
    PredefinedTypes.registerTypes()
    PredefinedFunctions.registerPredefinedFunctions()
    PredefinedVariables.registerPredefinedVariables()
    # now proceed to parse all models
    compilationUnits = list()
    for file in FrontendConfiguration.getFiles():
        parsedUnit = NESTMLParser.parseModel(file)
        if parsedUnit is not None:
            compilationUnits.append(parsedUnit)
    # check if across two files two neurons with same name have been defined
    CoCosManager.checkNotTwoNeuronsAcrossUnits(compilationUnits)
    # and generate them
    if not FrontendConfiguration.isDryRun():
        nestGenerator = NestCodeGenerator()
        for ast in compilationUnits:
            for neuron in ast.getNeuronList():
                # nestGenerator.generateHeader(neuron)
                pass


if __name__ == '__main__':
    main(sys.argv[1:])
