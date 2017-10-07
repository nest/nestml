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
from pynestml.nestml.Symbol import SymbolKind
from pynestml.nestml.TypeChecker import TypeChecker
from pynestml.nestml.ErrorStrings import ErrorStrings
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Either import Either


class FunctionCallVisitor(NESTMLVisitor):
    """
    Visits a single function call and updates its type.
    """

    def visitSimpleExpression(self, _expr=None):
        assert _expr.getScope() is not None, "Run symboltable creator."
        scope = _expr.getScope()
        functionName = _expr.getFunctionCall().getName()

        methodSymbol = scope.resolveToSymbol(functionName, SymbolKind.FUNCTION)

        if methodSymbol is None:
            errorMsg = ErrorStrings.messageResolveFail(self, functionName, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            return

        # convolve symbol does not have a return type set.
        # returns whatever type the second parameter is.
        if functionName == "convolve":
            # Deviations from the assumptions made here are handled in the convolveCoco
            bufferParameter = _expr.getFunctionCall().getArgs()[1]

            if bufferParameter.getVariable() is not None:
                bufferName = bufferParameter.getVariable().getName()
                bufferSymbolResolve = scope.resolve(bufferName, SymbolKind.VARIABLE)
                if bufferSymbolResolve is not None:
                    _expr.setTypeEither(Either.value(bufferSymbolResolve.getTypeSymbol()))
                    return

            # getting here means there is an error with the parameters to convolve
            errorMsg = ErrorStrings.messageCannotCalculateConvolveType(self, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            return

        if TypeChecker.isVoid(methodSymbol.getReturnType()):
            errorMsg = ErrorStrings.messageVoidFunctionOnRhs(self, functionName, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            return

        # if nothing special is handled, just get the expression type from the return type of the function
        _expr.setTypeEither(Either.value(methodSymbol.getReturnType()))
