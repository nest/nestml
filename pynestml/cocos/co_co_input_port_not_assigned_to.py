# -*- coding: utf-8 -*-
#
# co_co_input_port_not_assigned_to.py
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
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoInputPortNotAssignedTo(CoCo):
    """
    This coco ensures that no values are assigned to input ports.

    Given:

    .. code-block:: nestml

       input:
           current_in pA <- continuous

    Allowed:

    .. code-block:: nestml

       foo = current_in + 10 pA

    Not allowed:

    .. code-block:: nestml

       current_in = foo + 10 pA

    """

    @classmethod
    def check_co_co(cls, node: ASTNeuron):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        """
        node.accept(NoInputPortAssignedToVisitor())


class NoInputPortAssignedToVisitor(ASTVisitor):
    def visit_assignment(self, node):
        symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_name(), SymbolKind.VARIABLE)
        if symbol is not None and symbol.block_type == BlockType.INPUT:
            code, message = Messages.get_value_assigned_to_buffer(node.get_variable().get_complete_name())
            Logger.log_message(code=code, message=message,
                               error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
