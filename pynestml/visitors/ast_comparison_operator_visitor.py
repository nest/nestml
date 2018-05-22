#
# ast_comparison_operator_visitor.py.py
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
rhs : left=rhs comparisonOperator right=rhs
"""
from pynestml.symbols.PredefinedTypes import PredefinedTypes
from pynestml.symbols.UnitTypeSymbol import UnitTypeSymbol
from pynestml.utils.error_strings import ErrorStrings
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import MessageCode
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.symbols.BooleanTypeSymbol import BooleanTypeSymbol
from pynestml.symbols.ErrorTypeSymbol import ErrorTypeSymbol


class ASTComparisonOperatorVisitor(ASTVisitor):
    """
    Visits a single rhs consisting of a binary comparison operator.
    """

    def visit_expression(self, _expr=None):
        """
        Visits a single comparison operator expression and updates the type.
        :param _expr: an expression
        :type _expr: ASTExpression
        """
        lhs_type = _expr.get_lhs().type
        rhs_type = _expr.get_rhs().type

        lhs_type.referenced_object = _expr.get_lhs()
        rhs_type.referenced_object = _expr.get_rhs()

        if (lhs_type.is_numeric_primitive() and rhs_type.is_numeric_primitive()) \
                or (lhs_type.equals(rhs_type) and lhs_type.is_numeric()) or (
                isinstance(lhs_type, BooleanTypeSymbol) and isinstance(rhs_type, BooleanTypeSymbol)):
            _expr.type = PredefinedTypes.get_boolean_type()
            return

        # Error message for any other operation
        if (isinstance(lhs_type, UnitTypeSymbol) and rhs_type.is_numeric()) or (
                isinstance(rhs_type, UnitTypeSymbol) and lhs_type.is_numeric()):
            # if the incompatibility exists between a unit and a numeric, the c++ will still be fine, just WARN
            error_msg = ErrorStrings.message_comparison(self, _expr.get_source_position())
            _expr.type = PredefinedTypes.get_boolean_type()
            Logger.log_message(message=error_msg, code=MessageCode.SOFT_INCOMPATIBILITY,
                               error_position=_expr.get_source_position(),
                               log_level=LoggingLevel.WARNING)
            return
        else:
            # hard incompatibility, cannot recover in c++, ERROR
            error_msg = ErrorStrings.message_comparison(self, _expr.get_source_position())
            _expr.type = ErrorTypeSymbol()
            Logger.log_message(code=MessageCode.HARD_INCOMPATIBILITY,
                               error_position=_expr.get_source_position(),
                               message=error_msg, log_level=LoggingLevel.ERROR)
            return
