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
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.VoidTypeSymbol import VoidTypeSymbol
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class FunctionCallVisitor(NESTMLVisitor):
    """
    Visits a single function call and updates its type.
    """

    def visit_simple_expression(self, _expr=None):
        """
        Visits a single function call as stored in a simple expression and derives the correct type of all its
        parameters. :param _expr: a simple expression :type _expr: ASTSimpleExpression :rtype void
        """
        assert (_expr is not None and isinstance(_expr, ASTSimpleExpression)), \
            '(PyNestML.Visitor.FunctionCallVisitor) No or wrong type of simple expression provided (%s)!' % tuple(_expr)
        assert (_expr.getScope() is not None), \
            "(PyNestML.Visitor.FunctionCallVisitor) No scope found, run symboltable creator!"
        scope = _expr.getScope()
        function_name = _expr.getFunctionCall().getName()
        method_symbol = scope.resolveToSymbol(function_name, SymbolKind.FUNCTION)
        # check if this function exists
        if method_symbol is None:
            code, message = Messages.getCouldNotResolve(function_name)
            Logger.logMessage(_code=code, _message=message, _errorPosition=_expr.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
            _expr.type = ErrorTypeSymbol()
            return
        return_type = method_symbol.getReturnType()
        return_type.referenced_object = _expr

        # convolve symbol does not have a return type set.
        # returns whatever type the second parameter is.
        if function_name == PredefinedFunctions.CONVOLVE:
            # Deviations from the assumptions made here are handled in the convolveCoco
            buffer_parameter = _expr.getFunctionCall().getArgs()[1]

            if buffer_parameter.getVariable() is not None:
                buffer_name = buffer_parameter.getVariable().getName()
                buffer_symbol_resolve = scope.resolveToSymbol(buffer_name, SymbolKind.VARIABLE)
                if buffer_symbol_resolve is not None:
                    _expr.type = buffer_symbol_resolve.getTypeSymbol()
                    return

            # getting here means there is an error with the parameters to convolve
            code, message = Messages.get_convolve_needs_buffer_parameter()
            Logger.logMessage(_code=code, _message=message, _errorPosition=_expr.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
            _expr.type = ErrorTypeSymbol()
            return

        if isinstance(method_symbol.getReturnType(), VoidTypeSymbol):
            error_msg = ErrorStrings.messageVoidFunctionOnRhs(self, function_name, _expr.getSourcePosition())
            _expr.type = ErrorTypeSymbol()
            return

        # if nothing special is handled, just get the expression type from the return type of the function
        _expr.type = return_type
