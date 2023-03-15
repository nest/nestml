# -*- coding: utf-8 -*-
#
# ast_numeric_literal_visitor.py
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

"""
simpleExpression : (UNSIGNED_INTEGER | FLOAT) (variable)?
"""
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.symbol import SymbolKind
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTNumericLiteralVisitor(ASTVisitor):
    """
    Visits a single numeric literal and updates its type.
    """

    def visit_simple_expression(self, node):
        """
        Visit a simple rhs and update the type of a numeric literal.
        :param node: a single meta_model node
        :type node: ast_node
        :return: no value returned, the type is updated in-place
        :rtype: void
        """
        assert node.get_scope() is not None, "Run symboltable creator."
        # if variable is also set in this rhs, the var type overrides the literal
        if node.get_variable() is not None:
            scope = node.get_scope()
            var_name = node.get_variable().get_name()
            variable_symbol_resolve = scope.resolve_to_symbol(var_name, SymbolKind.VARIABLE)
            if variable_symbol_resolve is not None:
                node.type = variable_symbol_resolve.get_type_symbol()
            else:
                type_symbol_resolve = scope.resolve_to_symbol(var_name, SymbolKind.TYPE)
                if type_symbol_resolve is not None:
                    node.type = type_symbol_resolve
                else:
                    node.type = ErrorTypeSymbol()
            node.type.referenced_object = node
            return

        if node.get_numeric_literal() is not None and isinstance(node.get_numeric_literal(), float):
            node.type = PredefinedTypes.get_real_type()
            node.type.referenced_object = node
            return

        elif node.get_numeric_literal() is not None and isinstance(node.get_numeric_literal(), int):
            node.type = PredefinedTypes.get_integer_type()
            node.type.referenced_object = node
            return
