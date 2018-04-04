#
# ASTNumericLiteralVisitortor.py
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
simpleExpression : (INTEGER|FLOAT) (variable)?
"""
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either


class ASTNumericLiteralVisitor(ASTVisitor):
    """
    Visits a single numeric literal and updates its type.
    """

    def visit_simple_expression(self, node):
        """
        Visit a simple rhs and update the type of a numeric literal.
        :param node:
        :type node:
        :return:
        :rtype:
        """
        assert node.get_scope() is not None, "Run symboltable creator."
        # if variable is also set in this rhs, the var type overrides the literal
        if node.get_variable() is not None:
            scope = node.get_scope()
            var_name = node.get_variable().get_name()
            variable_symbol_resolve = scope.resolve_to_symbol(var_name, SymbolKind.VARIABLE)
            node.set_type_either(Either.value(variable_symbol_resolve.get_type_symbol()))
            return

        if node.get_numeric_literal() is not None and isinstance(node.get_numeric_literal(), float):
            node.set_type_either(Either.value(PredefinedTypes.get_real_type()))
            return

        elif node.get_numeric_literal() is not None and isinstance(node.get_numeric_literal(), int):
            node.set_type_either(Either.value(PredefinedTypes.get_integer_type()))
            return
