#
# BinaryLogicVisitor.py
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
expression: left=expression logicalOperator right=expression
"""
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.BooleanTypeSymbol import BooleanTypeSymbol
from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class BinaryLogicVisitor(NESTMLVisitor):
    """
    Visits a single binary logical operator expression and updates its types.
    """

    def visit_expression(self, _expr=None):
        """
        Visits an expression which uses a binary logic operator and updates the type.
        :param _expr: a single expression.
        :type _expr: ASTExpression
        """
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.Visitor.BinaryLogicVisitor) No or wrong type of expression provided (%s)!' % type(_expr)
        lhs_type_e = _expr.getLhs().getTypeEither()
        rhs_type_e = _expr.getRhs().getTypeEither()

        if lhs_type_e.isError():
            _expr.setTypeEither(lhs_type_e)
            return
        if rhs_type_e.isError():
            _expr.setTypeEither(rhs_type_e)
            return

        lhs_type = lhs_type_e.getValue()
        rhs_type = rhs_type_e.getValue()

        lhs_type.referenced_object = _expr.getLhs()
        rhs_type.referenced_object = _expr.getRhs()

        if isinstance(lhs_type, BooleanTypeSymbol) and isinstance(rhs_type, BooleanTypeSymbol):
            _expr.type = PredefinedTypes.getBooleanType()
        else:
            if (isinstance(lhs_type, BooleanTypeSymbol)):
                offending_type = lhs_type
            else:
                offending_type = rhs_type
            code, message = Messages.getTypeDifferentFromExpected(BooleanTypeSymbol(), offending_type)
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=lhs_type.referenced_object.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
            _expr.type = ErrorTypeSymbol()
        return
