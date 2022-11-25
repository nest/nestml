# -*- coding: utf-8 -*-
#
# nest_simple_expression_printer.py
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

from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression


class NESTSimpleExpressionPrinter(CppSimpleExpressionPrinter):
    r"""
    Printer for ASTSimpleExpressions in C++ syntax.
    """

    def _print(self, node: ASTSimpleExpression) -> str:
        if node.is_delay_variable():
            return self._variable_printer.print_delay_variable(node.get_variable())

        return super()._print(node)
