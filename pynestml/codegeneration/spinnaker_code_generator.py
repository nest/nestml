# -*- coding: utf-8 -*-
#
# spinnaker_code_generator.py
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

import copy
from typing import Sequence, Union, Optional, Mapping, Any

import os

from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.codegeneration.printers.cpp_printer import CppPrinter
from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter
from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter
from pynestml.codegeneration.printers.unitless_c_simple_expression_printer import UnitlessCSimpleExpressionPrinter
from pynestml.codegeneration.printers.c_simple_expression_printer import CSimpleExpressionPrinter
from pynestml.codegeneration.printers.gsl_variable_printer import GSLVariablePrinter
from pynestml.codegeneration.printers.spinnaker_c_function_call_printer import SpinnakerCFunctionCallPrinter
from pynestml.codegeneration.printers.spinnaker_c_type_symbol_printer import SpinnakerCTypeSymbolPrinter
from pynestml.codegeneration.printers.spinnaker_gsl_function_call_printer import SpinnakerGSLFunctionCallPrinter
from pynestml.codegeneration.printers.spinnaker_c_variable_printer import SpinnakerCVariablePrinter
from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.ode_toolbox_function_call_printer import ODEToolboxFunctionCallPrinter
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.codegeneration.printers.python_expression_printer import PythonExpressionPrinter
from pynestml.codegeneration.printers.python_simple_expression_printer import PythonSimpleExpressionPrinter
from pynestml.codegeneration.printers.python_standalone_printer import PythonStandalonePrinter
from pynestml.codegeneration.printers.python_stepping_function_function_call_printer import \
    PythonSteppingFunctionFunctionCallPrinter
from pynestml.codegeneration.printers.python_stepping_function_variable_printer import \
    PythonSteppingFunctionVariablePrinter
from pynestml.codegeneration.printers.python_variable_printer import PythonVariablePrinter
from pynestml.codegeneration.python_standalone_code_generator import PythonStandaloneCodeGenerator
from pynestml.codegeneration.printers.spinnaker_python_function_call_printer import SpinnakerPythonFunctionCallPrinter
from pynestml.codegeneration.printers.spinnaker_python_simple_expression_printer import \
    SpinnakerPythonSimpleExpressionPrinter
from pynestml.codegeneration.printers.spinnaker_python_type_symbol_printer import SpinnakerPythonTypeSymbolPrinter
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse


class CustomNESTCodeGenerator(NESTCodeGenerator):
    def setup_printers(self):
        self._constant_printer = ConstantPrinter()

        # C/Spinnaker API printers
        self._type_symbol_printer = SpinnakerCTypeSymbolPrinter()
        self._nest_variable_printer = SpinnakerCVariablePrinter(expression_printer=None, with_origin=True,
                                                                with_vector_parameter=True)
        self._nest_function_call_printer = SpinnakerCFunctionCallPrinter(None)
        self._nest_function_call_printer_no_origin = SpinnakerCFunctionCallPrinter(None)

        self._printer = CppExpressionPrinter(
            simple_expression_printer=CSimpleExpressionPrinter(variable_printer=self._nest_variable_printer,
                                                               constant_printer=self._constant_printer,
                                                               function_call_printer=self._nest_function_call_printer))
        self._nest_variable_printer._expression_printer = self._printer
        self._nest_function_call_printer._expression_printer = self._printer
        self._nest_printer = CppPrinter(expression_printer=self._printer)

        self._nest_variable_printer_no_origin = SpinnakerCVariablePrinter(None, with_origin=False,
                                                                          with_vector_parameter=False)
        self._printer_no_origin = CppExpressionPrinter(
            simple_expression_printer=CSimpleExpressionPrinter(variable_printer=self._nest_variable_printer_no_origin,
                                                               constant_printer=self._constant_printer,
                                                               function_call_printer=self._nest_function_call_printer_no_origin))
        self._nest_variable_printer_no_origin._expression_printer = self._printer_no_origin
        self._nest_function_call_printer_no_origin._expression_printer = self._printer_no_origin

        # GSL printers
        self._gsl_variable_printer = GSLVariablePrinter(None)
        self._gsl_function_call_printer = SpinnakerGSLFunctionCallPrinter(None)

        self._gsl_printer = CppExpressionPrinter(
            simple_expression_printer=UnitlessCSimpleExpressionPrinter(variable_printer=self._gsl_variable_printer,
                                                                       constant_printer=self._constant_printer,
                                                                       function_call_printer=self._gsl_function_call_printer))
        self._gsl_function_call_printer._expression_printer = self._gsl_printer

        # ODE-toolbox printers
        self._ode_toolbox_variable_printer = ODEToolboxVariablePrinter(None)
        self._ode_toolbox_function_call_printer = ODEToolboxFunctionCallPrinter(None)
        self._ode_toolbox_printer = ODEToolboxExpressionPrinter(
            simple_expression_printer=UnitlessCSimpleExpressionPrinter(
                variable_printer=self._ode_toolbox_variable_printer,
                constant_printer=self._constant_printer,
                function_call_printer=self._ode_toolbox_function_call_printer))
        self._ode_toolbox_variable_printer._expression_printer = self._ode_toolbox_printer
        self._ode_toolbox_function_call_printer._expression_printer = self._ode_toolbox_printer


