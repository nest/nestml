#
# logging_helper.py
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
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class LoggingHelper(object):
    @staticmethod
    def drop_missing_type_error(_assignment):
        code, message = Messages.get_type_could_not_be_derived(_assignment.get_expression())
        Logger.log_message(code=code, message=message,
                           error_position=_assignment.get_expression().get_source_position(),
                           log_level=LoggingLevel.ERROR)

    @staticmethod
    def drop_incompatible_types_error(containing_expression, lhs_type_symbol, rhs_type_symbol):
        code, message = Messages.get_type_different_from_expected(lhs_type_symbol, rhs_type_symbol)
        Logger.log_message(error_position=containing_expression.get_source_position(),
                           code=code, message=message, log_level=LoggingLevel.ERROR)

    @staticmethod
    def drop_implicit_cast_warning(source_position, lhs_type_symbol, rhs_type_symbol):
        code, message = Messages.get_implicit_cast_rhs_to_lhs(rhs_type_symbol.print_symbol(),
                                                              lhs_type_symbol.print_symbol())
        Logger.log_message(error_position=source_position,
                           code=code, message=message, log_level=LoggingLevel.WARNING)
