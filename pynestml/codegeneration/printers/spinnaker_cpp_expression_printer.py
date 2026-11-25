# -*- coding: utf-8 -*-
#
# spinnaker_cpp_expression_printer.py
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

from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.codegeneration.printers.simple_expression_printer import SimpleExpressionPrinter
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.symbols.boolean_type_symbol import BooleanTypeSymbol
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel

class SpiNNakerCppExpressionPrinter(CppExpressionPrinter):
    r"""
    Printer for ``ASTExpression`` nodes in C++ syntax.

    Multiplication of fixed-point (``accum``, S16.15) numbers is printed according to ``fixed_point_multiplication``:

    - ``"gcc"``: the regular ``*`` operator. Note that GCC truncates the result (rounds towards minus infinity), which introduces a systematic bias.
    - ``"round_nearest"``: ``MULT_ROUND_NEAREST_ACCUM()`` from spinn_common's ``round.h`` (round to nearest).
    - ``"round_stochastic"``: ``MULT_ROUND_STOCHASTIC_ACCUM()`` from spinn_common's ``round.h`` (stochastic rounding; unbiased in expectation).

    Products of two integer- or boolean-typed operands are always printed with the regular ``*`` operator.
    """

    FIXED_POINT_MULTIPLICATION_MACROS = {"gcc": None,
                                         "round_nearest": "MULT_ROUND_NEAREST_ACCUM",
                                         "round_stochastic": "MULT_ROUND_STOCHASTIC_ACCUM"}

    def __init__(self, simple_expression_printer: SimpleExpressionPrinter, fixed_point_multiplication: str = "gcc"):
        super().__init__(simple_expression_printer=simple_expression_printer)
        if fixed_point_multiplication not in self.FIXED_POINT_MULTIPLICATION_MACROS.keys():
            raise ValueError("Unknown value for fixed_point_multiplication: \"" + str(fixed_point_multiplication) + "\"; should be one of: " + ", ".join(self.FIXED_POINT_MULTIPLICATION_MACROS.keys()))
        self._fixed_point_multiplication = fixed_point_multiplication

    @staticmethod
    def _is_integer_typed(node: ASTExpressionNode) -> bool:
        r"""Returns True if the expression is known to be integer- or boolean-typed; False if it is real-typed (or has a physical unit), or if its type could not be determined"""
        try:
            return isinstance(node.type, (IntegerTypeSymbol, BooleanTypeSymbol))
        except Exception:
            return False

    def _print_multiplication(self, node: ASTExpressionNode, lhs: str, rhs: str) -> str:
        macro = self.FIXED_POINT_MULTIPLICATION_MACROS[self._fixed_point_multiplication]
        if macro is None or (self._is_integer_typed(node.get_lhs()) and self._is_integer_typed(node.get_rhs())):
            return lhs + " * " + rhs

        # the rounding macros from round.h call __builtin_trap() at runtime if the operand types are not both accum (s1615), so cast explicitly
        return macro + "((accum) (" + lhs + "), (accum) (" + rhs + "))"

    def print_compound_product(self, node: ASTAssignment) -> str:
        r"""Print a compound product assignment (``x *= expr``), using the same multiplication method as for binary ``*`` expressions"""
        assert node.is_compound_product
        variable = self.print(node.get_variable())
        expr = self.print(node.get_expression())
        macro = self.FIXED_POINT_MULTIPLICATION_MACROS[self._fixed_point_multiplication]

        variable_is_integer_typed = False
        try:
            symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(), SymbolKind.VARIABLE)
            variable_is_integer_typed = isinstance(symbol.get_type_symbol(), (IntegerTypeSymbol, BooleanTypeSymbol))
        except Exception:
            pass

        if macro is None or (variable_is_integer_typed and self._is_integer_typed(node.get_expression())):
            return variable + " *= " + expr

        return variable + " = " + macro + "((accum) (" + variable + "), (accum) (" + expr + "))"

    def _print_arithmetic_operator_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints an arithmetic operator.
        :param node: an expression with arithmetic operator
        :return: a string representation
        """
        op = node.get_binary_operator()
        lhs = self.print(node.get_lhs())
        rhs = self.print(node.get_rhs())

        if op.is_pow_op:
            # TODO: make a dummy ASTFunctionCall so we can delegate this to the FunctionCallPrinter
            return "(expk(" + rhs + " * logk(" + lhs + ")))"

        if op.is_plus_op:
            return lhs + " + " + rhs

        if op.is_minus_op:
            return lhs + " - " + rhs

        if op.is_times_op:
            return self._print_multiplication(node, lhs, rhs)

        if op.is_div_op:
            Logger.log_message(None, None, "SpiNNaker does not feature an FPU so division is not implemented on this platform", None, LoggingLevel.WARNING)
            return "_kdivk(" + lhs + ", " + rhs + ")"

        if op.is_modulo_op:
            return lhs + " % " + rhs

        raise RuntimeError("Cannot determine arithmetic operator!")
