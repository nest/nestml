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
import platform


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


def install_nest(target_path: str, **path) -> None:
    '''
    This method can be used to build the generated code and install the resulting extension module into NEST.

    Parameters
    ----------
    target_path : str
        Path to the target directory, which should contain the generated code artifacts (target platform code and CMake configuration file).
    nest_path : str
        Path to the NEST installation, which should point to the main directory where NEST is installed. This folder contains the ``bin``, ``lib(64)``, ``include``, and ``share`` folders of the NEST install. The ``bin`` folder should contain the ``nest-config`` script, which is accessed by NESTML to perform the installation. This path is the same as that passed through the ``-Dwith-nest`` argument of the CMake command before building the generated NEST module. The suffix ``bin/nest-config`` will be automatically appended to ``nest_path``.

    install_dir: str
        Path to the install directory, where the generated module library will be created.

    Raises
    ------
    GeneratedCodeBuildException
        If any kind of failure occurs during cmake configuration, build, or install.
    '''
    expected = {"nest_path", "install_path"}
    actual = set(path.keys())
    must_use_diferent_path = False
    if actual == expected:
        nest_installer(target_path, path["nest_path"], path["install_path"])
        must_use_diferent_path = True
    else:
        if "nest_path" in path:
            nest_installer(target_path, path["nest_path"], path["nest_path"])
        else:
            raise ValueError("Path must contain at least\"nest_path\" and \"install_path\" is optional ")
    if must_use_diferent_path:
        system = platform.system()
        lib_key = ""

        if system == "Linux":
            lib_key = "LD_LIBRARY_PATH"
        else:
            lib_key = "DYLD_LIBRARY_PATH"

        update_lib_path(path["install_path"], lib_key)




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


def update_lib_path(path, lib_key):
    shell_script_path = os.path.expanduser("~/.bashrc")
    lines = []

    with open(shell_script_path, "r") as bashrc:
        lines = bashrc.readlines()
    with open(shell_script_path, "w+") as new_bashrc:
        expression = f"export {lib_key}"
        expression_not_found = True
        to_write_back = []
        for line in lines:
            if expression in line:
                split_line = line.split("=")
                paths = split_line[1].split(":")
                paths = [p.strip() for p in paths]
                if path not in paths:
                    new_expression = line + os.pathsep + path
                    to_write_back.append(new_expression)

                expression_not_found = False
            else:
                to_write_back.append(line)
        if expression_not_found:
            line = f"export {lib_key}={path}"
            to_write_back.append(line)
        new_bashrc.writelines(to_write_back)
    if lib_key in os.environ:
        os.environ[lib_key] += os.pathsep + path
    else:
        os.environ[lib_key] = path
