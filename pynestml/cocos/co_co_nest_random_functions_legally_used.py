# -*- coding: utf-8 -*-
#
# co_co_nest_random_functions_legally_used.py
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
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_on_condition_block import ASTOnConditionBlock
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoNestRandomFunctionsLegallyUsed(CoCo):
    """
    This CoCo ensure that the random functions are used only in the ``update``, ``onReceive``, and ``onCondition`` blocks.
    This CoCo is only checked for the NEST Simulator target.
    """

    @classmethod
    def check_co_co(cls, node: ASTNode):
        """
        Checks the coco.
        :param node: a single node (typically, a neuron or synapse)
        """
        visitor = CoCoNestRandomFunctionsLegallyUsedVisitor()
        visitor.neuron = node
        node.accept(visitor)


class CoCoNestRandomFunctionsLegallyUsedVisitor(ASTVisitor):
    def visit_function_call(self, node):
        """
        Visits a function call
        :param node: a function call
        """
        function_name = node.get_name()
        if function_name == PredefinedFunctions.RANDOM_NORMAL or function_name == PredefinedFunctions.RANDOM_UNIFORM \
                or function_name == PredefinedFunctions.RANDOM_POISSON:
            parent = node
            while parent:
                parent = parent.get_parent()

                if isinstance(parent, ASTUpdateBlock) or isinstance(parent, ASTOnReceiveBlock) \
                        or isinstance(parent, ASTOnConditionBlock):
                    # the random function is correctly defined, hence return
                    return

                if isinstance(parent, ASTModel):
                    # the random function is defined in other blocks (parameters, state, internals). Hence, an error.
                    code, message = Messages.get_random_functions_legally_used(function_name)
                    Logger.log_message(node=self.neuron, code=code, message=message, error_position=node.get_source_position(),
                                       log_level=LoggingLevel.ERROR)
