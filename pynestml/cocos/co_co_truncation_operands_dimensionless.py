# -*- coding: utf-8 -*-
#
# co_co_truncation_operands_dimensionless.py
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

from typing import Any, Dict, Optional

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_quantities import PredefinedQuantities
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.type_symbol import TypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoTruncationOperandsDimensionless(CoCo):
    r"""
    This coco ensures that values are only truncated or rounded to an integer if they are dimensionless. This applies to integer division (``//`` and ``//=``) and to the functions ``floor()``, ``ceil()`` and ``round()``.

    The truncation of a physical value depends on the unit in which it is expressed. As NESTML models are typed by physical quantity, these units are chosen by the target platform: for instance, a voltage is stored in mV for NEST, but in V for the Python-standalone target. Truncating 500 mV gives 500 mV, but truncating the same voltage expressed as 0.5 V gives 0 V.

    For integer division ``a // b``, the quotient ``a / b`` has to be dimensionless; the operands may have a physical dimension, as long as it is the same for both. The result is of type ``integer``. As ``a //= b`` is equivalent to ``a = a // b``, both ``a`` and ``b`` have to be dimensionless.

    Allowed:

    .. code-block:: nestml

       n integer = t // resolution()           # number of time steps in the interval t
       n //= 3
       V_m = (V_m // 1 mV) * 1 mV              # truncate to an explicitly specified resolution of 1 mV
       x = floor(V_m / 1 mV)

    Not allowed:

    .. code-block:: nestml

       V_m = V_m // 2                          # the quotient is a voltage
       V_m //= 2
       x "voltage" = floor(V_m)
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Ensures the coco for the handed over model.
        :param node: a single model instance.
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"

        node.accept(TruncationOperandsDimensionlessVisitor())


class TruncationOperandsDimensionlessVisitor(ASTVisitor):
    r"""
    Visits integer divisions and calls to rounding functions and checks that the truncated values are dimensionless.
    """

    ROUNDING_FUNCTIONS = [PredefinedFunctions.FLOOR, PredefinedFunctions.CEIL, PredefinedFunctions.ROUND]

    def visit_expression(self, node: ASTExpression):
        if node.get_binary_operator() is None or not getattr(node.get_binary_operator(), "is_integer_div_op", False):
            return

        # the type of ``a // b`` is the type of the quotient ``a / b`` if the latter is not dimensionless (see ASTDotOperatorVisitor)
        if isinstance(node.type, UnitTypeSymbol):
            self._log_error("Integer division \"//\"", "the quotient", node.type, node)

    def visit_assignment(self, node: ASTAssignment):
        if not node.is_compound_integer_quotient:
            return

        lhs_symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(), SymbolKind.VARIABLE)
        if lhs_symbol is not None and isinstance(lhs_symbol.get_type_symbol(), UnitTypeSymbol):
            self._log_error("Integer division \"//=\"", "the variable \"" + node.get_variable().get_complete_name() + "\"", lhs_symbol.get_type_symbol(), node)
            return

        if isinstance(node.get_expression().type, UnitTypeSymbol):
            self._log_error("Integer division \"//=\"", "the divisor", node.get_expression().type, node)

    def visit_function_call(self, node: ASTFunctionCall):
        if node.get_name() not in self.ROUNDING_FUNCTIONS:
            return

        for arg in node.get_args():
            if isinstance(arg.type, UnitTypeSymbol):
                self._log_error("Function \"" + node.get_name() + "()\"", "the argument", arg.type, node)

    @staticmethod
    def _log_error(operation: str, what: str, type_symbol: TypeSymbol, node: ASTNode) -> None:
        code, message = Messages.get_truncation_of_physical_quantity(operation, what, TruncationOperandsDimensionlessVisitor._print_quantity(type_symbol))
        Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)

    @staticmethod
    def _print_quantity(type_symbol: UnitTypeSymbol) -> str:
        r"""Return the name of the physical quantity (for instance, "voltage") if it is known, and the unit otherwise."""
        for name in PredefinedQuantities.get_quantity_names():
            unit = PredefinedQuantities.get_unit(name)
            if unit is not None and unit.is_equivalent(type_symbol.astropy_unit):
                return "\"" + name + "\""

        return "\"" + str(type_symbol.astropy_unit.decompose()) + "\""
