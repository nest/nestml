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
from pynestml.codegeneration.builder import Builder
from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.exceptions.code_generator_options_exception import CodeGeneratorOptionsException
from pynestml.frontend.frontend_configuration import FrontendConfiguration, InvalidPathException, \
    qualifier_store_log_arg, qualifier_module_name_arg, qualifier_logging_level_arg, \
    qualifier_target_platform_arg, qualifier_target_path_arg, qualifier_input_path_arg, qualifier_suffix_arg, \
    qualifier_dev_arg, qualifier_codegen_opts_arg, qualifier_install_path_arg
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser


def get_known_targets():
    targets = ["NEST", "NEST2", "autodoc", "none"]
    targets = [s.upper() for s in targets]
    return targets


def code_generator_from_target_name(target_name: str, options: Optional[Mapping[str, Any]]=None) -> CodeGenerator:
    """Static factory method that returns a new instance of a child class of CodeGenerator"""
    assert target_name.upper() in get_known_targets(), "Unknown target platform requested: \"" + str(target_name) + "\""

    if target_name.upper() == "NEST":
        from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
        return NESTCodeGenerator(options)

    if target_name.upper() == "NEST2":
        from pynestml.codegeneration.nest2_code_generator import NEST2CodeGenerator
        return NEST2CodeGenerator(options)

    if target_name.upper() == "AUTODOC":
        from pynestml.codegeneration.autodoc_code_generator import AutoDocCodeGenerator
        assert options is None or options == {}, "\"autodoc\" code generator does not support options"
        return AutoDocCodeGenerator()

    if target_name.upper() == "NONE":
        # dummy/null target: user requested to not generate any code
        code, message = Messages.get_no_code_generated()
        Logger.log_message(None, code, message, None, LoggingLevel.INFO)
        return CodeGenerator("", options)

    assert "Unknown code generator requested: " + target_name  # cannot reach here due to earlier assert -- silence static checker warnings


def builder_from_target_name(target_name: str, options: Optional[Mapping[str, Any]]=None) -> Builder:
    r"""Static factory method that returns a new instance of a child class of Builder"""
    from pynestml.frontend.pynestml_frontend import get_known_targets

    assert target_name.upper() in get_known_targets(), "Unknown target platform requested: \"" + str(target_name) + "\""

    if target_name.upper() in ["NEST", "NEST2"]:
        from pynestml.codegeneration.nest_builder import NESTBuilder
        return NESTBuilder(options)

    return None   # no builder requested or available


def generate_target(input_path: Union[str, Sequence[str]], target_platform: str, target_path=None,
                    install_path: str=None, logging_level="ERROR", module_name=None, store_log=False, suffix="",
                    dev=False, codegen_opts: Optional[Mapping[str, Any]]=None):
    r"""Generate and build code for the given target platform.

    Parameters
    ----------
    input_path : str **or** Sequence[str]
        One or more input path(s). Each path is a NESTML file, or a directory containing NESTML files. Directories will be searched recursively for files matching ``*.nestml``.
    target_platform : str
        The name of the target platform to generate code for.
    target_path : str, optional (default: append "target" to `input_path`)
        Path to target directory where generated code will be written into. Default is ``target``, which will be created in the current working directory if it does not yet exist.
    logging_level : str, optional (default: "ERROR")
        Sets the logging level, i.e., which level of messages should be printed. Default is ERROR, available are: DEBUG, INFO, WARNING, ERROR, NO.
    module_name : str, optional (default: "nestmlmodule")
        Sets the name of the module which shall be generated. Default is the name of the directory containing the models. The name has to end in ``module``. Default is ``nestmlmodule``.
    store_log : bool, optional (default: False)
        Stores a log.txt containing all messages in JSON notation. Default is OFF.
    suffix : str, optional (default: "")
        A suffix string that will be appended to the name of all generated models.
    install_path
        Path to the directory where the generated code will be installed.
    dev : bool, optional (default: False)
        Enable development mode: code generation is attempted even for models that contain errors, and extra information is rendered in the generated code.
    codegen_opts : Optional[Mapping[str, Any]]
        A dictionary containing additional options for the target code generator.
    """
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

    args.append(qualifier_target_platform_arg)
    args.append(target_platform)

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

    if install_path is not None:
        args.append(qualifier_install_path_arg)
        args.append(str(install_path))

    if dev:
        args.append(qualifier_dev_arg)

    FrontendConfiguration.parse_config(args)

    if codegen_opts:
        FrontendConfiguration.set_codegen_opts(codegen_opts)

    if not process() == 0:
        raise Exception("Error(s) occurred while processing the model")