class CustomPythonStandaloneCodeGenerator(PythonStandaloneCodeGenerator):
    def setup_printers(self):
        super().setup_printers()

        self._type_symbol_printer = SpinnakerPythonTypeSymbolPrinter()
        self._constant_printer = ConstantPrinter()

        # Python/mini simulation environment API printers
        self._nest_variable_printer = PythonVariablePrinter(expression_printer=None, with_origin=False,
                                                            with_vector_parameter=True)
        self._nest_function_call_printer = SpinnakerPythonFunctionCallPrinter(None)
        self._nest_function_call_printer_no_origin = SpinnakerPythonFunctionCallPrinter(None)

        self._printer = PythonExpressionPrinter(simple_expression_printer=SpinnakerPythonSimpleExpressionPrinter(
            variable_printer=self._nest_variable_printer,
            constant_printer=self._constant_printer,
            function_call_printer=self._nest_function_call_printer))
        self._nest_variable_printer._expression_printer = self._printer
        self._nest_function_call_printer._expression_printer = self._printer
        self._nest_printer = PythonStandalonePrinter(expression_printer=self._printer)

        self._nest_variable_printer_no_origin = PythonVariablePrinter(None, with_origin=False,
                                                                      with_vector_parameter=False)
        self._printer_no_origin = PythonExpressionPrinter(
            simple_expression_printer=SpinnakerPythonSimpleExpressionPrinter(
                variable_printer=self._nest_variable_printer_no_origin,
                constant_printer=self._constant_printer,
                function_call_printer=self._nest_function_call_printer_no_origin))
        self._nest_variable_printer_no_origin._expression_printer = self._printer_no_origin
        self._nest_function_call_printer_no_origin._expression_printer = self._printer_no_origin

        self._nest_unitless_function_call_printer = SpinnakerPythonFunctionCallPrinter(None)

        # GSL printers
        self._gsl_variable_printer = PythonSteppingFunctionVariablePrinter(None)
        print("In Python code generator: created self._gsl_variable_printer = " + str(self._gsl_variable_printer))
        self._gsl_function_call_printer = PythonSteppingFunctionFunctionCallPrinter(None)
        self._gsl_printer = PythonExpressionPrinter(simple_expression_printer=SpinnakerPythonSimpleExpressionPrinter(
            variable_printer=self._gsl_variable_printer,
            constant_printer=self._constant_printer,
            function_call_printer=self._gsl_function_call_printer))
        self._gsl_function_call_printer._expression_printer = self._gsl_printer
        self._gsl_variable_printer._expression_printer = self._gsl_printer


