# -*- coding: utf-8 -*-
#
# ast_variable_visitor.py
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
simpleExpression : variable
"""
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import MessageCode
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTVariableVisitor(ASTVisitor):
    """
    This visitor visits a single variable and updates its type.
    """

    def visit_simple_expression(self, node):
        """
        Visits a single variable as contained in a simple expression and derives its type.
        :param node: a single simple expression
        :type node: ASTSimpleExpression
        """
        assert isinstance(node, ASTSimpleExpression), \
            '(PyNestML.Visitor.VariableVisitor) No or wrong type of simple expression provided (%s)!' % type(node)
        assert (node.get_scope() is not None), \
            '(PyNestML.Visitor.VariableVisitor) No scope found, run symboltable creator!'

        scope = node.get_scope()
        var_name = node.get_variable().get_complete_name()
        var_resolve = scope.resolve_to_symbol(var_name, SymbolKind.VARIABLE)

        # update the type of the variable according to its symbol type.
        if var_resolve is not None:
            node.type = var_resolve.get_type_symbol()
            node.type.referenced_object = node
        else:
            # check if var_name is actually a type literal (e.g. "mV")
            var_resolve = scope.resolve_to_symbol(var_name, SymbolKind.TYPE)
            if var_resolve is not None:
                node.type = var_resolve
                node.type.referenced_object = node
            else:
                message = 'Variable ' + str(node) + ' could not be resolved!'
                Logger.log_message(code=MessageCode.SYMBOL_NOT_RESOLVED,
                                   error_position=node.get_source_position(),
                                   message=message, log_level=LoggingLevel.ERROR)
                node.type = ErrorTypeSymbol()
        return

    def visit_expression(self, node):
        raise Exception("Deprecated method used!")
