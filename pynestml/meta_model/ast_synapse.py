# -*- coding: utf-8 -*-
#
# ast_synapse.py
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

from typing import List, Optional

from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock
from pynestml.meta_model.ast_synapse_body import ASTSynapseBody
from pynestml.symbols.variable_symbol import BlockType
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages


class ASTSynapse(ASTNeuronOrSynapse):
    """
    This class is used to store instances of synapses.
    ASTSynapse represents synapse.
    @attribute Name    The name of the synapse
    @attribute Body    The body of the synapse, e.g. internal, state, parameter...
    Grammar:
        synapse : 'synapse' NAME body;
    Attributes:
        name = None
        body = None
        artifact_name = None
    """

    def __init__(self, name, body, default_weight=None, artifact_name=None, *args, **kwargs):
        """
        Standard constructor.
        :param name: the name of the synapse.
        :type name: str
        :param body: the body containing the definitions.
        :type body: ASTSynapseBody
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        :param artifact_name: the name of the file this synapse is contained in
        :type artifact_name: str
        """
        super(ASTSynapse, self).__init__(name, body, artifact_name, *args, **kwargs)
        self._default_weight = default_weight

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTSynapse
        """
        dup = ASTSynapse(name=self.name,
                         body=self.body.clone(),
                         default_weight=self._default_weight,
                         artifact_name=self.artifact_name,
                         # ASTNode common attributes:
                         source_position=self.source_position,
                         scope=self.scope,
                         comment=self.comment,
                         pre_comments=[s for s in self.pre_comments],
                         in_comment=self.in_comment,
                         post_comments=[s for s in self.post_comments],
                         implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def set_default_weight(self, w):
        self._default_weight = w

    def set_default_delay(self, var, expr, dtype):
        self._default_delay_variable = var
        self._default_delay_expression = expr
        self._default_delay_dtype = dtype


    def get_default_delay_expression(self):
        return self._default_delay_expression

    def get_default_delay_variable(self):
        return self._default_delay_variable

    def get_default_delay_dtype(self):
        return self._default_delay_dtype

    def get_weight_variable(self):
        return self._default_weight

    def get_default_weight(self):
        return self._default_weight

    def get_body(self):
        """
        Return the body of the synapse.
        :return: the body containing the definitions.
        :rtype: ASTSynapseBody
        """
        return self.body

    def get_on_receive_blocks(self) -> List[ASTOnReceiveBlock]:
        if not self.get_body():
            return []
        return self.get_body().get_on_receive_blocks()
        
    def get_on_receive_block(self, port_name: str) -> Optional[ASTOnReceiveBlock]:
        if not self.get_body():
            return None
        return self.get_body().get_on_receive_block(port_name)

    def get_input_blocks(self):
        """
        Returns a list of all input-blocks defined.
        :return: a list of defined input-blocks.
        :rtype: list(ASTInputBlock)
        """
        ret = list()
        from pynestml.meta_model.ast_input_block import ASTInputBlock
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTInputBlock):
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        elif isinstance(ret, list) and len(ret) == 0:
            return None
        else:
            return ret

    def get_input_buffers(self):
        """
        Returns a list of all defined input buffers.
        :return: a list of all input buffers.
        :rtype: list(VariableSymbol)
        """
        from pynestml.symbols.variable_symbol import BlockType
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and (symbol.block_type == BlockType.INPUT_BUFFER_SPIKE
                                                       or symbol.block_type == BlockType.INPUT_BUFFER_CURRENT):
                ret.append(symbol)
        return ret

    def get_spike_buffers(self):
        """
        Returns a list of all spike input buffers defined in the model.
        :return: a list of all spike input buffers.
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for BUFFER in self.get_input_buffers():
            if BUFFER.is_spike_buffer():
                ret.append(BUFFER)
        return ret
