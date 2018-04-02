#
# ASTConditionVisitor.py
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
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ASTConditionVisitor(ASTVisitor):
    """
    This visitor is used to derive the correct type of a ternary operator, i.e., of all its subexpressions.
    """

    def visit_expression(self, node=None):
        """
        Visits an rhs consisting of the ternary operator and updates its type.
        :param node: a single rhs
        :type node: ASTExpression
        """
        assert (node is not None and (isinstance(node, ASTExpression))), \
            '(PyNestML.Visitor.ASTConditionVisitor) No or wrong type of rhs provided (%s)!' % type(node)
        condition_e = node.get_condition().get_type_either()
        if_true_e = node.get_if_true().get_type_either()
        if_not_e = node.get_if_not().get_type_either()

        if condition_e.isError():
            node.set_type_either(condition_e)
            return
        if if_true_e.isError():
            node.set_type_either(if_true_e)
            return
        if if_not_e.isError():
            node.set_type_either(if_not_e)
            return

        if_true = if_true_e.getValue()
        if_not = if_not_e.getValue()

        # Condition must be a bool
        if not condition_e.getValue().equals(PredefinedTypes.getBooleanType()):
            error_msg = ErrorStrings.messageTernary(self, node.get_source_position())
            node.set_type_either(Either.error(error_msg))
            Logger.logMessage(_message=error_msg, _errorPosition=node.get_source_position(),
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _logLevel=LOGGING_LEVEL.ERROR)
            return

        # Alternatives match exactly -> any is valid
        if if_true.equals(if_not):
            node.set_type_either(Either.value(if_true))
            return

        # Both are units but not matching-> real WARN
        if if_true.is_unit() and if_not.is_unit():
            error_msg = ErrorStrings.messageTernaryMismatch(self, if_true.print_symbol(), if_not.print_symbol(),
                                                            node.get_source_position())
            node.set_type_either(Either.value(PredefinedTypes.getRealType()))
            Logger.logMessage(_message=error_msg,
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _errorPosition=if_true.get_source_position(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return

        # one Unit and one numeric primitive and vice versa -> assume unit, WARN
        if (if_true.is_unit() and if_not.is_numeric_primitive()) or (if_not.is_unit() and if_true.is_numeric_primitive()):
            unit_type = None
            if if_true.is_unit():
                unit_type = if_true
            else:
                unit_type = if_not
            error_msg = ErrorStrings.messageTernaryMismatch(self, str(if_true), str(if_not),
                                                            node.get_source_position())
            node.set_type_either(Either.value(unit_type))
            Logger.logMessage(_message=error_msg,
                              _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                              _errorPosition=if_true.get_source_position(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            return

        # both are numeric primitives (and not equal) ergo one is real and one is integer -> real
        if if_true.is_numeric_primitive() and if_not.is_numeric_primitive():
            node.set_type_either(Either.value(PredefinedTypes.getRealType()))
            return

        # if we get here it is an error
        error_msg = ErrorStrings.messageTernaryMismatch(self, str(if_true), str(if_not),
                                                        node.get_source_position())
        node.set_type_either(Either.error(error_msg))
        Logger.logMessage(_message=error_msg,
                          _errorPosition=node.get_source_position(),
                          _code=MessageCode.TYPE_DIFFERENT_FROM_EXPECTED,
                          _logLevel=LOGGING_LEVEL.ERROR)
