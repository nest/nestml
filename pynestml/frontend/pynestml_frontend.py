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

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

import os
import sys

from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.codegeneration.builder import Builder
from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.exceptions.code_generator_options_exception import CodeGeneratorOptionsException
from pynestml.frontend.frontend_configuration import FrontendConfiguration, InvalidPathException, \
    qualifier_store_log_arg, qualifier_module_name_arg, qualifier_logging_level_arg, \
    qualifier_target_platform_arg, qualifier_target_path_arg, qualifier_input_path_arg, qualifier_suffix_arg, \
    qualifier_dev_arg, qualifier_install_path_arg
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.transformers.transformer import Transformer
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser


def get_known_targets():
    targets = ["NEST", "NEST_compartmental", "python_standalone", "autodoc", "spinnaker", "none"]
    targets = [s.upper() for s in targets]
    return targets


def transformers_from_target_name(target_name: str, options: Optional[Mapping[str, Any]] = None) -> Tuple[Transformer, Dict[str, Any]]:
    """Static factory method that returns a list of new instances of a child class of Transformers"""
    assert target_name.upper() in get_known_targets(
    ), "Unknown target platform requested: \"" + str(target_name) + "\""

    # default: no transformers (empty list); options unchanged
    transformers: List[Transformer] = []
    if options is None:
        options = {}

    if target_name.upper() in ["NEST", "SPINNAKER"]:
        from pynestml.transformers.illegal_variable_name_transformer import IllegalVariableNameTransformer

        # rewrite all C++ keywords
        # from: https://docs.microsoft.com/en-us/cpp/cpp/keywords-cpp 2022-04-23
        variable_name_rewriter = IllegalVariableNameTransformer({"forbidden_names": ["alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand", "bitor", "bool", "break", "case", "catch", "char", "char8_t", "char16_t", "char32_t", "class", "compl", "concept", "const", "const_cast", "consteval", "constexpr", "constinit", "continue", "co_await", "co_return", "co_yield", "decltype", "default", "delete", "do", "double", "dynamic_cast", "else", "enum", "explicit", "export", "extern", "false", "float", "for", "friend",
                                                                "goto", "if", "inline", "int", "long", "mutable", "namespace", "new", "noexcept", "not", "not_eq", "nullptr", "operator", "or", "or_eq", "private", "protected", "public", "register", "reinterpret_cast", "requires", "return", "short", "signed", "sizeof", "static", "static_assert", "static_cast", "struct", "switch", "template", "this", "thread_local", "throw", "true", "try", "typedef", "typeid", "typename", "union", "unsigned", "using", "virtual", "void", "volatile", "wchar_t", "while", "xor", "xor_eq"]})
        transformers.append(variable_name_rewriter)

    if target_name.upper() in ["SPINNAKER"]:
        from pynestml.transformers.synapse_remove_post_port import SynapseRemovePostPortTransformer

        # co-generate neuron and synapse
        synapse_post_neuron_co_generation = SynapseRemovePostPortTransformer()
        options = synapse_post_neuron_co_generation.set_options(options)
        transformers.append(synapse_post_neuron_co_generation)

    if target_name.upper() == "NEST":
        from pynestml.transformers.synapse_post_neuron_transformer import SynapsePostNeuronTransformer

        # co-generate neuron and synapse
        synapse_post_neuron_co_generation = SynapsePostNeuronTransformer()
        options = synapse_post_neuron_co_generation.set_options(options)
        transformers.append(synapse_post_neuron_co_generation)

    if target_name.upper() in ["PYTHON_STANDALONE"]:
        from pynestml.transformers.illegal_variable_name_transformer import IllegalVariableNameTransformer

        # rewrite all Python keywords
        # from: ``import keyword; print(keyword.kwlist)``
        variable_name_rewriter = IllegalVariableNameTransformer({"forbidden_names": ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']})
        transformers.append(variable_name_rewriter)

    return transformers, options


def code_generator_from_target_name(target_name: str, options: Optional[Mapping[str, Any]] = None) -> CodeGenerator:
    """Static factory method that returns a new instance of a child class of CodeGenerator"""
    assert target_name.upper() in get_known_targets(
    ), "Unknown target platform requested: \"" + str(target_name) + "\""

    if target_name.upper() == "NEST":
        from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
        return NESTCodeGenerator(options)

    if target_name.upper() == "PYTHON_STANDALONE":
        from pynestml.codegeneration.python_standalone_code_generator import PythonStandaloneCodeGenerator
        return PythonStandaloneCodeGenerator(options)

    if target_name.upper() == "AUTODOC":
        from pynestml.codegeneration.autodoc_code_generator import AutoDocCodeGenerator
        assert options is None or options == {
        }, "\"autodoc\" code generator does not support options"
        return AutoDocCodeGenerator()

    if target_name.upper() == "NEST_COMPARTMENTAL":
        from pynestml.codegeneration.nest_compartmental_code_generator import NESTCompartmentalCodeGenerator
        return NESTCompartmentalCodeGenerator()

    if target_name.upper() == "SPINNAKER":
        from pynestml.codegeneration.spinnaker_code_generator import SpiNNakerCodeGenerator
        return SpiNNakerCodeGenerator(options)

    if target_name.upper() == "NONE":
        # dummy/null target: user requested to not generate any code
        code, message = Messages.get_no_code_generated()
        Logger.log_message(None, code, message, None, LoggingLevel.INFO)
        return CodeGenerator("", options)

    # cannot reach here due to earlier assert -- silence
    assert "Unknown code generator requested: " + target_name
    # static checker warnings


def builder_from_target_name(target_name: str, options: Optional[Mapping[str, Any]] = None) -> Tuple[Builder, Dict[str, Any]]:
    r"""Static factory method that returns a new instance of a child class of Builder"""
    from pynestml.frontend.pynestml_frontend import get_known_targets

    assert target_name.upper() in get_known_targets(
    ), "Unknown target platform requested: \"" + str(target_name) + "\""

    if target_name.upper() in ["NEST", "NEST_COMPARTMENTAL"]:
        from pynestml.codegeneration.nest_builder import NESTBuilder
        builder = NESTBuilder(options)
        remaining_options = builder.set_options(options)
        return builder, remaining_options

    if target_name.upper() == "SPINNAKER":
        from pynestml.codegeneration.spinnaker_builder import SpiNNakerBuilder
        builder = SpiNNakerBuilder(options)
        remaining_options = builder.set_options(options)
        return builder, remaining_options

    return None, options  # no builder requested or available


def generate_target(input_path: Union[str, Sequence[str]], target_platform: str, target_path=None,
                    install_path: str = None, logging_level="ERROR", module_name=None, store_log=False, suffix="",
                    dev=False, codegen_opts: Optional[Mapping[str, Any]] = None):
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

    configure_front_end(input_path, target_platform, target_path, install_path, logging_level,
                        module_name, store_log, suffix, dev, codegen_opts)
    if not process() == 0:
        raise Exception("Error(s) occurred while processing the model")


def configure_front_end(input_path: Union[str, Sequence[str]], target_platform: str, target_path=None,
                        install_path: str = None, logging_level="ERROR", module_name=None, store_log=False, suffix="",
                        dev=False, codegen_opts: Optional[Mapping[str, Any]] = None):

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


def generate_nest_target(input_path: Union[str, Sequence[str]], target_path: Optional[str] = None,
                         install_path: Optional[str] = None, logging_level="ERROR",
                         module_name=None, store_log: bool = False, suffix: str = "",
                         dev: bool = False, codegen_opts: Optional[Mapping[str, Any]] = None):
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


def generate_python_standalone_target(input_path: Union[str, Sequence[str]], target_path: Optional[str] = None,
                                      logging_level="ERROR", module_name: str = "nestmlmodule", store_log: bool = False,
                                      suffix: str = "", dev: bool = False, codegen_opts: Optional[Mapping[str, Any]] = None):
    r"""Generate and build code for the standalone Python target.

    Parameters
    ----------
    input_path : str **or** Sequence[str]
        Path to the NESTML file(s) or to folder(s) containing NESTML files to convert to NEST code.
    target_path : str, optional (default: append "target" to `input_path`)
        Path to the generated C++ code and install files.
    logging_level : str, optional (default: "ERROR")
        Sets which level of information should be displayed duing code generation (among "ERROR", "WARNING", "INFO", or "NO").
    module_name : str, optional (default: "nestmlmodule")
        The name of the generated Python module.
    store_log : bool, optional (default: False)
        Whether the log should be saved to file.
    suffix : str, optional (default: "")
        A suffix string that will be appended to the name of all generated models.
    dev : bool, optional (default: False)
        Enable development mode: code generation is attempted even for models that contain errors, and extra information is rendered in the generated code.
    codegen_opts : Optional[Mapping[str, Any]]
        A dictionary containing additional options for the target code generator.
    """
    generate_target(input_path, target_platform="python_standalone", target_path=target_path,
                    logging_level=logging_level, store_log=store_log, suffix=suffix, dev=dev,
                    codegen_opts=codegen_opts)


def generate_spinnaker_target(input_path: Union[str, Sequence[str]], target_path: Optional[str] = None, install_path: Optional[str] = None,
                              logging_level="ERROR", module_name: str = "nestmlmodule", store_log: bool=False,
                              suffix: str="", dev: bool=False, codegen_opts: Optional[Mapping[str, Any]]=None):
    r"""Generate and build code for the SpiNNaker target.

    Parameters
    ----------
    input_path : str **or** Sequence[str]
        Path to the NESTML file(s) or to folder(s) containing NESTML files to convert to NEST code.
    target_path : str, optional (default: append "target" to `input_path`)
        Path to the generated C++ code and install files.
    install_path
        Path to the directory where the generated code will be installed.
    logging_level : str, optional (default: "ERROR")
        Sets which level of information should be displayed duing code generation (among "ERROR", "WARNING", "INFO", or "NO").
    module_name : str, optional (default: "nestmlmodule")
        The name of the generated Python module.
    store_log : bool, optional (default: False)
        Whether the log should be saved to file.
    suffix : str, optional (default: "")
        A suffix string that will be appended to the name of all generated models.
    dev : bool, optional (default: False)
        Enable development mode: code generation is attempted even for models that contain errors, and extra information is rendered in the generated code.
    codegen_opts : Optional[Mapping[str, Any]]
        A dictionary containing additional options for the target code generator.
    """
    generate_target(input_path, target_platform="spinnaker", target_path=target_path,
                    install_path=install_path,
                    logging_level=logging_level, store_log=store_log, suffix=suffix, dev=dev,
                    codegen_opts=codegen_opts)


def generate_nest_compartmental_target(input_path: Union[str, Sequence[str]], target_path: Optional[str] = None,
                                       install_path: Optional[str] = None, logging_level="ERROR",
                                       module_name=None, store_log: bool = False, suffix: str = "",
                                       dev: bool = False, codegen_opts: Optional[Mapping[str, Any]] = None):
    r"""Generate and build compartmental model code for NEST Simulator.

    Parameters
    ----------
    input_path : str **or** Sequence[str]
        Path to the NESTML file(s) or to folder(s) containing NESTML files to convert to NEST code.
    target_path : str, optional (default: append "target" to `input_path`)
        Path to the generated C++ code and install files.
    install_path
        Path to the directory where the generated code will be installed.
    logging_level : str, optional (default: "ERROR")
        Sets which level of information should be displayed duing code generation (among "ERROR", "WARNING", "INFO", or "NO").
    module_name : str, optional (default: "nestmlmodule")
        The name of the generated Python module.
    store_log : bool, optional (default: False)
        Whether the log should be saved to file.
    suffix : str, optional (default: "")
        A suffix string that will be appended to the name of all generated models.
    dev : bool, optional (default: False)
        Enable development mode: code generation is attempted even for models that contain errors, and extra information is rendered in the generated code.
    codegen_opts : Optional[Mapping[str, Any]]
        A dictionary containing additional options for the target code generator.
    """
    generate_target(input_path, target_platform="NEST_compartmental", target_path=target_path,
                    logging_level=logging_level, module_name=module_name, store_log=store_log,
                    suffix=suffix, install_path=install_path, dev=dev, codegen_opts=codegen_opts)


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
        print(e)
        return 1
    # the default Python recursion limit is 1000, which might not be enough in practice when running an AST visitor on a deep tree, e.g. containing an automatically generated expression
    sys.setrecursionlimit(10000)
    # after all argument have been collected, start the actual processing
    return int(process())


def get_parsed_models():
    r"""
   Handle the parsing and validation of the NESTML files

    Returns
    -------
    models: Sequence[Union[ASTNeuron, ASTSynapse]]
        List of correctly parsed models
    errors_occurred : bool
        Flag indicating whether errors occurred during processing
    """
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
        if parsed_unit is None:
            # Parsing error in the NESTML model, return True
            return [],  True

        compilation_units.append(parsed_unit)

    if len(compilation_units) > 0:
        # generate a list of all neurons + synapses
        models: Sequence[Union[ASTNeuron, ASTSynapse]] = []
        for compilationUnit in compilation_units:
            models.extend(compilationUnit.get_neuron_list())
            models.extend(compilationUnit.get_synapse_list())

        # check that no models with duplicate names have been defined
        CoCosManager.check_no_duplicate_compilation_unit_names(models)

        # now exclude those which are broken, i.e. have errors.
        for model in models:
            if Logger.has_errors(model):
                code, message = Messages.get_model_contains_errors(model.get_name())
                Logger.log_message(node=model, code=code, message=message,
                                   error_position=model.get_source_position(),
                                   log_level=LoggingLevel.WARNING)
                return [model], True

        return models, False


def transform_models(transformers, models):
    for transformer in transformers:
        models = transformer.transform(models)
    return models


def generate_code(code_generators, models):
    code_generators.generate_code(models)


def process():
    r"""
    The main toolchain workflow entry point. For all models: parse, validate, transform, generate code and build.

    Returns
    -------
    errors_occurred : bool
        Flag indicating whether errors occurred during processing
    """

    # initialize and set options for transformers, code generator and builder
    codegen_and_builder_opts = FrontendConfiguration.get_codegen_opts()

    transformers, codegen_and_builder_opts = transformers_from_target_name(FrontendConfiguration.get_target_platform(),
                                                                           options=codegen_and_builder_opts)

    code_generator = code_generator_from_target_name(FrontendConfiguration.get_target_platform())
    codegen_and_builder_opts = code_generator.set_options(codegen_and_builder_opts)

    _builder, codegen_and_builder_opts = builder_from_target_name(FrontendConfiguration.get_target_platform(), options=codegen_and_builder_opts)

    if len(codegen_and_builder_opts) > 0:
        raise CodeGeneratorOptionsException("The code generator option(s) \"" + ", ".join(codegen_and_builder_opts.keys()) + "\" do not exist.")

    models, errors_occurred = get_parsed_models()

    if not errors_occurred:
        models = transform_models(transformers, models)
        generate_code(code_generator, models)

        # perform build
        if _builder is not None:
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
    if not os.path.isdir(os.path.join(FrontendConfiguration.get_target_path(), os.pardir, "report")):
        os.makedirs(os.path.join(FrontendConfiguration.get_target_path(), os.pardir, "report"))


def store_log_to_file():
    with open(str(os.path.join(FrontendConfiguration.get_target_path(), os.pardir, "report",
                               "log")) + ".txt", "w+") as f:
        f.write(str(Logger.get_json_format()))
