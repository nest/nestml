#
# LoggingHelper.py
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
expression : left=expression (plusOp='+'  | minusOp='-') right=expression
"""
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class LoggingHelper(object):
    @staticmethod
    def drop_missing_type_error(_assignment):
        code, message = Messages.getTypeCouldNotBeDerived(_assignment.getExpression())
        Logger.logMessage(_code=code, _message=message, _errorPosition=_assignment.getExpression().getSourcePosition(),
                          _logLevel=LOGGING_LEVEL.ERROR)

    @staticmethod
    def drop_incompatible_types_error(_containing_expression, _lhs_type_symbol, _rhs_type_symbol):
        code, message = Messages.getTypeDifferentFromExpected(_lhs_type_symbol, _rhs_type_symbol)
        Logger.logMessage(_errorPosition=_containing_expression.getSourcePosition(),
                          _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)

    @staticmethod
    def drop_implicit_cast_warning(_source_position, _lhs_type_symbol, _rhs_type_symbol):
        code, message = Messages.getImplicitCastRhsToLhs(_rhs_type_symbol.print_symbol(),
                                                         _lhs_type_symbol.print_symbol())
        Logger.logMessage(_errorPosition=_source_position,
                          _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
