#
# FunctionCallVisitor.py
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
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.VoidTypeSymbol import VoidTypeSymbol


class FunctionCallVisitor(NESTMLVisitor):
    """
    Visits a single function call and updates its type.
    """

    def visit_simple_expression(self, _expr=None):
        """
        Visits a single function call as stored in a simple expression and derives the correct type of all its parameters.
        :param _expr: a simple expression
        :type _expr: ASTSimpleExpression
        :rtype void
        """
        assert (_expr is not None and isinstance(_expr, ASTSimpleExpression)), \
            '(PyNestML.Visitor.FunctionCallVisitor) No or wrong type of simple expression provided (%s)!' % tuple(_expr)
        assert (_expr.getScope() is not None), \
            "(PyNestML.Visitor.FunctionCallVisitor) No scope found, run symboltable creator!"
        scope = _expr.getScope()
        functionName = _expr.getFunctionCall().getName()
        methodSymbol = scope.resolveToSymbol(functionName, SymbolKind.FUNCTION)
        # check if this function exists
        if methodSymbol is None:
            errorMsg = ErrorStrings.messageResolveFail(self, functionName, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            return

        # convolve symbol does not have a return type set.
        # returns whatever type the second parameter is.
        if functionName == PredefinedFunctions.CONVOLVE:
            # Deviations from the assumptions made here are handled in the convolveCoco
            bufferParameter = _expr.getFunctionCall().getArgs()[1]

            if bufferParameter.getVariable() is not None:
                bufferName = bufferParameter.getVariable().getName()
                bufferSymbolResolve = scope.resolveToSymbol(bufferName, SymbolKind.VARIABLE)
                if bufferSymbolResolve is not None:
                    _expr.setTypeEither(Either.value(bufferSymbolResolve.getTypeSymbol()))
                    return

            # getting here means there is an error with the parameters to convolve
            errorMsg = ErrorStrings.messageCannotCalculateConvolveType(self, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            return

        if isinstance(methodSymbol.getReturnType(),VoidTypeSymbol):
            errorMsg = ErrorStrings.messageVoidFunctionOnRhs(self, functionName, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            return

        # if nothing special is handled, just get the expression type from the return type of the function
        _expr.setTypeEither(Either.value(methodSymbol.getReturnType()))