class SpiNNakerCodeGenerator(CodeGenerator):
    r"""
    Code generator for SpiNNaker
    """

    codegen_cpp: Optional[NESTCodeGenerator] = None

    _default_options = {
        "neuron_synapse_pairs": [],
        "templates": {
            "path": os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources_spinnaker"))),
            "model_templates": {
                "neuron": ["@NEURON_NAME@_impl.h.jinja2",
                           "@NEURON_NAME@.py.jinja2",
                           "@NEURON_NAME@_impl.py.jinja2",
                           "@NEURON_NAME@_chain_example.py.jinja2",
                           "__init__.py.jinja2",
                           "Makefile_@NEURON_NAME@_impl.jinja2"],
                "synapse": ["@SYNAPSE_NAME@_impl.c.jinja2",
                            "@SYNAPSE_NAME@_impl.h.jinja2",
                            "@SYNAPSE_NAME@_timing_impl.h.jinja2",
                            "@SYNAPSE_NAME@_timing_impl.c.jinja2",
                            "@SYNAPSE_NAME@_weight_impl.h.jinja2",
                            "@SYNAPSE_NAME@_weight_impl.c.jinja2",
                            "@SYNAPSE_NAME@.py.jinja2",
                            "@SYNAPSE_NAME@_timing.py.jinja2",
                            "@SYNAPSE_NAME@_weight.py.jinja2",
                            "@SYNAPSE_NAME@_impl.py.jinja2",
                            "Makefile_@SYNAPSE_NAME@_impl.jinja2"],
            },
            "module_templates": ["Makefile_root.jinja2", "Makefile_models.jinja2", "extra.mk.jinja2",
                                 "extra_neuron.mk.jinja2", "extra_synapse.mk.jinja2"]
        }
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("SpiNNaker", options)

        options_cpp = copy.deepcopy(NESTCodeGenerator._default_options)
        options_cpp["neuron_synapse_pairs"] = self._options["neuron_synapse_pairs"]
        options_cpp["templates"]["model_templates"]["neuron"] = [fname for fname in
                                                                 self._options["templates"]["model_templates"]["neuron"]
                                                                 if ((fname.endswith(".h.jinja2") or fname.endswith(".c.jinja2")
                                                                      or ("Makefile" in fname)) and "@NEURON_NAME@" in fname)]
        options_cpp["templates"]["model_templates"]["synapse"] = [fname for fname in
                                                                  self._options["templates"]["model_templates"]["synapse"]
                                                                  if ((fname.endswith(".h.jinja2") or fname.endswith(".c.jinja2") or ("Makefile" in fname)) and "@SYNAPSE_NAME@" in fname)]
        options_cpp["nest_version"] = "<not available>"
        options_cpp["templates"]["module_templates"] = self._options["templates"]["module_templates"]
        options_cpp["templates"]["path"] = self._options["templates"]["path"]
        self.codegen_cpp = CustomNESTCodeGenerator(options_cpp)
        self.codegen_cpp._target = "SpiNNaker"

        options_py = copy.deepcopy(PythonStandaloneCodeGenerator._default_options)
        options_py["templates"]["model_templates"]["neuron"] = [fname for fname in
                                                                self._options["templates"]["model_templates"]["neuron"]
                                                                if (fname.endswith(".py.jinja2")) and ("@NEURON_NAME@" in fname or fname == "__init__.py.jinja2")]
        options_py["templates"]["model_templates"]["synapse"] = [fname for fname in
                                                                 self._options["templates"]["model_templates"][
                                                                     "synapse"] if (fname.endswith(".py.jinja2")) and "@SYNAPSE_NAME@" in fname]
        options_py["nest_version"] = "<not available>"
        options_py["templates"]["module_templates"] = []
        options_py["templates"]["path"] = self._options["templates"]["path"]
        self.codegen_py = CustomPythonStandaloneCodeGenerator(options_py)
        self.codegen_py._target = "SpiNNaker"

    def generate_code(self, models: Sequence[Union[ASTNeuron, ASTSynapse]]) -> None:
        cloned_models = []
        for model in models:
            cloned_model = model.clone()
            cloned_model.accept(ASTSymbolTableVisitor())
            cloned_models.append(cloned_model)

        self.codegen_cpp.generate_code(cloned_models)

        cloned_models = []
        for model in models:
            cloned_model = model.clone()
            cloned_model.accept(ASTSymbolTableVisitor())
            cloned_models.append(cloned_model)

        self.codegen_py.generate_code(cloned_models)
