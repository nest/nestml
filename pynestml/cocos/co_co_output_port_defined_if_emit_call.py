# -*- coding: utf-8 -*-
#
# co_co_output_port_defined_if_emit_call.py
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
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.template_type_symbol import TemplateTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.type_caster import TypeCaster
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoOutputPortDefinedIfEmitCall(CoCo):
    """
    This context condition checker ensures that if an event is emitted, a corresponding output port is defined with the appropriate type.
    """

    @classmethod
    def check_co_co(cls, neuron: ASTNeuron):
        """
        Checks the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        visitor = OutputPortDefinedIfEmitCalledVisitor()
        visitor.neuron = neuron
        neuron.accept(visitor)


class OutputPortDefinedIfEmitCalledVisitor(ASTVisitor):
    """
    This visitor ensures that all function calls are consistent.
    """

    neuron = None

    def visit_function_call(self, node):
        """
        Check consistency for a single function call: check if the called function has been declared, whether the number and types of arguments correspond to the declaration, etc.

        :param node: a single function call.
        :type node: ASTFunctionCall
        """
        func_name = node.get_name()
        if func_name == 'emit_spike':
            output_block = self.neuron.get_output_blocks()
            if output_block is None:
                code, message = Messages.get_block_not_defined_correctly('output', missing=True)
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)
                return

            if not output_block.is_spike():
                code, message = Messages.get_emit_spike_function_but_no_output_port()
                Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                                   error_position=node.get_source_position())
                return
