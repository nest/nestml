# -*- coding: utf-8 -*-
#
# ast_mark_delay_vars_visitor.py
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
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTMarkDelayVarsVisitor(ASTVisitor):
    """
    A visitor that marks has_delay value in ASTExpression and ASTSimpleExpression nodes to True
    """
    def __init__(self):
        super(ASTMarkDelayVarsVisitor, self).__init__()

    def visit_expression(self, node: ASTExpression):
        node.has_delay = True

    def visit_simple_expression(self, node: ASTSimpleExpression):
        node.has_delay = True

    def visit_variable(self, node: ASTVariable):
        delay_variable_symbol = node.get_scope().resolve_to_symbol(node.get_complete_name(), SymbolKind.VARIABLE)
        if delay_variable_symbol is not None:
            delay_parameter = delay_variable_symbol.get_delay_parameter()
            if delay_parameter is not None:
                node.set_delay_parameter(delay_parameter)
