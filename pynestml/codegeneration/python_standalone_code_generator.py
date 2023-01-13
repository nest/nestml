# -*- coding: utf-8 -*-
#
# python_standalone_code_generator.py
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

from typing import Any, Dict, Mapping, Optional, Sequence, Union

import os

from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.python_expression_printer import PythonExpressionPrinter
from pynestml.codegeneration.printers.python_stepping_function_function_call_printer import PythonSteppingFunctionFunctionCallPrinter
from pynestml.codegeneration.printers.python_stepping_function_variable_printer import PythonSteppingFunctionVariablePrinter
from pynestml.codegeneration.python_code_generator_utils import PythonCodeGeneratorUtils
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.codegeneration.printers.python_type_symbol_printer import PythonTypeSymbolPrinter
from pynestml.codegeneration.printers.python_standalone_printer import PythonStandalonePrinter
from pynestml.codegeneration.printers.python_function_call_printer import PythonFunctionCallPrinter
from pynestml.codegeneration.printers.python_variable_printer import PythonVariablePrinter
from pynestml.codegeneration.printers.python_simple_expression_printer import PythonSimpleExpressionPrinter


class PythonStandaloneCodeGenerator(NESTCodeGenerator):

    _default_options = {
        "neuron_synapse_pairs": [],
        "preserve_expressions": False,
        "simplify_expression": "sympy.logcombine(sympy.powsimp(sympy.expand(expr)))",
        "templates": {
            "path": "point_neuron",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.py.jinja2"],
                "synapse": ["@SYNAPSE_NAME@.py.jinja2"]
            },
            "module_templates": ["simulator.py.jinja2", "test_python_standalone_module.py.jinja2", "neuron.py.jinja2", "spike_generator.py.jinja2", "utils.py.jinja2"]
        }
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(NESTCodeGenerator, self).__init__("python_standalone", PythonStandaloneCodeGenerator._default_options.update(options if options else {}))

        self.analytic_solver = {}
        self.numeric_solver = {}
        self.non_equations_state_variables = {}  # those state variables not defined as an ODE in the equations block

        self.setup_template_env()
        self.setup_printers()

    def setup_printers(self):
        super().setup_printers()

        self._type_symbol_printer = PythonTypeSymbolPrinter()
        self._constant_printer = ConstantPrinter()

        # Python/mini simulation environment API printers
        self._nest_variable_printer = PythonVariablePrinter(expression_printer=None, with_origin=True, with_vector_parameter=True)
        self._nest_function_call_printer = PythonFunctionCallPrinter(None)
        self._nest_function_call_printer_no_origin = PythonFunctionCallPrinter(None)

        self._printer = PythonExpressionPrinter(simple_expression_printer=PythonSimpleExpressionPrinter(variable_printer=self._nest_variable_printer,
                                                                                                        constant_printer=self._constant_printer,
                                                                                                        function_call_printer=self._nest_function_call_printer))
        self._nest_variable_printer._expression_printer = self._printer
        self._nest_function_call_printer._expression_printer = self._printer
        self._nest_printer = PythonStandalonePrinter(expression_printer=self._printer)

        self._nest_variable_printer_no_origin = PythonVariablePrinter(None, with_origin=False, with_vector_parameter=False)
        self._printer_no_origin = PythonExpressionPrinter(simple_expression_printer=PythonSimpleExpressionPrinter(variable_printer=self._nest_variable_printer_no_origin,
                                                                                                                  constant_printer=self._constant_printer,
                                                                                                                  function_call_printer=self._nest_function_call_printer_no_origin))
        self._nest_variable_printer_no_origin._expression_printer = self._printer_no_origin
        self._nest_function_call_printer_no_origin._expression_printer = self._printer_no_origin

        self._nest_unitless_function_call_printer = PythonFunctionCallPrinter(None)

        # GSL printers
        self._gsl_variable_printer = PythonSteppingFunctionVariablePrinter(None)
        print("In Python code generator: created self._gsl_variable_printer = " + str(self._gsl_variable_printer))
        self._gsl_function_call_printer = PythonSteppingFunctionFunctionCallPrinter(None)
        self._gsl_printer = PythonExpressionPrinter(simple_expression_printer=PythonSimpleExpressionPrinter(variable_printer=self._gsl_variable_printer,
                                                                                                            constant_printer=self._constant_printer,
                                                                                                            function_call_printer=self._gsl_function_call_printer))
        self._gsl_function_call_printer._expression_printer = self._gsl_printer
        self._gsl_variable_printer._expression_printer = self._gsl_printer

    def _get_model_namespace(self, astnode: ASTNeuronOrSynapse) -> Dict:
        namespace = super()._get_model_namespace(astnode)
        namespace["python_codegen_utils"] = PythonCodeGeneratorUtils
        namespace["gsl_printer"] = self._gsl_printer

        return namespace
