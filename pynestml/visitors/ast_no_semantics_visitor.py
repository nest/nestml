# -*- coding: utf-8 -*-
#
# ast_no_semantics_visitor.py
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
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.utils.error_strings import ErrorStrings
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import MessageCode
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTNoSemanticsVisitor(ASTVisitor):
    """
    A visitor which indicates that there a no semantics for the given node.
    """

    def visit_expression(self, node):
        """
        Visits a single rhs but does not execute any steps besides printing a message. This
        visitor indicates that no functionality has been implemented for this type of nodes.
        :param node: a single rhs
        :type node: ast_expression or ast_simple_expression
        """
        error_msg = ErrorStrings.message_no_semantics(self, str(node), node.get_source_position())
        node.type = ErrorTypeSymbol()
        # just warn though
        Logger.log_message(message=error_msg,
                           code=MessageCode.NO_SEMANTICS,
                           error_position=node.get_source_position(),
                           log_level=LoggingLevel.WARNING)
        return
