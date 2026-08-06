# -*- coding: utf-8 -*-
#
# convolutions_to_buffers_transformer.py
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

from typing import Any, Dict, Iterable, List, Optional, Mapping, Set, Tuple, Union

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

import sympy

from pynestml.codegeneration.printers.nestml_simple_expression_printer_units_as_factors import NESTMLSimpleExpressionPrinterUnitsAsFactors
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.transformers.transformer import Transformer
from pynestml.utils.ast_utils import ASTUtils
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor


class ConvolutionsToBuffersTransformer(Transformer):
    r"""
    Replace all occurrences of `convolve(kernel[']^n, spike_input_port)` with the corresponding buffer variable, e.g. `g_E__X__spikes_exc[__d]^n` for a kernel named `g_E` and a spike input port named `spikes_exc`. Replaces all occurrences of ``spike_input_port`` outside of convolutions with 0 because it corresponds to a delta function-like increment. Similarly, convolutions with delta kernels are replaced with a value of 0.

    Store metadata pertaining to which buffer variables are needed (with key ``kernel_buffers``) and metadata pertaining to increments due to delta kernels (with key ``delta_factors``).
    """

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(Transformer, self).__init__(options)

    def generate_kernel_buffers(self, model: ASTModel) -> Set[Tuple[ASTKernel, ASTInputPort]]:
        """
        For every occurrence of a convolution of the form `convolve(var, spike_buf)`: add the element `(kernel, spike_buf)` to the set, with `kernel` being the kernel that contains variable `var`.
        """

        kernel_buffers = set()
        for equations_block in model.get_equations_blocks():
            convolve_calls = ASTUtils.get_convolve_function_calls(equations_block)
            for convolve in convolve_calls:
                el = (convolve.get_args()[0], convolve.get_args()[1])
                sym = convolve.get_args()[0].get_scope().resolve_to_symbol(convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
                if sym is None:
                    raise Exception("No initial value(s) defined for kernel with variable \"" + convolve.get_args()[0].get_variable().get_complete_name() + "\"")

                if sym.block_type == BlockType.INPUT:
                    # swap the order
                    el = (el[1], el[0])

                # find the corresponding kernel object
                var = el[0].get_variable()
                assert var is not None
                kernel = model.get_kernel_by_name(var.get_name())
                assert kernel is not None, "In convolution \"convolve(" + str(var.name) + ", " + str(el[1]) + ")\": no kernel by name \"" + var.get_name() + "\" found in model."

                el = (kernel, el[1])

                # make sure no duplicates are added -- expressions should be compared as strings
                el_exists = False
                for _el in kernel_buffers:
                    if el[0] == _el[0] and str(el[1]) == str(_el[1]):
                        el_exists = True
                        break

                if not el_exists:
                    kernel_buffers.add(el)

        return kernel_buffers

    def get_delta_factors_from_convolutions(self, model: ASTModel) -> dict:
        r"""
        For every occurrence of a convolution of the form `x^(n) = a * convolve(kernel, inport) + ...` where `kernel` is a delta function, add the element `(x^(n), inport) --> a` to the set.
        """
        delta_factors = {}

        for equations_block in model.get_equations_blocks():
            for ode_eq in equations_block.get_ode_equations():
                var = ode_eq.get_lhs()
                expr = ode_eq.get_rhs()
                conv_calls = ASTUtils.get_convolve_function_calls(expr)
                for conv_call in conv_calls:
                    assert len(conv_call.args) == 2, "convolve() function call should have precisely two arguments: kernel and spike input port"
                    kernel_name = conv_call.args[0].get_variable().get_name()
                    kernel = model.get_kernel_by_name(kernel_name)
                    assert kernel
                    if ASTUtils.is_delta_kernel(kernel):
                        inport = conv_call.args[1].get_variable()
                        factor_str = self.get_factor_str_from_expr_and_inport(expr, str(conv_call))
                        assert factor_str
                        delta_factors[(var, inport)] = factor_str

        return delta_factors

    def get_delta_factors_from_input_port_references(self, model: ASTModel) -> dict:
        r"""
        For every occurrence of a convolution of the form ``x^(n) = a * inport + ...``, add the element `(x^(n), inport) --> a` to the set.
        """
        delta_factors = {}

        spike_inports = model.get_spike_input_ports()
        for equations_block in model.get_equations_blocks():
            for ode_eq in equations_block.get_ode_equations():
                var = ode_eq.get_lhs()
                expr = ode_eq.get_rhs()

                for inport_sym in spike_inports:
                    inport_var = ASTNodeFactory.create_ast_variable(inport_sym.name)
                    inport_var.update_scope(equations_block.get_scope())

                    factor_str = self.get_factor_str_from_expr_and_inport(expr, inport_var.name)

                    if factor_str:
                        delta_factors[(var, inport_var)] = factor_str

                    # XXX: what about vectors?

        return delta_factors

    def get_factor_str_from_expr_and_inport(self, expr, sub_expr):
        r"""
        Use ``sympy.coeff()`` to extract the factor ``a`` with which ``sub_expr`` appears in ``expr = ... + a * sub_expr + ...``. Using sympy means that this should also work with more complex, nested expressions.
        """

        from sympy import sympify

        from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
        from pynestml.codegeneration.printers.nestml_function_call_printer import NESTMLFunctionCallPrinter
        from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter
        from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter
        from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter

        printer = NESTMLPrinter()
        printer._expression_printer = ODEToolboxExpressionPrinter(simple_expression_printer=None)
        printer._constant_printer = ConstantPrinter()
        printer._function_call_printer = NESTMLFunctionCallPrinter(expression_printer=printer._expression_printer)
        printer._variable_printer = ODEToolboxVariablePrinter(expression_printer=printer._expression_printer)
        printer._simple_expression_printer = NESTMLSimpleExpressionPrinterUnitsAsFactors(variable_printer=printer._variable_printer, function_call_printer=printer._function_call_printer, constant_printer=printer._constant_printer)
        printer._expression_printer._simple_expression_printer = printer._simple_expression_printer

        expr_str = printer.print(expr)

        root_node = expr
        while not isinstance(root_node, ASTModel):
            root_node = root_node.get_parent()

        all_variable_symbols = root_node.get_parameter_symbols() + root_node.get_state_symbols() + root_node.get_internal_symbols()
        all_variable_symbols_dict = {s.name: sympy.Symbol(s.name) for s in all_variable_symbols}

        # pretend that physical units are variables
        unit_vars_str = PredefinedUnits.get_units().keys()
        all_variable_symbols_dict |= {s: sympy.Symbol(s) for s in unit_vars_str}

        sympy_expr = sympify(expr_str, locals=all_variable_symbols_dict)  # minimal dict to make no assumptions (e.g. "beta" could otherwise be recognised as a function instead of as a parameter symbol)
        sympy_expr = sympy.expand(sympy_expr)
        sympy_sub_expr = sympy.parsing.sympy_parser.parse_expr(sub_expr)
        factor_str = []
        for term in sympy.Add.make_args(sympy_expr):
            coeff = term.coeff(sympy_sub_expr)
            if coeff:
                factor_str.append(str(coeff))

        factor_str = " + ".join(factor_str)

        return factor_str

    def _transform_model(self, model: ASTModel, equations_block: ASTEquationsBlock) -> None:
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

        def replace_function_call_through_var(_expr: ASTSimpleExpression):
            if _expr.is_function_call() and _expr.get_function_call().get_name() == PredefinedFunctions.CONVOLVE:
                convolve = _expr.get_function_call()
                el = (convolve.get_args()[0], convolve.get_args()[1])
                sym = convolve.get_args()[0].get_scope().resolve_to_symbol(convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
                if sym.block_type == BlockType.INPUT:
                    # swap elements
                    el = (el[1], el[0])
                var = el[0].get_variable()
                spike_input_port = el[1].get_variable()
                kernel = model.get_kernel_by_name(var.get_name())

                _expr.set_function_call(None)
                buffer_var = ASTUtils.construct_kernel_X_spike_buf_name(
                    var.get_name(), spike_input_port, var.get_differential_order() - 1)
                if ASTUtils.is_delta_kernel(kernel):
                    # delta kernels are treated separately, and should be kept out of the dynamics (computing derivates etc.) --> set to zero
                    _expr.set_variable(None)
                    _expr.set_numeric_literal(0)
                else:
                    ast_variable = ASTVariable(buffer_var)
                    ast_variable.set_source_position(_expr.get_source_position())
                    _expr.set_variable(ast_variable)

        def func_replace_function_call_through_var(x):
            return replace_function_call_through_var(x) if isinstance(x, ASTSimpleExpression) else True

        def replace_spiking_input_port_with_zero(_expr=None):
            if _expr.get_variable():
                port = ASTUtils.get_input_port_by_name(model.get_input_blocks(), _expr.get_variable().name)
                if port and port.is_spike():
                    # the spiking input port appears directly in the ODE -- this is equivalent to convolving with a delta kernel. Updates due to this term will be handled in ``delta_factors``
                    _expr.set_variable(None)
                    _expr.set_numeric_literal(0)

        def func_replace_spiking_input_port_with_zero(x):
            return replace_spiking_input_port_with_zero(x) if isinstance(x, ASTSimpleExpression) else True

        equations_block.accept(ASTHigherOrderVisitor(func_replace_function_call_through_var))
        equations_block.accept(ASTHigherOrderVisitor(func_replace_spiking_input_port_with_zero))
        equations_block.accept(ASTSymbolTableVisitor())

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Dict[str, Dict[str, Any]]) -> Iterable[ASTModel]:
        for model in models:
            if not model.get_equations_blocks():
                continue

            if len(model.get_equations_blocks()) > 1:
                raise Exception("Only one equations block per model supported for now")

            equations_block = model.get_equations_blocks()[0]

            if not model.name in metadata.keys():
                metadata[model.name] = {}

            metadata[model.name]["kernel_buffers"] = self.generate_kernel_buffers(model)
            metadata[model.name]["delta_factors"] = self.get_delta_factors_from_input_port_references(model)
            metadata[model.name]["delta_factors"] |= self.get_delta_factors_from_convolutions(model)

            self._transform_model(model, equations_block)

        return models
