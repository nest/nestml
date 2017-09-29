#
# ComparisonOperatorVisitor.py
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
expression : left=expression comparisonOperator right=expression
"""
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
from pynestml.src.main.python.org.nestml.symbol_table.typechecker.TypeChecker import TypeChecker
from pynestml.src.main.python.org.nestml.visitor.ErrorStrings import ErrorStrings
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
from pynestml.src.main.python.org.nestml.visitor.expression_visitor.Either import Either
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL


class ComparisonOperatorVisitor(NESTMLVisitor):
    
    def visitExpression(self, _expr=None):
        lhsTypeE = _expr.getLhs().getTypeEither()
        rhsTypeE = _expr.getRhs().getTypeEither()

        if lhsTypeE.isError():
            _expr.setTypeEither(lhsTypeE)
            return
        if rhsTypeE.isError():
            _expr.setTypeEither(rhsTypeE)
            return

        lhsType = lhsTypeE.getValue()
        rhsType = rhsTypeE.getValue()

        if ((TypeChecker.isReal(lhsType) or TypeChecker.isInteger(lhsType))
            and (TypeChecker.isReal(rhsType) or TypeChecker.isInteger(rhsType)))\
                or (lhsType.equals(rhsType) and TypeChecker.isNumeric(lhsType))\
                or (TypeChecker.isBoolean(lhsType) and TypeChecker.isBoolean(rhsType)):
            _expr.setTypeEither(Either.value(PredefinedTypes.getBooleanType()))
            return

        #Error message for any other operation
        if (TypeChecker.isUnit(lhsType) and TypeChecker.isNumeric(rhsType)) \
                or (TypeChecker.isUnit(rhsType) and TypeChecker.isNumeric(lhsType)):
            #if the incompatibility exists between a unit and a numeric, the c++ will still be fine, just WARN
            errorMsg = ErrorStrings.messageComparison(self,_expr.getSourcePosition())
            _expr.setTypeEither(Either.value(PredefinedTypes.getBooleanType()))
            Logger.logMessage(errorMsg, LOGGING_LEVEL.WARNING)
            return
        else:
            #hard incombatibility, cannot recover in c++, ERROR
            errorMsg = ErrorStrings.messageComparison(self, _expr.getSourcePosition())
            _expr.setTypeEither(Either.error(errorMsg))
            Logger.logMessage(errorMsg, LOGGING_LEVEL.ERROR)
            return