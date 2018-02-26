#
# VariableVisitor.py
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
from copy import copy

from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import MessageCode


class VariableVisitor(NESTMLVisitor):
    """
    This visitor visits a single variable and updates its type.
    """

    def visit_simple_expression(self, _expr=None):
        """
        Visits a single variable as contained in a simple expression and derives its type.
        :param _expr: a single simple expression
        :type _expr: ASTSimpleExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTSimpleExpression)), \
            '(PyNestML.Visitor.VariableVisitor) No or wrong type of simple expression provided (%s)!' % type(_expr)
        assert (_expr.getScope() is not None), \
            '(PyNestML.Visitor.VariableVisitor) No scope found, run symboltable creator!'

        scope = _expr.getScope()
        varName = _expr.getVariable().getName()
        varResolve = scope.resolveToSymbol(varName, SymbolKind.VARIABLE)

        # update the type of the variable according to its symbol type.
        if varResolve is not None:
            _expr.type = varResolve.getTypeSymbol()
            _expr.type.referenced_object = _expr
        else:
            message = 'Variable ' + str(_expr) + ' could not be resolved!'
            Logger.logMessage(_code=MessageCode.SYMBOL_NOT_RESOLVED,
                              _errorPosition=_expr.getSourcePosition(),
                              _message=message, _logLevel=LOGGING_LEVEL.ERROR)
            _expr.type = ErrorTypeSymbol()
        return

    def visit_expression(self, _expr=None):
        raise Exception("Deprecated method used!")
