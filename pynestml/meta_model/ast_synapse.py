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

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_shape import ASTOdeShape
from pynestml.meta_model.ast_synapse_body import ASTSynapseBody
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.symbols.variable_symbol import BlockType
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.ast_utils import ASTUtils
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

    def __init__(self, name, body, source_position=None, artifact_name=None):
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
        print("In ASTSynapse::__init__()")

        assert isinstance(name, str), \
            '(PyNestML.AST.Synapse) No  or wrong type of synapse name provided (%s)!' % type(name)
        assert isinstance(body, ASTSynapseBody), \
            '(PyNestML.AST.Synapse) No or wrong type of synapse body provided (%s)!' % type(body)
        assert (artifact_name is not None and isinstance(artifact_name, str)), \
            '(PyNestML.AST.Synapse) No or wrong type of artifact name provided (%s)!' % type(artifact_name)
        super(ASTSynapse, self).__init__(name, body, source_position, artifact_name)
        self.name = name + "_connection" + FrontendConfiguration.suffix
        self.body = body
        self.artifact_name = artifact_name
        self._default_weight = None


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


    def get_pre_receive(self):
        """
        Returns the pre_receive block
        :return: the pre_receive block
        :rtype: ...
        """
        return self.get_body().get_pre_receive()


    def get_post_receive(self):
        """
        Returns the post_receive block
        :return: the post_receive block
        :rtype: ...
        """
        return self.get_body().get_post_receive()

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
            if isinstance(symbol, VariableSymbol) and (symbol.block_type == BlockType.INPUT_BUFFER_SPIKE or
                                                       symbol.block_type == BlockType.INPUT_BUFFER_CURRENT):
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

