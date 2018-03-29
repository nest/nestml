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

    def visitSimpleExpression(self, _expr=None):
        """
        Visit a simple expression and update the type of a numeric literal.
        :param _expr:
        :type _expr:
        :return:
        :rtype:
        """
        assert _expr.getScope() is not None, "Run symboltable creator."
        # if variable is also set in this expression, the var type overrides the literal
        if _expr.getVariable() is not None:
            scope = _expr.getScope()
            var_name = _expr.getVariable().getName()
            variable_symbol_resolve = scope.resolveToSymbol(var_name, SymbolKind.VARIABLE)
            _expr.setTypeEither(Either.value(variable_symbol_resolve.getTypeSymbol()))
            return

        if _expr.getNumericLiteral() is not None and isinstance(_expr.getNumericLiteral(), float):
            _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
            return

        elif _expr.getNumericLiteral() is not None and isinstance(_expr.getNumericLiteral(), int):
            _expr.setTypeEither(Either.value(PredefinedTypes.getIntegerType()))
            return
