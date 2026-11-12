# -*- coding: utf-8 -*-
#
# unit_conversion_transformer.py
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

from typing import Any, Dict, Iterable, Mapping, Optional, Type

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.codegeneration.unit_converter import UnitConverter
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.symbol import SymbolKind
from pynestml.transformers.transformer import Transformer
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor


class UnitConversionTransformer(Transformer):
    r"""
    Convert all physical units in expressions into plain numbers, in the preferred units of the target platform.

    In a NESTML model, physical units appear in expressions as part of numeric literals, such as ``-70 mV`` or ``10 ms``. The generated code stores all physical values as plain numbers, in a fixed set of preferred units of the target platform (for instance, mV, ms and pA for NEST, or V, s and A for the Python-standalone target), as defined by the target's ``UnitConverter``. This transformer replaces each literal with a unit by the corresponding plain number in the preferred unit of the same physical dimension: for NEST, ``-70 mV`` becomes ``-70.`` and ``1 V`` becomes ``1000.``; for the Python-standalone target, ``-70 mV`` becomes ``-0.07``.

    This includes the units of continuous input ports that were made explicit when the model was parsed (``(I_stim * 1 pA)``; see ``InsertContinuousInputPortUnitsVisitor``), and units that appear on their own in an expression (as a factor, for instance ``ms`` in ``t / ms``).

    The data types of declarations (such as ``"voltage"``) and of continuous input ports (such as ``pA``) are not changed: they describe the types of variables, not values.

    This transformer runs just before the ``ODEToolboxTransformer``, so that ODE-toolbox (and all subsequent processing, such as printing the generated code) only sees plain numbers in the preferred units of the target platform. The results returned by ODE-toolbox, which are inserted into the model as plain numbers, are thus in the same system of units as the rest of the model.
    """

    def __init__(self, options: Optional[Mapping[str, Any]] = None, unit_converter: Type[UnitConverter] = NESTUnitConverter):
        r"""
        :param options: transformer options (none are currently supported)
        :param unit_converter: the system of physical units of the target platform
        """
        super(Transformer, self).__init__(options)
        self._unit_converter = unit_converter

    @override
    def transform(self,
                  models: Iterable[ASTModel],
                  metadata: Dict[str, Dict[str, Any]]) -> Iterable[ASTModel]:
        for model in models:
            self.convert_units(model)

        return models

    def convert_units(self, model: ASTModel) -> None:
        r"""
        Replace all numeric literals with physical units in ``model`` by plain numbers in the preferred units of the target platform.
        """
        def convert(node):
            if isinstance(node, ASTSimpleExpression):
                self._convert_simple_expression(node)

        model.accept(ASTHigherOrderVisitor(visit_funcs=convert))

        # the types of expressions are cached; they are now outdated, as literals no longer have physical units
        def reset_type(node):
            if isinstance(node, ASTExpressionNode):
                node.type = None

        model.accept(ASTHigherOrderVisitor(visit_funcs=reset_type))

    def _convert_simple_expression(self, node: ASTSimpleExpression) -> None:
        if node.is_numeric_literal_with_unit():
            # e.g. "-70 mV"
            node.numeric_literal = self._round(self._unit_converter.get_factor_of_unit_type(node.unitType) * node.get_numeric_literal())
            node.unitType = None
            return

        if node.is_variable() and node.get_scope() is not None \
                and node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(), SymbolKind.VARIABLE) is None \
                and PredefinedUnits.is_unit(node.get_variable().get_complete_name()):
            # a physical unit that appears on its own in an expression, e.g. "ms" in ``t / ms``
            node.numeric_literal = self._round(self._unit_converter.get_factor(PredefinedUnits.get_unit(node.get_variable().get_complete_name()).get_unit()))
            node.variable = None

    @staticmethod
    def _round(value: float) -> float:
        r"""Remove floating-point noise from the product of a literal and a conversion factor (e.g. 3.0000000000000004e-08 for 30 nS in S)."""
        return float("%.15g" % value)
