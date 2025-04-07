# -*- coding: utf-8 -*-
#
# co_co_timestep_function_legally_used.py
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
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoTimestepFuncLegallyUsed(CoCo):
    """
    This Coco ensures that the predefined ``timestep()`` function appears only in the update.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Checks the coco.
        :param node: a single node (typically, a neuron or synapse)
        """
        visitor = CoCoTimestepFuncLegallyUsedVisitor()
        visitor.neuron = node
        node.accept(visitor)


class CoCoTimestepFuncLegallyUsedVisitor(ASTVisitor):
    def visit_simple_expression(self, node):
        """
        Visits a single function call

        :param node: a simple expression
        """
        assert isinstance(node, ASTSimpleExpression), \
            '(PyNestML.Visitor.FunctionCallVisitor) No or wrong type of simple expression provided (%s)!' % tuple(node)
        assert (node.get_scope() is not None), \
            "(PyNestML.Visitor.FunctionCallVisitor) No scope found, run symboltable creator!"
        if node.get_function_call() is None:
            return
        function_name = node.get_function_call().get_name()
        if function_name == PredefinedFunctions.TIME_TIMESTEP:
            _node = node
            while _node:
                _node = _node.get_parent()

                if isinstance(_node, ASTUpdateBlock):
                    # function was used inside an ``update`` block; everything is OK
                    return

                if isinstance(_node, ASTModel):
                    # we reached the top-level block without running into an ``update`` block on the way --> incorrect usage of the function
                    code, message = Messages.get_timestep_function_legally_used()
                    Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                                       log_level=LoggingLevel.ERROR)
