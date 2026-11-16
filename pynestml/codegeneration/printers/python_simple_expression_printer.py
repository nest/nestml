# -*- coding: utf-8 -*-
#
# python_simple_expression_printer.py
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

from typing import Type

from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.function_call_printer import FunctionCallPrinter
from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.codegeneration.unit_converter import UnitConverter
from pynestml.codegeneration.printers.simple_expression_printer import SimpleExpressionPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable


class PythonSimpleExpressionPrinter(SimpleExpressionPrinter):
    r"""
    Printer for ASTSimpleExpressions in Python syntax.

    Physical units in literals are converted to the preferred units of the target platform, as given by the ``unit_converter``.
    """

    def __init__(self,
                 variable_printer: VariablePrinter,
                 constant_printer: ConstantPrinter,
                 function_call_printer: FunctionCallPrinter,
                 unit_converter: Type[UnitConverter] = NESTUnitConverter):
        super().__init__(variable_printer=variable_printer, constant_printer=constant_printer, function_call_printer=function_call_printer)
        self._unit_converter = unit_converter

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        if node.is_numeric_literal_with_unit():
            # e.g. "-70 mV": convert to the preferred unit of the target platform
            return self._constant_printer.print_constant(self._unit_converter.get_factor_of_unit_type(node.unitType) * node.get_numeric_literal())

        if isinstance(node, ASTVariable):
            return self._variable_printer.print(node.get_variable())

        if node.is_numeric_literal():
            return str(node.get_numeric_literal())

        if node.is_inf_literal:
            return "float(\"inf\")"

        if node.is_string():
            return str(node.get_string())

        if node.is_boolean_true:
            return "True"

        if node.is_boolean_false:
            return "False"

        if node.is_variable() or node.is_delay_variable():
            return self._variable_printer.print(node.get_variable())

        if node.is_function_call():
            return self._function_call_printer.print_function_call(node.get_function_call())

        raise Exception("Unknown node type: " + str(node))

    def _print(self, node: ASTNode) -> str:
        if isinstance(node, ASTVariable):
            return self._variable_printer.print(node)

        if isinstance(node, ASTFunctionCall):
            return self._function_call_printer.print(node)

        return self.print_simple_expression(node)

    def print(self, node: ASTNode) -> str:
        return self._print(node)
