# -*- coding: utf-8 -*-
#
# genn_code_generator.py
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

from typing import Any, Dict, List, Mapping, Optional, Tuple

from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.codegeneration.printers.cpp_printer import CppPrinter
from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter
from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.genn_c_variable_printer import GeNNCVariablePrinter
from pynestml.codegeneration.printers.genn_derived_variable_printer import GeNNDerivedVariablePrinter
from pynestml.codegeneration.printers.genn_function_call_printer import GeNNFunctionCallPrinter
from pynestml.codegeneration.printers.nest2_cpp_function_call_printer import NEST2CppFunctionCallPrinter
from pynestml.codegeneration.printers.nest_cpp_function_call_printer import NESTCppFunctionCallPrinter
from pynestml.codegeneration.printers.nest_cpp_type_symbol_printer import NESTCppTypeSymbolPrinter
from pynestml.codegeneration.printers.nest_gsl_function_call_printer import NESTGSLFunctionCallPrinter
from pynestml.codegeneration.printers.python_expression_printer import PythonExpressionPrinter
from pynestml.codegeneration.printers.python_stepping_function_function_call_printer import PythonSteppingFunctionFunctionCallPrinter
from pynestml.codegeneration.printers.python_stepping_function_variable_printer import PythonSteppingFunctionVariablePrinter
from pynestml.codegeneration.python_code_generator_utils import PythonCodeGeneratorUtils
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_model import ASTModel
from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.codegeneration.printers.python_type_symbol_printer import PythonTypeSymbolPrinter
from pynestml.codegeneration.printers.python_standalone_printer import PythonStandalonePrinter
from pynestml.codegeneration.printers.python_function_call_printer import PythonFunctionCallPrinter
from pynestml.codegeneration.printers.python_variable_printer import PythonVariablePrinter
from pynestml.codegeneration.printers.python_simple_expression_printer import PythonSimpleExpressionPrinter
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_on_condition_block import ASTOnConditionBlock
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_visitor import ASTVisitor


