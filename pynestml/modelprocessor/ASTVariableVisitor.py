#
# ASTVariableVisitortor.py
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
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import MessageCode


class ASTVariableVisitor(ASTVisitor):
    """
    This visitor visits a single variable and updates its type.
    """

    def visit_simple_expression(self, node=None):
        """
        Visits a single variable as contained in a simple rhs and derives its type.
        :param node: a single simple rhs
        :type node: ASTSimpleExpression
        """
        assert (node is not None and isinstance(node, ASTSimpleExpression)), \
            '(PyNestML.Visitor.ASTVariableVisitor) No or wrong type of simple rhs provided (%s)!' % type(node)
        assert (node.get_scope() is not None), \
            '(PyNestML.Visitor.ASTVariableVisitor) No scope found, run symboltable creator!'

        scope = node.get_scope()
        var_name = node.get_variable().get_name()
        var_resolve = scope.resolveToSymbol(var_name, SymbolKind.VARIABLE)
        # update the type of the variable according to its symbol type.
        if var_resolve is not None:
            node.set_type_either(Either.value(var_resolve.get_type_symbol()))
        else:
            message = 'Variable ' + str(node) + ' could not be resolved!'
            Logger.logMessage(_code=MessageCode.SYMBOL_NOT_RESOLVED,
                              _errorPosition=node.get_source_position(),
                              _message=message, _logLevel=LOGGING_LEVEL.ERROR)
            node.set_type_either(Either.error('Variable could not be resolved!'))
        return

    def visit_expression(self, node=None):
        raise Exception("Deprecated method used!")
