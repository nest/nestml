#
# ast_neuron.py
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

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.meta_model.ast_ode_shape import ASTOdeShape
from pynestml.meta_model.ast_neuron_body import ASTNeuronBody
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.symbols.variable_symbol import BlockType
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages

def symbol_by_name(name, symbols):
    """get a symbol from a list of symbols by the given name"""
    for sym in symbols:
        if sym.name == name:
            return sym
    return None

class ASTNeuron(ASTNeuronOrSynapse):
    """
    This class is used to store instances of neurons.
    ASTNeuron represents neuron.
    @attribute Name    The name of the neuron
    @attribute Body    The body of the neuron, e.g. internal, state, parameter...
    Grammar:
        neuron : 'neuron' NAME body;
    Attributes:
        name = None
        body = None
        artifact_name = None
    """

    def __init__(self, name, body, artifact_name=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param name: the name of the neuron.
        :type name: str
        :param body: the body containing the definitions.
        :type body: ASTBody
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        :param artifact_name: the name of the file this neuron is contained in
        :type artifact_name: str
        """
        super(ASTNeuron, self).__init__(name, body, artifact_name, *args, **kwargs)

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTNeuron
        """
        dup = ASTNeuron(name=self.name,
         body=self.body.clone(),
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

    def get_name(self):
        """
        Returns the name of the neuron.
        :return: the name of the neuron.
        :rtype: str
        """
        return self.name

    def get_body(self):
        """
        Return the body of the neuron.
        :return: the body containing the definitions.
        :rtype: ASTNeuronBody
        """
        return self.body

    def get_artifact_name(self):
        """
        Returns the name of the artifact this neuron has been stored in.
        :return: the name of the file
        :rtype: str
        """
        return self.artifact_name

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
        if isinstance(ret, list) and len(ret) == 0:
            return None
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

    def get_current_buffers(self):
        """
        Returns a list of all current buffers defined in the model.
        :return: a list of all current input buffers.
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for BUFFER in self.get_input_buffers():
            if BUFFER.is_current_buffer():
                ret.append(BUFFER)
        return ret

    def get_parameter_symbols(self):
        """
        Returns a list of all parameter symbol defined in the model.
        :return: a list of parameter symbols.
        :rtype: list(VariableSymbol)
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.PARAMETERS and \
                    not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_state_symbols(self):
        """
        Returns a list of all state symbol defined in the model.
        :return: a list of state symbols.
        :rtype: list(VariableSymbol)
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.STATE and \
                    not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_function_symbols(self):
        """
        Returns a list of all function symbols defined in the model.
        :return: a list of function symbols.
        :rtype: list(VariableSymbol)
        """
        from pynestml.symbols.variable_symbol import BlockType
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) \
             and (symbol.block_type == BlockType.EQUATION or symbol.block_type == BlockType.INITIAL_VALUES) \
             and symbol.is_function:
                ret.append(symbol)
        return ret

    def is_multisynapse_spikes(self):
        """
        Returns whether this neuron uses multi-synapse spikes.
        :return: True if multi-synaptic, otherwise False.
        :rtype: bool
        """
        buffers = self.get_spike_buffers()
        for iBuffer in buffers:
            if iBuffer.has_vector_parameter():
                return True
        return False

    def get_multiple_receptors(self):
        """
        Returns a list of all spike buffers which are defined as inhibitory and excitatory.
        :return: a list of spike buffers variable symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for iBuffer in self.get_spike_buffers():
            if iBuffer.is_excitatory() and iBuffer.is_inhibitory():
                if iBuffer is not None:
                    ret.append(iBuffer)
                else:
                    code, message = Messages.get_could_not_resolve(iBuffer.get_symbol_name())
                    Logger.log_message(
                        message=message,
                        code=code,
                        error_position=iBuffer.get_source_position(),
                        log_level=LoggingLevel.ERROR)
        return ret

    def get_initial_values_symbols(self):
        """
        Returns a list of all initial values symbol defined in the model. Note that the order here is the same as the order by which the symbols are defined in the model: this is important if a particular variable is defined in terms of another (earlier) variable.
        
        :return: a list of initial values symbols.
        :rtype: list(VariableSymbol)
        """

        """from pynestml.symbols.variable_symbol import BlockType
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) \
             and symbol.block_type == BlockType.INITIAL_VALUES \
             and not symbol.is_predefined:
                ret.append(symbol)
        return ret"""

        iv_syms = []
        symbols = self.get_scope().get_symbols_in_this_scope()
        
        iv_blk = self.get_initial_values_blocks()
        for decl in iv_blk.get_declarations():
            for var in decl.get_variables():
                iv_sym = symbol_by_name(var.get_complete_name(), symbols)
                assert not iv_sym is None, "Symbol by name \"" + var.get_complete_name() + "\" not found in initial values block"
                iv_syms.append(iv_sym)
        #print("Returning syms: " + ", ".join([iv_sym.name for iv_sym in iv_syms]))
        return iv_syms
                
        

    def get_initial_values_blocks(self):
        """
        Returns a list of all initial blocks defined in this body.
        :return: a list of initial-blocks.
        :rtype: list(ASTBlockWithVariables)
        """
        ret = list()
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_initial_values:
                ret.append(elem)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        if isinstance(ret, list) and len(ret) == 0:
            return None
        return ret

    def remove_initial_blocks(self):
        """
        Remove all equations blocks
        """
        from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTBlockWithVariables) and elem.is_initial_values:
                self.get_body().get_body_elements().remove(elem)

    def get_function_initial_values_symbols(self):
        """
        Returns a list of all initial values symbols as defined in the model which are marked as functions.
        :return: a list of symbols
        :rtype: list(VariableSymbol)
        """
        ret = list()
        for symbol in self.get_initial_values_symbols():
            if symbol.is_function:
                ret.append(symbol)
        return ret

    def get_non_function_initial_values_symbols(self):
        """
        Returns a list of all initial values symbols as defined in the model which are not marked as functions.
        :return: a list of symbols
        :rtype:list(VariableSymbol)
        """
        ret = list()
        for symbol in self.get_initial_values_symbols():
            if not symbol.is_function:
                ret.append(symbol)
        return ret

    def is_array_buffer(self):
        """
        This method indicates whether this neuron uses buffers defined vector-wise.
        :return: True if vector buffers defined, otherwise False.
        :rtype: bool
        """
        buffers = self.get_input_buffers()
        for BUFFER in buffers:
            if BUFFER.has_vector_parameter():
                return True
        return False
