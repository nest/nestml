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


import sys, os
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.nestml.NESTMLParser import NESTMLParser
from pynestml.nestml.NESTMLParserExceptions import InvalidPathException
from pynestml.nestml.PredefinedUnits import PredefinedUnits
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
from pynestml.nestml.PredefinedVariables import PredefinedVariables
from pynestml.nestml.CoCosManager import CoCosManager
from pynestml.codegeneration.NestCodeGenerator import NestCodeGenerator
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


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
    neurons = list()
    for compilationUnit in compilationUnits:
        neurons.extend(compilationUnit.getNeuronList())

    if not FrontendConfiguration.isDryRun():
        nestGenerator = NestCodeGenerator()
        nestGenerator.analyseAndGenerateNeurons(neurons)
        nestGenerator.generateNESTModuleCode(neurons)
    else:
        Logger.logMessage('Dry mode selected with -dry parameter, no models generated!', LOGGING_LEVEL.INFO)
    if FrontendConfiguration.storeLog():
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                                   'log')) + '.txt', 'w+') as f:
            f.write(str(Logger.getPrintableFormat()))
    return


if __name__ == '__main__':
    main(sys.argv[1:])
