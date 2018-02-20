#
# PowVisitor.py
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
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol


class PowVisitor(NESTMLVisitor):
    """
    Visits a single power expression and updates its types accordingly.
    """

    def visit_expression(self, _expr=None):
        """
        Visits a single power expression and updates the types.
        :param _expr: a single expression.
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.PowVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        baseTypeE = _expr.getLhs().getTypeEither()
        exponentTypeE = _expr.getRhs().getTypeEither()

        if baseTypeE.isError():
            _expr.setTypeEither(baseTypeE)
            return

        if exponentTypeE.isError():
            _expr.setTypeEither(exponentTypeE)
            return

        baseType = baseTypeE.getValue()
        exponentType = exponentTypeE.getValue()

        if baseType.is_instance_of(UnitTypeSymbol):
            _expr.type = self.try_to_calculate_resulting_unit(_expr)
            return
        else:
            _expr.type = baseType ** exponentType
            return

    def try_to_calculate_resulting_unit(self, _expr):
        base_type = _expr.getLhs().getTypeEither().getValue()
        exponent_numeric_value_either = self.calculateNumericValue(_expr.getRhs())
        if exponent_numeric_value_either.isValue():
            return base_type ** exponent_numeric_value_either.getValue()
        else:
            return base_type ** None


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
            return self.calculateNumericValue(_expr.getExpr())
        elif isinstance(_expr, ASTSimpleExpression) and _expr.getNumericLiteral() is not None:
            if isinstance(_expr.getNumericLiteral(), int):
                literal = _expr.getNumericLiteral()
                return Either.value(literal)
            else:
                errorMessage = ErrorStrings.messageUnitBase(self, _expr.getSourcePosition())
                return Either.error(errorMessage)
        elif _expr.isUnaryOperator() and _expr.getUnaryOperator().isUnaryMinus():
            term = self.calculateNumericValue(_expr.getExpression())
            if term.isError():
                return term
            return Either.value(-term.getValue())
        errorMessage = ErrorStrings.messageNonConstantExponent(self, _expr.getSourcePosition())
        return Either.error(errorMessage)
