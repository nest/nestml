# -*- coding: utf-8 -*-
#
# chan_info_enricher.py
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

from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
import sympy

from pynestml.utils.mechs_info_enricher import MechsInfoEnricher


class ChanInfoEnricher(MechsInfoEnricher):
    """
    Class extends MechsInfoEnricher by the computation of the inline derivative. This hasn't been done in the
    channel processing because it would cause a circular dependency through the coco checks used by the ModelParser
    which we need to use.
    """

    def __init__(self, params):
        super(MechsInfoEnricher, self).__init__(params)

    @classmethod
    def enrich_mechanism_specific(cls, neuron, mechs_info):
        mechs_info = cls.compute_expression_derivative(mechs_info)
        return mechs_info

    @classmethod
    def compute_expression_derivative(cls, chan_info):
        for ion_channel_name, ion_channel_info in chan_info.items():
            inline_expression = chan_info[ion_channel_name]["root_expression"]
            expr_str = str(inline_expression.get_expression())
            sympy_expr = sympy.parsing.sympy_parser.parse_expr(expr_str)
            sympy_expr = sympy.diff(sympy_expr, "v_comp")

            ast_expression_d = ModelParser.parse_expression(str(sympy_expr))
            # copy scope of the original inline_expression into the the derivative
            ast_expression_d.update_scope(inline_expression.get_scope())
            ast_expression_d.accept(ASTSymbolTableVisitor())

            chan_info[ion_channel_name]["inline_derivative"] = ast_expression_d

        return chan_info
