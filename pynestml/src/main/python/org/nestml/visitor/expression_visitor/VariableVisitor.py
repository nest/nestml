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
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.Either import Either
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL,Logger


class VariableVisitor(NESTMLVisitor):

    def visitSimpleExpression(self, _expr=None):
        assert _expr.getScope() is not None, "Run symboltable creator."

        scope = _expr.getScope()

        varName = _expr.getVariable().getName()
        varResolve = scope.resolveToSymbol(varName, SymbolKind.VARIABLE)
        if varResolve is not None:
            _expr.setTypeEither(Either.value(varResolve.getTypeSymbol()))
        else:
            Logger.logMessage('Variable '+_expr.printAST() + ' could not be resolved!',LOGGING_LEVEL.ERROR)
            _expr.setTypeEither(Either.error('Variable could not be resolved!'))
        return

    def visitExpression(self, _expr=None):
        if _expr.isSimpleExpression():
            simpEx = _expr.getExpression()
            self.visitSimpleExpression(simpEx)
            _expr.setTypeEither(simpEx.getTypeEither())
        return
