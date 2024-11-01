# -*- coding: utf-8 -*-
#
# co_co_spike_input_ports_appear_only_in_equation_rhs_and_event_handlers.py
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

from typing import Optional
from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoSpikeInputPortsAppearOnlyInEquationRHSAndEventHandlers(CoCo):
    """
    This coco ensures that spiking input port names appear only in the right-hand side of equations and in the onReceive block declaration.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over node.
        """
        assert node is not None and (isinstance(node, ASTModel)), "No or wrong type provided (%s): expecting neuron or synapse!" % type(node)

        visitor = SpikeInputPortsAppearOnlyInEquationRHSAndEventHandlersVisitor()
        visitor.model_ = node
        node.accept(visitor)


class SpikeInputPortsAppearOnlyInEquationRHSAndEventHandlersVisitor(ASTVisitor):

    def visit_variable(self, node: ASTVariable):
        in_port: Optional[ASTInputPort] = ASTUtils.get_input_port_by_name(self.model_.get_input_blocks(), node.get_name())

        # only check spiking input ports
        if in_port is not None and in_port.is_spike():
            if in_port.parameters and not node.attribute:
                # input port has parameters (for instance, ``x`` in ``foo <- spike(x real)`` but the variable reference is missing an attribute (``foo`` instead of ``foo.x``)
                code, message = Messages.get_spike_input_port_attribute_missing(node.get_name())
                Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                                   log_level=LoggingLevel.ERROR)

            _node = node
            while _node:
                _node = _node.get_parent()

                if isinstance(_node, ASTOnReceiveBlock) and _node.input_port_variable.name == in_port.name:
                    # spike input port was used inside an ``onReceive`` block for this spike port; everything is OK
                    return

                if isinstance(_node, ASTOdeEquation):
                    # spike input port was used inside the rhs of an equation; everything is OK
                    return

                if isinstance(_node, ASTInlineExpression):
                    # spike input port was used inside the rhs of an inline expression; everything is OK
                    return

                if isinstance(_node, ASTModel):
                    # we reached the top-level block without running into an ``update`` block on the way --> incorrect usage of the function
                    code, message = Messages.get_spike_input_port_appears_outside_equation_rhs_and_event_handler(node.get_name())
                    Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                                       log_level=LoggingLevel.ERROR)

