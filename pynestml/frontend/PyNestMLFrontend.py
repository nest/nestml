#
# PyNestMLFrontend.py
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
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.ModelParserExceptions import InvalidPathException
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.CoCosManager import CoCosManager
from pynestml.codegeneration.NestCodeGenerator import NestCodeGenerator
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


def main(args):
    try:
        FrontendConfiguration.config(args)
    except InvalidPathException:
        print('Not a valid path to model or directory: "%s"!' % FrontendConfiguration.getPath())
        return
    # The handed over parameters seem to be correct, proceed with the main routine
    # initialize the predefined elements
    PredefinedUnits.registerUnits()
    PredefinedTypes.registerTypes()
    PredefinedFunctions.registerPredefinedFunctions()
    PredefinedVariables.registerPredefinedVariables()
    # now proceed to parse all models
    compilation_units = list()
    for file in FrontendConfiguration.getFiles():
        parsed_unit = ModelParser.parse_model(file)
        if parsed_unit is not None:
            compilation_units.append(parsed_unit)
    # generate a list of all neurons
    neurons = list()
    for compilationUnit in compilation_units:
        neurons.extend(compilationUnit.getNeuronList())
    # check if across two files two neurons with same name have been defined
    CoCosManager.checkNotTwoNeuronsAcrossUnits(compilation_units)
    # now exclude those which are broken, i.e. have errors.
    if not FrontendConfiguration.isDev():
        for neuron in neurons:
            if Logger.hasErrors(neuron):
                code, message = Messages.getNeuronContainsErrors(neuron.getName())
                Logger.logMessage(_neuron=neuron, _code=code, _message=message,
                                  _errorPosition=neuron.getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.INFO)
                neurons.remove(neuron)

    if not FrontendConfiguration.isDryRun():
        nest_generator = NestCodeGenerator()
        nest_generator.analyseAndGenerateNeurons(neurons)
        nest_generator.generateNESTModuleCode(neurons)
    else:
        code, message = Messages.getDryRun()
        Logger.logMessage(_neuron=None, _code=code, _message=message, _logLevel=LOGGING_LEVEL.INFO)
    if FrontendConfiguration.storeLog():
        store_log_to_file()
    return


def store_log_to_file():
    with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                               'log')) + '.txt', 'w+') as f:
        f.write(str(Logger.getPrintableFormat()))
    return


if __name__ == '__main__':
    main(sys.argv[1:])
