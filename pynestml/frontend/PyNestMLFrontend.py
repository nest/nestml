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

import os
import sys

from pynestml.cocos.CoCosManager import CoCosManager
from pynestml.codegeneration.NestCodeGenerator import NestCodeGenerator
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration, InvalidPathException
from pynestml.symbols.PredefinedFunctions import PredefinedFunctions
from pynestml.symbols.PredefinedTypes import PredefinedTypes
from pynestml.symbols.PredefinedUnits import PredefinedUnits
from pynestml.symbols.PredefinedVariables import PredefinedVariables
from pynestml.utils.Logger import Logger, LoggingLevel
from pynestml.utils.Messages import Messages
from pynestml.utils.ModelParser import ModelParser


def main(args):
    try:
        FrontendConfiguration.config(args)
    except InvalidPathException:
        print('Not a valid path to model or directory: "%s"!' % FrontendConfiguration.get_path())
        return
    # The handed over parameters seem to be correct, proceed with the main routine
    init_predefined()
    # now proceed to parse all models
    compilation_units = list()
    for file in FrontendConfiguration.get_files():
        parsed_unit = ModelParser.parse_model(file)
        if parsed_unit is not None:
            compilation_units.append(parsed_unit)
    # generate a list of all neurons
    neurons = list()
    for compilationUnit in compilation_units:
        neurons.extend(compilationUnit.get_neuron_list())
    # check if across two files two neurons with same name have been defined
    CoCosManager.check_not_two_neurons_across_units(compilation_units)
    # now exclude those which are broken, i.e. have errors.
    if not FrontendConfiguration.is_dev():
        for neuron in neurons:
            if Logger.has_errors(neuron):
                code, message = Messages.get_neuron_contains_errors(neuron.get_name())
                Logger.log_message(neuron=neuron, code=code, message=message,
                                   error_position=neuron.get_source_position(),
                                   log_level=LoggingLevel.INFO)
                neurons.remove(neuron)

    if not FrontendConfiguration.is_dry_run():
        nest_generator = NestCodeGenerator()
        nest_generator.analyseAndGenerateNeurons(neurons)
        nest_generator.generateNESTModuleCode(neurons)
    else:
        code, message = Messages.get_dry_run()
        Logger.log_message(neuron=None, code=code, message=message, log_level=LoggingLevel.INFO)
    if FrontendConfiguration.store_log():
        store_log_to_file()
    return


def init_predefined():
    # initialize the predefined elements
    PredefinedUnits.register_units()
    PredefinedTypes.register_types()
    PredefinedFunctions.register_functions()
    PredefinedVariables.register_variables()


def store_log_to_file():
    with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                               'log')) + '.txt', 'w+') as f:
        f.write(str(Logger.get_json_format()))
    return


if __name__ == '__main__':
    main(sys.argv[1:])
