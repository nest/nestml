#
# pynestml_frontend.py
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

from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.codegeneration.codegenerator import CodeGenerator
from pynestml.frontend.frontend_configuration import FrontendConfiguration, InvalidPathException, \
    qualifier_store_log_arg, qualifier_module_name_arg, qualifier_logging_level_arg, \
    qualifier_target_arg, qualifier_target_path_arg, qualifier_input_path_arg, qualifier_dev_arg, \
    qualifier_suffix
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.model_installer import install_nest as nest_installer


def to_nest(input_path, target_path = None, logging_level = 'ERROR', module_name = None, store_log = False, suffix = "",
            dev = False):
    # if target_path is not None and not os.path.isabs(target_path):
    #    print('PyNestML: Please provide absolute target path!')
    #    return
    args = list()
    args.append(qualifier_input_path_arg)
    args.append(str(input_path))
    if target_path is not None:
        args.append(qualifier_target_path_arg)
        args.append(str(target_path))
    args.append(qualifier_target_arg)
    args.append(str("NEST"))
    args.append(qualifier_logging_level_arg)
    args.append(str(logging_level))
    if module_name is not None:
        args.append(qualifier_module_name_arg)
        args.append(str(module_name))
    if store_log:
        args.append(qualifier_store_log_arg)
    if len(suffix) > 0:
        args.append(qualifier_suffix)
        args.append(suffix)
    if dev:
        args.append(qualifier_dev_arg)
    FrontendConfiguration.parse_config(args)
    process()


def install_nest(models_path, nest_path):
    # type: (str,str) -> None
    """
    This procedure can be used to install generate models into the NEST simulator.
    :param models_path: the path to the generated models, should contain the cmake file (automatically generated).
    :param nest_path: the path to the NEST installation, should point to the dir where nest is installed, a.k.a.
            the -Dwith-nest argument of the make command. The postfix /bin/nest-config is automatically attached.
    :return:
    """
    nest_installer(models_path=models_path, nest_path=nest_path)


def main(args):
    """Returns the process exit code: 0 for success, > 0 for failure"""
    try:
        FrontendConfiguration.parse_config(args)
    except InvalidPathException:
        print('Not a valid path to model or directory: "%s"!' % FrontendConfiguration.get_path())
        return 1
    # after all argument have been collected, start the actual processing
    return process()


def process():
    
    # init log dir
    create_report_dir()
    
    # The handed over parameters seem to be correct, proceed with the main routine
    init_predefined()
    
    # now proceed to parse all models
    compilation_units = list()
    nestml_files = FrontendConfiguration.get_files()
    if not type(nestml_files) is list:
        nestml_files = [nestml_files]

    from pynestml.symbols.predefined_functions import PredefinedFunctions 
    if not "POST_TRACE_FUNCTION" in dir(PredefinedFunctions):
        # register predefined functions that are specific to NEST
        print("XXXXXXXXXXXXXX: iserting get_post_trace predef func")
        params = list()
        PredefinedFunctions.POST_TRACE_FUNCTION = "get_post_trace"
        PredefinedFunctions.register_function(PredefinedFunctions.POST_TRACE_FUNCTION, params=[], return_type=PredefinedTypes.get_real_type(), element_reference=None)


    for nestml_file in nestml_files:
        parsed_unit = ModelParser.parse_model(nestml_file)
        if parsed_unit is not None:
            compilation_units.append(parsed_unit)

    if len(compilation_units) > 0:
        # generate a list of all compilation units (neurons + synapses)
        neurons = list()
        synapses = list()
        for compilationUnit in compilation_units:
            neurons.extend(compilationUnit.get_neuron_list())
            synapses.extend(compilationUnit.get_synapse_list())

            # check if across two files neurons with duplicate names have been defined
            CoCosManager.check_no_duplicate_compilation_unit_names(neurons)

            # check if across two files synapses with duplicate names have been defined
            CoCosManager.check_no_duplicate_compilation_unit_names(synapses)

        # now exclude those which are broken, i.e. have errors.
        if not FrontendConfiguration.is_dev():
            for neuron in neurons:
                if Logger.has_errors(neuron):
                    code, message = Messages.get_neuron_contains_errors(neuron.get_name())
                    Logger.log_message(astnode=neuron, code=code, message=message,
                                       error_position=neuron.get_source_position(),
                                       log_level=LoggingLevel.INFO)
                    neurons.remove(neuron)


            for synapse in synapses:
                if Logger.has_errors(synapse):
                    code, message = Messages.get_synapse_contains_errors(synapse.get_name())
                    Logger.log_message(astnode=synapse, code=code, message=message,
                                       error_position=synapse.get_source_position(),
                                       log_level=LoggingLevel.INFO)
                    synapses.remove(synapse)

        # perform code generation
        _codeGenerator = CodeGenerator(target=FrontendConfiguration.get_target())
        _codeGenerator.generate_code(neurons, synapses)

    if FrontendConfiguration.store_log:
        store_log_to_file()

    return


def init_predefined():
    # initialize the predefined elements
    PredefinedUnits.register_units()
    PredefinedTypes.register_types()
    PredefinedFunctions.register_functions()
    PredefinedVariables.register_variables()


def create_report_dir():
    if not os.path.isdir(os.path.join(FrontendConfiguration.get_target_path(), '..', 'report')):
        os.makedirs(os.path.join(FrontendConfiguration.get_target_path(), '..', 'report'))


def store_log_to_file():
    with open(str(os.path.join(FrontendConfiguration.get_target_path(), '..', 'report',
                               'log')) + '.txt', 'w+') as f:
        f.write(str(Logger.get_json_format()))


if __name__ == '__main__':
    main(sys.argv[1:])
