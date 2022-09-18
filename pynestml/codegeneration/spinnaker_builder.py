# -*- coding: utf-8 -*-
#
# spinnaker_builder.py
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

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union

import os
import platform
import subprocess
import sys
import fnmatch

from pynestml.codegeneration.builder import Builder
from pynestml.exceptions.generated_code_build_exception import GeneratedCodeBuildException
from pynestml.exceptions.invalid_path_exception import InvalidPathException
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.nest_assignments_helper import NestAssignmentsHelper
from pynestml.codegeneration.nest_declarations_helper import NestDeclarationsHelper
from pynestml.codegeneration.printers.cpp_types_printer import CppTypesPrinter
from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.codegeneration.printers.gsl_reference_converter import GSLReferenceConverter
from pynestml.codegeneration.printers.unitless_expression_printer import UnitlessExpressionPrinter
from pynestml.codegeneration.printers.nest_printer import NestPrinter
from pynestml.codegeneration.printers.nest_reference_converter import NESTReferenceConverter
from pynestml.codegeneration.printers.ode_toolbox_reference_converter import ODEToolboxReferenceConverter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.real_type_symbol import RealTypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_equations_with_delay_vars_visitor import ASTEquationsWithDelayVarsVisitor
from pynestml.visitors.ast_mark_delay_vars_visitor import ASTMarkDelayVarsVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_random_number_generator_visitor import ASTRandomNumberGeneratorVisitor


class SpiNNakerBuilder(Builder):
    r"""Compiles and build the SpiNNaker generated C code."""

    _default_options = {
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("SPINNAKER", options)

    def build(self) -> None:
        r"""
        This method can be used to build the generated code.

        Raises
        ------
        GeneratedCodeBuildException
            If any kind of failure occurs during compile or build.
        InvalidPathException
            If a failure occurs while trying to access the target path or the SpiNNaker installation path.
        """
        target_path = FrontendConfiguration.get_target_path()

        if not os.path.isdir(target_path):
            raise InvalidPathException('Target path (' + target_path + ') is not a directory!')

        install_path = FrontendConfiguration.get_install_path()

        if not os.path.isdir(install_path):
            raise InvalidPathException('Installation path (' + install_path + ') is not a directory!')

        generated_file_names = os.listdir(target_path)
        generated_file_names_neuron_py = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.py") and not "impl.py" in fn]
        generated_file_names_neuron_impl_py = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.py") and "impl.py" in fn]
        generated_file_names_makefiles = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "Makefile_*") if not fn == "Makefile"]
        generated_file_names_neuron_c = [fn for fn in generated_file_names if fnmatch.fnmatch(fn, "*.h")]

        old_cwd = os.getcwd()
        try:
            os.chdir(install_path)

            make_cmd = ['make']

            # check if we run on win
            if sys.platform.startswith('win'):
                shell = True
            else:
                shell = False

            # copy files from target to install directory
            # Copy the pyNN python file
            try:
                os.makedirs(os.path.join(install_path, "python_models8", "neuron", "builds"))
            except:
                pass
            for fn in generated_file_names_neuron_py:
                try:
                    subprocess.check_call(["cp", fn, os.path.join(install_path, "python_models8", "neuron", "builds")], stderr=subprocess.STDOUT, shell=shell,
                                        cwd=target_path)
                except subprocess.CalledProcessError as e:
                    raise GeneratedCodeBuildException(
                        'Error occurred during install! More detailed error messages can be found in stdout.')

            # Copy the pyNN implementation file
            try:
                os.makedirs(os.path.join(install_path, "python_models8", "neuron", "implementations"))
            except:
                pass

            for fn in generated_file_names_neuron_impl_py:
                try:
                    subprocess.check_call(["cp", os.path.join(target_path, fn), os.path.join(install_path, "python_models8", "neuron", "implementations")], stderr=subprocess.STDOUT, shell=shell,
                                        cwd=target_path)
                except subprocess.CalledProcessError as e:
                    raise GeneratedCodeBuildException(
                        'Error occurred during install! More detailed error messages can be found in stdout.')

            # Copy the root Makefile
            try:
                os.makedirs(os.path.join(install_path, "c_models", "makefiles"))
            except:
                pass
            try:
                subprocess.check_call(["cp", "Makefile", os.path.join(install_path, "c_models", "makefiles", "Makefile")], stderr=subprocess.STDOUT, shell=shell,
                                    cwd=target_path)
            except subprocess.CalledProcessError as e:
                raise GeneratedCodeBuildException(
                    'Error occurred during install! More detailed error messages can be found in stdout.')

            # Copy the model Makefile
            for fn in generated_file_names_makefiles:
                neuron_subdir = fn[len("Makefile_"):]
                try:
                    try:
                        os.makedirs(os.path.join(install_path, "c_models", "makefiles", neuron_subdir))
                    except:
                        pass
                    subprocess.check_call(["cp", fn, os.path.join(install_path, "c_models", "makefiles", neuron_subdir, "Makefile")], stderr=subprocess.STDOUT, shell=shell,
                                        cwd=target_path)
                except subprocess.CalledProcessError as e:
                    raise GeneratedCodeBuildException(
                        'Error occurred during install! More detailed error messages can be found in stdout.')

            # Copy the .h files of the neuron model
            try:
                os.makedirs(os.path.join(install_path, "c_models", "src", "my_models", "implementations"))
            except:
                pass
            for fn in generated_file_names_neuron_c:
                try:
                    subprocess.check_call(["cp", fn, os.path.join(install_path, "c_models", "src", "my_models", "implementations", fn)], stderr=subprocess.STDOUT, shell=shell,
                                          cwd=target_path)
                except:
                    raise GeneratedCodeBuildException(
                        'Error occurred during install! More detailed error messages can be found in stdout.')

            # call make
            try:
                subprocess.check_call(make_cmd, stderr=subprocess.STDOUT, shell=shell,
                                      cwd=str(os.path.join(install_path, "c_models", "makefiles")))
            except subprocess.CalledProcessError as e:
                raise GeneratedCodeBuildException(
                    'Error occurred during \'make\'! More detailed error messages can be found in stdout.')
        finally:
            os.chdir(old_cwd)
