# -*- coding: utf-8 -*-
#
# ast_condition_visitor.py
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
rhs : condition=rhs '?' ifTrue=rhs ':' ifNot=rhs
"""
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.error_strings import ErrorStrings
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import MessageCode
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTConditionVisitor(ASTVisitor):
    """
    This visitor is used to derive the correct type of a ternary operator, i.e., of all its subexpressions.
    """

    def visit_expression(self, node):
        """
        Visits an rhs consisting of the ternary operator and updates its type.
        :param node: a single rhs
        :type node: ast_expression
        """
        condition = node.get_condition().type
        if_true = node.get_if_true().type
        if_not = node.get_if_not().type

        condition.referenced_object = node.get_condition()
        if_true.referenced_object = node.get_if_true()
        if_not.referenced_object = node.get_if_not()

        # Condition must be a bool
        if not condition.equals(PredefinedTypes.get_boolean_type()):
            error_msg = ErrorStrings.message_ternary(self, node.get_source_position())
            node.type = ErrorTypeSymbol()
            Logger.log_message(message=error_msg, error_position=node.get_source_position(),
                               code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                               log_level=LoggingLevel.ERROR)
            return

        # Alternatives match exactly -> any is valid
        if if_true.equals(if_not) \
                or if_true.differs_only_in_magnitude(if_not) \
                or if_true.is_castable_to(if_not):
            node.type = if_true
            return

        # Both are units but not matching-> real WARN
        if isinstance(if_true, UnitTypeSymbol) and isinstance(if_not, UnitTypeSymbol):
            error_msg = ErrorStrings.message_ternary_mismatch(self, if_true.print_symbol(), if_not.print_symbol(),
                                                              node.get_source_position())
            node.type = PredefinedTypes.get_real_type()
            Logger.log_message(message=error_msg,
                               code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                               error_position=if_true.referenced_object.get_source_position(),
                               log_level=LoggingLevel.WARNING)
            return

        # one Unit and one numeric primitive and vice versa -> assume unit, WARN
        if (isinstance(if_true, UnitTypeSymbol) and if_not.is_numeric_primitive()) or (
                isinstance(if_not, UnitTypeSymbol) and if_true.is_numeric_primitive()):
            if isinstance(if_true, UnitTypeSymbol):
                unit_type = if_true
            else:
                unit_type = if_not
            error_msg = ErrorStrings.message_ternary_mismatch(self, str(if_true), str(if_not),
                                                              node.get_source_position())
            node.type = unit_type
            Logger.log_message(message=error_msg,
                               code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                               error_position=if_true.referenced_object.get_source_position(),
                               log_level=LoggingLevel.WARNING)
            return

        # both are numeric primitives (and not equal) ergo one is real and one is integer -> real
        if if_true.is_numeric_primitive() and if_not.is_numeric_primitive():
            node.type = PredefinedTypes.get_real_type()
            return

        # if we get here it is an error
        error_msg = ErrorStrings.message_ternary_mismatch(self, str(if_true), str(if_not),
                                                          node.get_source_position())
        node.type = ErrorTypeSymbol()
        Logger.log_message(message=error_msg,
                           error_position=node.get_source_position(),
                           code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                           log_level=LoggingLevel.ERROR)
