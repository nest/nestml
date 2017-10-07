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
simpleexpression : variable
"""
from pynestml.nestml.Symbol import SymbolKind
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Either import Either
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import MessageCode


class VariableVisitor(NESTMLVisitor):
    def visitSimpleExpression(self, _expr=None):
        assert _expr.getScope() is not None, "Run symboltable creator."

        scope = _expr.getScope()

        varName = _expr.getVariable().getName()
        varResolve = scope.resolveToSymbol(varName, SymbolKind.VARIABLE)
        if varResolve is not None:
            _expr.setTypeEither(Either.value(varResolve.getTypeSymbol()))
        else:
            message = 'Variable ' + _expr.printAST() + ' could not be resolved!'
            Logger.logMessage(_code=MessageCode.SYMBOL_NOT_RESOLVED,
                              _errorPosition=_expr.getSourcePosition(),
                              _message=message, _logLevel=LOGGING_LEVEL.ERROR)
            _expr.setTypeEither(Either.error('Variable could not be resolved!'))
        return

    def visitExpression(self, _expr=None):
        if _expr.isSimpleExpression():
            simpEx = _expr.getExpression()
            self.visitSimpleExpression(simpEx)
            _expr.setTypeEither(simpEx.getTypeEither())
        return
