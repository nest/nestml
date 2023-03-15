# -*- coding: utf-8 -*-
#
# co_co_resolution_func_legally_used.py
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
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.symbols.predefined_functions import PredefinedFunctions


class CoCoResolutionFuncLegallyUsed(CoCo):
    """
    This Coco ensures that the predefined ``resolution()`` function appears only in the update, parameters, internals, or state block.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Checks the coco.
        :param node: a single node (typically, a neuron or synapse)
        """
        visitor = CoCoResolutionFuncLegallyUsedVisitor()
        visitor.neuron = node
        node.accept(visitor)


class CoCoResolutionFuncLegallyUsedVisitor(ASTVisitor):
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
        if function_name == PredefinedFunctions.TIME_RESOLUTION:
            _node = node
            while _node:
                _node = self.neuron.get_parent(_node)

                if isinstance(_node, ASTEquationsBlock) \
                        or isinstance(_node, ASTFunction):
                    code, message = Messages.get_could_not_resolve(function_name)
                    Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                                       log_level=LoggingLevel.ERROR)
