# -*- coding: utf-8 -*-
#
# co_co_vector_input_port_correct_size_type.py
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
from pynestml.meta_model.ast_expression import ASTExpression

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoVectorInputPortsCorrectSizeType(CoCo):
    """
    This CoCo checks if the size of the vector input port is of the type integer and its value is greater than 0.
    """
    @classmethod
    def check_co_co(cls, node: ASTNeuron):
        visitor = InputPortsVisitor()
        node.accept(visitor)


class InputPortsVisitor(ASTVisitor):
    """
    This visitor checks if the size of the vector input port is of the type integer and its value is greater than 0
    """
    def visit_input_port(self, node: ASTInputPort):
        size_parameter = node.get_size_parameter()
        if size_parameter:
            # For negative numbers, the size_parameter is an expression
            if isinstance(size_parameter, ASTExpression) and size_parameter.is_unary_operator() and \
                    size_parameter.get_unary_operator().is_unary_minus and size_parameter.get_expression().is_numeric_literal():
                code, message = Messages.get_input_port_size_not_greater_than_zero(node.get_name())
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)
                return

            # otherwise, it is a simple expression
            if size_parameter.is_variable() or (size_parameter.is_numeric_literal() and not isinstance(size_parameter.get_numeric_literal(), int)):
                code, message = Messages.get_input_port_size_not_integer(node.get_name())
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)
                return
