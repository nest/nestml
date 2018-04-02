#
# ASTNoSemanticsics.py
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
Placeholder for rhs productions that are not implemented
"""
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode


class ASTNoSemantics(ASTVisitor):
    """
    A visitor which indicates that there a no semantics for the given node.
    """

    def visit_expression(self, node=None):
        """
        Visits a single rhs but does not execute any steps besides printing a message. This
        visitor indicates that no functionality has been implemented for this type of nodes.
        :param node: a single rhs
        :type node: ASTExpression or ASTSimpleExpression
        """
        error_msg = ErrorStrings.messageNoSemantics(self, str(node), node.get_source_position())
        node.set_type_either(Either.error(error_msg))
        # just warn though
        Logger.logMessage(_message=error_msg,
                          _code=MessageCode.NO_SEMANTICS,
                          _errorPosition=node.get_source_position(),
                          _logLevel=LOGGING_LEVEL.WARNING)
        return
