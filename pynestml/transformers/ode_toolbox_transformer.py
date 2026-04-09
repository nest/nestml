# -*- coding: utf-8 -*-
#
# ode_toolbox_transformer.py
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

from typing import Any, Dict, Iterable, Mapping, Optional, Set, Tuple

import odetoolbox

from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter
from pynestml.codegeneration.printers.ode_toolbox_function_call_printer import ODEToolboxFunctionCallPrinter
from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter
from pynestml.codegeneration.printers.sympy_simple_expression_printer import SympySimpleExpressionPrinter
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_kernel import ASTKernel

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.codegeneration.code_generator_utils import CodeGeneratorUtils
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.string_utils import removesuffix
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_visitor import ASTVisitor


class ODEToolboxTransformer(Transformer):
    r"""
    Run ODE-toolbox analysis on a model.

    Store the result in the model metadata with keys ``analytic_solver`` and ``numeric_solver``.

    Options
    -------

    - **preserve_expressions**: Set to True, or a list of strings corresponding to individual variable names, to disable internal rewriting of expressions, and return same output as input expression where possible. Only applies to variables specified as first-order differential equations. (This parameter is passed to ODE-toolbox.)
    - **simplify_expression**: For all expressions ``expr`` that are rewritten by ODE-toolbox: the contents of this parameter string are ``eval()``ed in Python to obtain the final output expression. Override for custom expression simplification steps. Example: ``sympy.simplify(expr)``. Default: ``"sympy.logcombine(sympy.powsimp(sympy.expand(expr)))"``. (This parameter is passed to ODE-toolbox.)
    - **solver**: A string identifying the preferred ODE solver. ``"analytic"`` for propagator solver preferred; fallback to numeric solver in case ODEs are not analytically solvable. Use ``"numeric"`` to disable analytic solver.
    """

    _default_options = {
        "preserve_expressions": True,
        "simplify_expression": "sympy.logcombine(sympy.powsimp(sympy.expand(expr)))",
        "solver": "analytic"
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

        # ODE-toolbox printers
        self._constant_printer = ConstantPrinter()
        self._ode_toolbox_variable_printer = ODEToolboxVariablePrinter(None)
        self._ode_toolbox_function_call_printer = ODEToolboxFunctionCallPrinter(None)
        self._ode_toolbox_printer = ODEToolboxExpressionPrinter(simple_expression_printer=SympySimpleExpressionPrinter(variable_printer=self._ode_toolbox_variable_printer,
                                                                                                                       constant_printer=self._constant_printer,
                                                                                                                       function_call_printer=self._ode_toolbox_function_call_printer))
        self._ode_toolbox_variable_printer._expression_printer = self._ode_toolbox_printer
        self._ode_toolbox_function_call_printer._expression_printer = self._ode_toolbox_printer

    def create_ode_toolbox_indict(self, neuron: ASTModel, kernel_buffers: Mapping[ASTKernel, ASTInputPort]):
        odetoolbox_indict = ASTUtils.transform_ode_and_kernels_to_json(neuron, neuron.get_parameters_blocks(), kernel_buffers, printer=self._ode_toolbox_printer)
        odetoolbox_indict["options"] = {}
        odetoolbox_indict["options"]["output_timestep_symbol"] = "__h"
        odetoolbox_indict["options"]["simplify_expression"] = self.get_option("simplify_expression")

        return odetoolbox_indict

    def ode_toolbox_analysis(self,
                             model: ASTModel,
                             kernel_buffers: Mapping[ASTKernel, ASTInputPort],
                             metadata: Dict[str, Dict[str, Any]]):
        """
        Prepare data for ODE-toolbox input format, invoke ODE-toolbox analysis via its API, and return the output.
        """
        assert len(model.get_equations_blocks()) <= 1, "Only one equations block supported for now."
        assert len(model.get_parameters_blocks()) <= 1, "Only one parameters block supported for now."

        equations_block = model.get_equations_blocks()[0]

        if len(equations_block.get_kernels()) == 0 and len(equations_block.get_ode_equations()) == 0:
            # no equations defined -> no changes to the model
            return None, None

        odetoolbox_indict = self.create_ode_toolbox_indict(model, kernel_buffers)

        odetoolbox_indict["options"]["simplify_expression"] = self.get_option("simplify_expression")
        disable_analytic_solver = self.get_option("solver") != "analytic"
        solver_result = odetoolbox.analysis(odetoolbox_indict,
                                            disable_stiffness_check=True,
                                            disable_analytic_solver=disable_analytic_solver,
                                            preserve_expressions=self.get_option("preserve_expressions"),
                                            log_level=FrontendConfiguration.logging_level)
        analytic_solver = None
        analytic_solvers = [x for x in solver_result if x["solver"] == "analytical"]
        assert len(analytic_solvers) <= 1, "More than one analytic solver not presently supported"
        if len(analytic_solvers) > 0:
            analytic_solver = analytic_solvers[0]

        # if numeric solver is required, generate a stepping function that includes each state variable, including the analytic ones
        numeric_solver = None
        numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]
        if numeric_solvers:
            if analytic_solver:
                # previous solver_result contains both analytic and numeric solver; re-run ODE-toolbox generating only numeric solver
                solver_result = odetoolbox.analysis(odetoolbox_indict,
                                                    disable_stiffness_check=True,
                                                    disable_analytic_solver=True,
                                                    preserve_expressions=self.get_option("preserve_expressions"),
                                                    log_level=FrontendConfiguration.logging_level)
            numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]
            assert len(numeric_solvers) <= 1, "More than one numeric solver not presently supported"
            if len(numeric_solvers) > 0:
                numeric_solver = numeric_solvers[0]

        if analytic_solver is not None:
            ASTUtils.add_declarations_to_internals(model, analytic_solver["propagators"])

        #
        #   save the results to metadata
        #

        if not model.name in metadata.keys():
            metadata[model.name] = {}

        metadata[model.name]["analytic_solver"] = analytic_solver
        metadata[model.name]["numeric_solver"] = numeric_solver

        return model

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Dict[str, Dict[str, Any]]) -> Iterable[ASTModel]:
        new_models = []

        for model in models:
            if len(model.get_equations_blocks()) == 0:
                # no equations, no need to call ODE-toolbox
                new_models.append(model)
                continue

            if len(model.get_equations_blocks()) > 1:
                raise Exception("Only one equations block per model supported for now")

            assert "kernel_buffers" in metadata[model.name].keys(), "ConvolutionsToBuffersTransformer should have been run first on the model!"

            new_model = self.ode_toolbox_analysis(model, metadata[model.name]["kernel_buffers"], metadata)
            new_models.append(new_model)

        return new_models
