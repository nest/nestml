#
# ASTFunctionCallVisitortor.py
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
simpleExpression : functionCall
"""
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions


class ASTFunctionCallVisitor(ASTVisitor):
    """
    Visits a single function call and updates its type.
    """

    def visitSimpleExpression(self, _expr=None):
        """
        Visits a single function call as stored in a simple expression and derives the correct type of
         all its parameters.
        :param _expr: a simple expression
        :type _expr: ASTSimpleExpression
        :rtype void
        """
        assert (_expr is not None and isinstance(_expr, ASTSimpleExpression)), \
            '(PyNestML.Visitor.ASTFunctionCallVisitor) No or wrong type of simple expression provided (%s)!' % tuple(
                _expr)
        assert (_expr.getScope() is not None), \
            "(PyNestML.Visitor.ASTFunctionCallVisitor) No scope found, run symboltable creator!"
        scope = _expr.getScope()
        function_name = _expr.getFunctionCall().getName()
        method_symbol = scope.resolveToSymbol(function_name, SymbolKind.FUNCTION)
        # check if this function exists
        if method_symbol is None:
            error_msg = ErrorStrings.messageResolveFail(self, function_name, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(error_msg))
            return

        # convolve symbol does not have a return type set.
        # returns whatever type the second parameter is.
        if function_name == PredefinedFunctions.CONVOLVE:
            # Deviations from the assumptions made here are handled in the convolveCoco
            buffer_parameter = _expr.getFunctionCall().getArgs()[1]

            if buffer_parameter.getVariable() is not None:
                buffer_name = buffer_parameter.getVariable().getName()
                buffer_symbol_resolve = scope.resolveToSymbol(buffer_name, SymbolKind.VARIABLE)
                if buffer_symbol_resolve is not None:
                    _expr.setTypeEither(Either.value(buffer_symbol_resolve.getTypeSymbol()))
                    return

            # getting here means there is an error with the parameters to convolve
            error_msg = ErrorStrings.messageCannotCalculateConvolveType(self, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(error_msg))
            return

        if method_symbol.getReturnType().isVoid():
            error_msg = ErrorStrings.messageVoidFunctionOnRhs(self, function_name, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(error_msg))
            return

        # if nothing special is handled, just get the expression type from the return type of the function
        _expr.setTypeEither(Either.value(method_symbol.getReturnType()))
