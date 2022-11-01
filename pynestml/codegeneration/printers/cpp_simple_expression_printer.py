# -*- coding: utf-8 -*-
#
# cpp_simple_expression_printer.py
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

from typing import Optional, Tuple

import re

from pynestml.codegeneration.printers.simple_expression_printer import SimpleExpressionPrinter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbol_table.scope import Scope
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable


class CppSimpleExpressionPrinter(SimpleExpressionPrinter):
    r"""
    Printer for ASTSimpleExpressions in C++ syntax.
    """

    def print_simple_expression(self, node: ASTSimpleExpression, prefix: str = "") -> str:
        if node.has_unit():
            return str(node.get_numeric_literal()) + " * " + \
                self._variable_printer.print_variable(node.get_variable(), prefix=prefix)

        if node.is_numeric_literal():
            return str(node.get_numeric_literal())

        if node.is_inf_literal:
            return 'std::numeric_limits< double_t >::infinity()'

        if node.is_string():
            return str(node.get_string())

        if node.is_boolean_true:
            return 'true'

        if node.is_boolean_false:
            return 'false'

        if node.is_variable() or node.is_delay_variable():
            return self._variable_printer.print_variable(node.get_variable(), prefix=prefix)

        if node.is_function_call():
            return self._function_call_printer.print_function_call(node.get_function_call(), prefix=prefix)

        raise Exception("Unknown node type: " + str(node))


    def print(self, node: ASTNode, prefix: str = "") -> str:
        assert isinstance(node, ASTSimpleExpression)

        return self.print_simple_expression(node, prefix=prefix)
