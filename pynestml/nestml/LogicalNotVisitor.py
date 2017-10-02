#
# LogicalNotVisitor.py
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
expression: logicalNot='not' term=expression
"""
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.TypeChecker import TypeChecker
from pynestml.nestml.ErrorStrings import ErrorStrings
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class LogicalNotVisitor(NESTMLVisitor):
    def visitExpression(self, _expr=None):
        exprTypeE = _expr.getExpression().getTypeEither()

        if exprTypeE.isError():
            _expr.setTypeEither(exprTypeE)
            return

        exprType = exprTypeE.getValue()

        if TypeChecker.isBoolean(exprType):
            _expr.setTypeEither(Either.value(PredefinedTypes.getBooleanType()))
        else:
            errorMsg = ErrorStrings.messageExpectedBool(self, _expr.getSourcePosition)
            _expr.setTypeEither(Either.error(errorMsg))
            Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
