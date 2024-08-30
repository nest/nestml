# -*- coding: utf-8 -*-
#
# nestml_printer_units_as_factors.py
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

from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression


class NESTMLPrinterUnitsAsFactors(NESTMLPrinter):
    r"""
    Same as the NESTMLPrinter, except print unit literals with a multiplication operator between (for example "42 * ms" instead of "42 ms").
    """

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        if node.is_numeric_literal():
            if node.variable is not None:
                # numeric literal + physical unit
                return str(node.numeric_literal) + " * " + self.print(node.variable)

            return str(node.numeric_literal)

        return super(node)