class GeNNCodeGenerator(NESTCodeGenerator):
    r"""
    Code generator for the GeNN target.

    Options:

    - **neuron_models**: List of neuron model names. Instructs the code generator that models with these names are neuron models.
    - **preserve_expressions**: Set to True, or a list of strings corresponding to individual variable names, to disable internal rewriting of expressions, and return same output as input expression where possible. Only applies to variables specified as first-order differential equations. (This parameter is passed to ODE-toolbox.)
    - **simplify_expression**: For all expressions ``expr`` that are rewritten by ODE-toolbox: the contents of this parameter string are ``eval()``ed in Python to obtain the final output expression. Override for custom expression simplification steps. Example: ``sympy.simplify(expr)``. Default: ``"sympy.logcombine(sympy.powsimp(sympy.expand(expr)))"``. (This parameter is passed to ODE-toolbox.)
    - **templates**: Path containing jinja templates used to generate code.
        - **path**: Path containing jinja templates used to generate code.
        - **model_templates**: A list of the jinja templates or a relative path to a directory containing the neuron model templates.
            - **neuron**: A list of neuron model jinja templates.
        - **module_templates**: A list of the jinja templates or a relative path to a directory containing the templates related to generating the module/package.
    - **solver**: A string identifying the preferred ODE solver. ``"analytic"`` for propagator solver preferred; fallback to numeric solver in case ODEs are not analytically solvable. Use ``"numeric"`` to disable analytic solver.
    - **membrane_potential_variable**: A string identifying a variable in the model that corresponds to the membrane potential of the neuron. This is needed because GeNN treats the membrane potential in a specific way (through dedicated getters and setters).
    """

    _default_options = {
        "preserve_expressions": False,
        "simplify_expression": "sympy.logcombine(sympy.powsimp(sympy.expand(expr)))",
        "templates": {
            "path": "resources_genn",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.py.jinja2"]
            },
            "module_templates": []
        },
        "solver": "analytic",
        "membrane_potential_variable": "V_m"
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(NESTCodeGenerator, self).__init__({**GeNNCodeGenerator._default_options, **(options if options else {})})

        # make sure GeNN code generator contains all options that are present in the NEST code generator
        for k, v in NESTCodeGenerator._default_options.items():
            if not k in self._options.keys():
                self.add_options({k: v})

        self.set_options({"numeric_solver": "forward-Euler"})    # only forward Euler is supported for now for GeNN

        self.analytic_solver = {}
        self.numeric_solver = {}
        self.non_equations_state_variables = {}  # those state variables not defined as an ODE in the equations block

        self.setup_template_env()
        self.setup_printers()

    def setup_printers(self):
        super().setup_printers()

        self._constant_printer = ConstantPrinter()

        # C++/NEST API printers
        self._type_symbol_printer = NESTCppTypeSymbolPrinter()
        self._nest_variable_printer = GeNNCVariablePrinter(expression_printer=None, with_origin=True, with_vector_parameter=True)
        self._nest_function_call_printer = GeNNFunctionCallPrinter(None)
        self._nest_function_call_printer_no_origin = GeNNFunctionCallPrinter(None)

        self._printer = CppExpressionPrinter(simple_expression_printer=CppSimpleExpressionPrinter(variable_printer=self._nest_variable_printer,
                                                                                                  constant_printer=self._constant_printer,
                                                                                                  function_call_printer=self._nest_function_call_printer))
        self._nest_variable_printer._expression_printer = self._printer
        self._nest_function_call_printer._expression_printer = self._printer
        self._nest_printer = CppPrinter(expression_printer=self._printer)

        self._nest_variable_printer_no_origin = GeNNCVariablePrinter(None, with_origin=False, with_vector_parameter=False)
        self._printer_no_origin = CppExpressionPrinter(simple_expression_printer=CppSimpleExpressionPrinter(variable_printer=self._nest_variable_printer_no_origin,
                                                                                                            constant_printer=self._constant_printer,
                                                                                                            function_call_printer=self._nest_function_call_printer_no_origin))
        self._nest_variable_printer_no_origin._expression_printer = self._printer_no_origin
        self._nest_function_call_printer_no_origin._expression_printer = self._printer_no_origin

        # GSL printers
        self._gsl_variable_printer = GeNNCVariablePrinter(None)
        self._gsl_function_call_printer = GeNNFunctionCallPrinter(None)

        self._gsl_printer = CppExpressionPrinter(simple_expression_printer=CppSimpleExpressionPrinter(variable_printer=self._gsl_variable_printer,
                                                                                                      constant_printer=self._constant_printer,
                                                                                                      function_call_printer=self._gsl_function_call_printer))
        self._gsl_function_call_printer._expression_printer = self._gsl_printer

        # Python printers
        self._py_variable_printer = GeNNDerivedVariablePrinter(expression_printer=None, with_origin=True, with_vector_parameter=True)
        self._py_function_call_printer = PythonFunctionCallPrinter(None)
        self._py_function_call_printer_no_origin = PythonFunctionCallPrinter(None)

        self._py_expr_printer = PythonExpressionPrinter(simple_expression_printer=PythonSimpleExpressionPrinter(variable_printer=self._py_variable_printer,
                                                                                                                constant_printer=self._constant_printer,
                                                                                                                function_call_printer=self._py_function_call_printer))
        self._py_variable_printer._expression_printer = self._py_expr_printer
        self._py_function_call_printer._expression_printer = self._py_expr_printer
        self._genn_derived_params_printer = PythonStandalonePrinter(expression_printer=self._py_expr_printer)

    def create_ode_toolbox_indict(self, neuron: ASTModel, kernel_buffers: Mapping[ASTKernel, ASTInputPort]):
        odetoolbox_indict = super().create_ode_toolbox_indict(neuron, kernel_buffers)
        odetoolbox_indict["options"]["propagators_prefix"] = "P"    # GeNN does not support variable names that start with an underscore; hence, override the default "__P"
        odetoolbox_indict["options"]["output_timestep_symbol"] = "dt"

        return odetoolbox_indict

    def _get_model_namespace(self, astnode: ASTModel) -> Dict:
        namespace = super()._get_model_namespace(astnode)

        namespace["threshold_condition"] = self._get_model_threshold_condition_block(astnode).get_cond_expr()
        namespace["threshold_reset_stmts"] = self._get_model_threshold_condition_block(astnode).get_stmts_body()

        namespace["CppVariablePrinter"] = CppVariablePrinter
        namespace["genn_derived_params_printer"] = self._genn_derived_params_printer

        return namespace

    def _expression_contains_variable(self, expr, var_name) -> bool:
        class ContainsVariableVisitor(ASTVisitor):
            def __init__(self):
                super().__init__()
                self.contains_variable = False

            def visit_variable(self, node: ASTNode):
                if node.get_complete_name() == var_name:
                    self.contains_variable = True

        visitor = ContainsVariableVisitor()
        expr.accept(visitor)
        return visitor.contains_variable

    def _get_model_threshold_condition_block(self, astnode: ASTModel) -> ASTOnConditionBlock:
        for condition_block in astnode.get_on_condition_blocks():
            if self._expression_contains_variable(condition_block.cond_expr,
                                                  self.get_option("membrane_potential_variable")):
                return condition_block

        raise Exception("Could not find an onCondition block in the NESTML model \"" + astnode.name + "\" that contains the membrane potential variable \"" + self.get_option("membrane_potential_variable") + "\". Please check the GeNN code generator option \"membrane_potential_variable\"")

    def analyse_neuron(self, neuron: ASTModel) -> Tuple[Dict[str, ASTAssignment], Dict[str, ASTAssignment], List[ASTOdeEquation], List[ASTOdeEquation]]:
        # timestep symbol in GeNN is "dt" rather than "__h"
        neuron.add_to_internals_block(ModelParser.parse_declaration('dt ms = resolution()'), index=0)
        return super().analyse_neuron(neuron)
