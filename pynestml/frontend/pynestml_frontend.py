# -*- coding: utf-8 -*-
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

from typing import Any, Mapping, Optional, Sequence, Union

import os
import sys

from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.codegeneration.codegenerator import CodeGenerator
from pynestml.frontend.frontend_configuration import FrontendConfiguration, InvalidPathException, \
    qualifier_store_log_arg, qualifier_module_name_arg, qualifier_logging_level_arg, \
    qualifier_target_arg, qualifier_target_path_arg, qualifier_input_path_arg, qualifier_suffix_arg, \
    qualifier_dev_arg, qualifier_codegen_opts_arg
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.model_installer import install_nest as nest_installer


def to_nest(input_path: Union[str, Sequence[str]], target_path=None, logging_level='ERROR',
            module_name=None, store_log=False, suffix="", dev=False, codegen_opts: Optional[Mapping[str, Any]]=None):
    '''Translate NESTML files into their equivalent C++ code for the NEST simulator.

    Parameters
    ----------
    input_path : str **or** Sequence[str]
        Path to the NESTML file(s) or to folder(s) containing NESTML files to convert to NEST code.
    target_path : str, optional (default: append "target" to `input_path`)
        Path to the generated C++ code and install files.
    logging_level : str, optional (default: 'ERROR')
        Sets which level of information should be displayed duing code generation (among 'ERROR', 'WARNING', 'INFO', or 'NO').
    module_name : str, optional (default: "nestmlmodule")
        Name of the module, which will be used to import the model in NEST via `nest.Install(module_name)`.
    store_log : bool, optional (default: False)
        Whether the log should be saved to file.
    suffix : str, optional (default: "")
        Suffix which will be appended to the model's name (internal use to avoid naming conflicts with existing NEST models).
    dev : bool, optional (default: False)
        Enable development mode: code generation is attempted even for models that contain errors, and extra information is rendered in the generated code.
    codegen_opts : Optional[Mapping[str, Any]]
        A dictionary containing additional options for the target code generator.
    '''
    # if target_path is not None and not os.path.isabs(target_path):
    #    print('PyNestML: Please provide absolute target path!')
    #    return
    args = list()
    args.append(qualifier_input_path_arg)
    if type(input_path) is str:
        args.append(str(input_path))
    else:
        for s in input_path:
            args.append(s)

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

    if suffix:
        args.append(qualifier_suffix_arg)
        args.append(suffix)

    if dev:
        args.append(qualifier_dev_arg)

    FrontendConfiguration.parse_config(args)

    if codegen_opts:
        FrontendConfiguration.set_codegen_opts(codegen_opts)

    if not process() == 0:
        raise Exception("Error(s) occurred while processing the model")


def install_nest(models_path, nest_path):
    # type: (str,str) -> None
    '''
    This procedure can be used to install generated models into the NEST
    simulator.

    Parameters
    ----------
    models_path : str
        Path to the generated models, which should contain the
        (automatically generated) CMake file.
    nest_path : str
        Path to the NEST installation, which should point to the main directory
        where NEST is installed. This folder contains the bin/, lib(64)/,
        include/, and share/ folders of the NEST install. Most importantly, the
        bin/ folder should contain the "nest-config" script. This path is
        passed through the -Dwith-nest argument of the CMake command during the
        installation of the generated NEST module. The suffix /bin/nest-config
        will be automatically attached to `nest_path`.
    '''
    nest_installer(models_path, nest_path)


def main():
    """
    Entry point for the command-line application.

    Returns
    -------
    The process exit code: 0 for success, > 0 for failure
    """
    try:
        FrontendConfiguration.parse_config(sys.argv[1:])
    except InvalidPathException as e:
        return 1
    # the default Python recursion limit is 1000, which might not be enough in practice when running an AST visitor on a deep tree, e.g. containing an automatically generated expression
    sys.setrecursionlimit(10000)
    # after all argument have been collected, start the actual processing
    return int(process())


def process():
    """
    Returns
    -------
    errors_occurred : bool
        Flag indicating whether errors occurred during processing
    """

    errors_occurred = False

    # init log dir
    create_report_dir()
    # The handed over parameters seem to be correct, proceed with the main routine
    init_predefined()
    # now proceed to parse all models
    compilation_units = list()
    nestml_files = FrontendConfiguration.get_files()
    if not type(nestml_files) is list:
        nestml_files = [nestml_files]
    for nestml_file in nestml_files:
        parsed_unit = ModelParser.parse_model(nestml_file)
        if parsed_unit is not None:
            compilation_units.append(parsed_unit)
    if len(compilation_units) > 0:
        # generate a list of all neurons
        neurons = list()
        for compilationUnit in compilation_units:
            neurons.extend(compilationUnit.get_neuron_list())
        # check if across two files two neurons with same name have been defined
        CoCosManager.check_not_two_neurons_across_units(compilation_units)
        # now exclude those which are broken, i.e. have errors.
        if not FrontendConfiguration.is_dev:
            for neuron in neurons:
                if Logger.has_errors(neuron):
                    code, message = Messages.get_neuron_contains_errors(neuron.get_name())
                    Logger.log_message(node=neuron, code=code, message=message,
                                       error_position=neuron.get_source_position(),
                                       log_level=LoggingLevel.INFO)
                    neurons.remove(neuron)
                    errors_occurred = True
        # perform code generation
        _codeGenerator = CodeGenerator.from_target_name(FrontendConfiguration.get_target(),
                                                        options=FrontendConfiguration.get_codegen_opts())
        _codeGenerator.generate_code(neurons)
        for neuron in neurons:
            if Logger.has_errors(neuron):
                errors_occurred = True
                break
    if FrontendConfiguration.store_log:
        store_log_to_file()
    return errors_occurred


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
