# -*- coding: utf-8 -*-
#
# co_co_function_have_rhs.py
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
from pynestml.cocos.co_co import CoCo
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoFunctionHaveRhs(CoCo):
    """
    This coco ensures that all function declarations, e.g., function V_rest mV = V_m - 55mV, have a rhs.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        node.accept(FunctionRhsVisitor())


class FunctionRhsVisitor(ASTVisitor):
    """
    This visitor ensures that everything declared as function has a rhs.
    """

    def visit_declaration(self, node):
        """
        Checks if the coco applies.
        :param node: a single declaration.
        :type node: ASTDeclaration.
        """
        if node.is_function and not node.has_expression():
            code, message = Messages.get_no_rhs(node.get_variables()[0].get_name())
            Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                               code=code, message=message)
        return
