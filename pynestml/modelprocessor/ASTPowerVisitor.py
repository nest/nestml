#
# ASTPowerVisitor.pyor.py
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
expression : <assoc=right> left=expression powOp='**' right=expression
"""
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class ASTPowerVisitor(ASTVisitor):
    """
    Visits a single power expression and updates its types accordingly.
    """

    def visitExpression(self, _expr=None):
        """
        Visits a single power expression and updates the types.
        :param _expr: a single expression.
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.ASTPowerVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        base_type_e = _expr.getLhs().getTypeEither()
        exponent_type_e = _expr.getRhs().getTypeEither()

        if base_type_e.isError():
            _expr.setTypeEither(base_type_e)
            return

        if exponent_type_e.isError():
            _expr.setTypeEither(exponent_type_e)
            return

        base_type = base_type_e.getValue()
        exponent_type = exponent_type_e.getValue()

        if base_type.isNumeric() and exponent_type.isNumeric():
            if base_type.isInteger() and exponent_type.isInteger():
                _expr.setTypeEither(Either.value(PredefinedTypes.getIntegerType()))
                return
            elif base_type.isUnit():
                # exponents to units MUST be integer and calculable at time of analysis.
                # Otherwise resulting unit is undefined
                if not exponent_type.isInteger():
                    error_msg = ErrorStrings.messageUnitBase(self, _expr.getSourcePosition())
                    _expr.setTypeEither(Either.error(error_msg))
                    Logger.logMessage(error_msg, LOGGING_LEVEL.ERROR)
                    return
                base_unit = base_type.getEncapsulatedUnit()
                # TODO the following part is broken @ptraeder?
                exponent_value = self.calculateNumericValue(
                    _expr.getRhs())  # calculate exponent value if exponent composed of literals
                if exponent_value.isValue():
                    _expr.setTypeEither(
                        Either.value(PredefinedTypes.getTypeIfExists(base_unit ** exponent_value.getValue())))
                    return
                else:
                    error_msg = exponent_value.getError()
                    _expr.setTypeEither(Either.error(error_msg))
                    Logger.logMessage(error_msg, LOGGING_LEVEL.ERROR)
                    return
            else:
                _expr.setTypeEither(Either.value(PredefinedTypes.getRealType()))
                return
        # Catch-all if no case has matched
        error_msg = ErrorStrings.messageUnitBase(self, _expr.getSourcePosition())
        _expr.setTypeEither(Either.error(error_msg))
        Logger.logMessage(error_msg, LOGGING_LEVEL.ERROR)

    def calculateNumericValue(self, _expr=None):
        """
        Calculates the numeric value of a exponent.
        :param _expr: a single expression
        :type _expr: ASTSimpleExpression or ASTExpression
        :return: an Either object
        :rtype: Either
        """
        # TODO write tests for this by PTraeder
        if isinstance(_expr, ASTExpression) and _expr.isEncapsulated():
            return self.calculateNumericValue(_expr.getExpression())
        elif isinstance(_expr, ASTSimpleExpression) and _expr.getNumericLiteral() is not None:
            if isinstance(_expr.getNumericLiteral(), int):
                literal = _expr.getNumericLiteral()
                return Either.value(literal)
            else:
                error_message = ErrorStrings.messageUnitBase(self, _expr.getSourcePosition())
                return Either.error(error_message)
        elif _expr.isUnaryOperator() and _expr.getUnaryOperator().isUnaryMinus():
            term = self.calculateNumericValue(_expr.getExpression())
            if term.isError():
                return term
            return Either.value(-term.getValue())
        error_message = ErrorStrings.messageNonConstantExponent(self, _expr.getSourcePosition())
        return Either.error(error_message)