def generate_nest_target(input_path: Union[str, Sequence[str]], target_path: Optional[str] = None,
                         install_path: Optional[str] = None, logging_level="ERROR",
                         module_name=None, store_log: bool=False, suffix: str="",
                         dev: bool=False, codegen_opts: Optional[Mapping[str, Any]]=None):
    r"""Generate and build code for NEST Simulator.

    Parameters
    ----------
    input_path : str **or** Sequence[str]
        Path to the NESTML file(s) or to folder(s) containing NESTML files to convert to NEST code.
    target_path : str, optional (default: append "target" to `input_path`)
        Path to the generated C++ code and install files.
    logging_level : str, optional (default: "ERROR")
        Sets which level of information should be displayed duing code generation (among "ERROR", "WARNING", "INFO", or "NO").
    module_name : str, optional (default: "nestmlmodule")
        Name of the module, which will be used to import the model in NEST via `nest.Install(module_name)`.
    store_log : bool, optional (default: False)
        Whether the log should be saved to file.
    suffix : str, optional (default: "")
        A suffix string that will be appended to the name of all generated models.
    install_path
        Path to the directory where the generated NEST extension module will be installed into. If the parameter is not specified, the module will be installed into the NEST Simulator installation directory, as reported by nest-config.
    dev : bool, optional (default: False)
        Enable development mode: code generation is attempted even for models that contain errors, and extra information is rendered in the generated code.
    codegen_opts : Optional[Mapping[str, Any]]
        A dictionary containing additional options for the target code generator.
    """
    generate_target(input_path, target_platform="NEST", target_path=target_path, logging_level=logging_level,
                    module_name=module_name, store_log=store_log, suffix=suffix, install_path=install_path,
                    dev=dev, codegen_opts=codegen_opts)


def main() -> int:
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

    codegen_and_builder_opts = FrontendConfiguration.get_codegen_opts()
    _codeGenerator = code_generator_from_target_name(FrontendConfiguration.get_target_platform())
    codegen_and_builder_opts = _codeGenerator.set_options(codegen_and_builder_opts)
    _builder = builder_from_target_name(FrontendConfiguration.get_target_platform())

    if _builder is not None:
        codegen_and_builder_opts = _builder.set_options(codegen_and_builder_opts)

    if len(codegen_and_builder_opts) > 0:
        raise CodeGeneratorOptionsException("The code generator option(s) \"" + ", ".join(codegen_and_builder_opts.keys()) + "\" do not exist.")

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
        if not FrontendConfiguration.is_dev:
            for neuron in neurons:
                if Logger.has_errors(neuron):
                    code, message = Messages.get_model_contains_errors(neuron.get_name())
                    Logger.log_message(node=neuron, code=code, message=message,
                                       error_position=neuron.get_source_position(),
                                       log_level=LoggingLevel.INFO)
                    neurons.remove(neuron)
                    errors_occurred = True

            for synapse in synapses:
                if Logger.has_errors(synapse):
                    code, message = Messages.get_model_contains_errors(synapse.get_name())
                    Logger.log_message(node=synapse, code=code, message=message,
                                       error_position=synapse.get_source_position(),
                                       log_level=LoggingLevel.INFO)
                    synapses.remove(synapse)
                    errors_occurred = True

        # perform code generation
        _codeGenerator.generate_code(neurons, synapses)
        for astnode in neurons + synapses:
            if Logger.has_errors(astnode):
                errors_occurred = True
                break

    # perform build
    if not errors_occurred and _builder is not None:
        _builder.build()

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
    if not os.path.isdir(os.path.join(FrontendConfiguration.get_target_path(), "..", "report")):
        os.makedirs(os.path.join(FrontendConfiguration.get_target_path(), "..", "report"))


def store_log_to_file():
    with open(str(os.path.join(FrontendConfiguration.get_target_path(), "..", "report",
                               "log")) + ".txt", "w+") as f:
        f.write(str(Logger.get_json_format()))
