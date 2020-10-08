# -*- coding: utf-8 -*-
#
# co_co_function_max_one_lhs.py
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


class CoCoFunctionMaxOneLhs(CoCo):
    """
    This coco ensures that whenever a function (aka alias) is declared, only one left-hand side is present.
    Allowed:
        function V_rest mV = V_m - 55mV
    Not allowed:
        function V_reset,V_rest mV = V_m - 55mV
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        node.accept(FunctionMaxOneLhs())


class FunctionMaxOneLhs(ASTVisitor):
    """
    This visitor ensures that every function has exactly one lhs.
    """

    def visit_declaration(self, node):
        """
        Checks the coco.
        :param node: a single declaration.
        :type node: ast_declaration
        """
        if node.is_function and len(node.get_variables()) > 1:
            code, message = Messages.get_several_lhs(list((var.get_name() for var in node.get_variables())))
            Logger.log_message(error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR,
                               code=code, message=message)
        return
