# -*- coding: utf-8 -*-
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

from typing import List, Optional

from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.variable_symbol import BlockType, VariableSymbol


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
                        implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_input_ports(self) -> List[VariableSymbol]:
        """
        Returns a list of all defined input ports.
        :return: a list of all input ports.
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.INPUT:
                ret.append(symbol)
        return ret

    def get_spike_input_ports(self) -> List[VariableSymbol]:
        """
        Returns a list of all spike input ports defined in the model.
        """
        ret = list()
        for port in self.get_input_ports():
            if port.is_spike_input_port():
                ret.append(port)
        return ret

    def get_continuous_input_ports(self) -> List[VariableSymbol]:
        """
        Returns a list of all continuous time input ports defined in the model.
        """
        ret = list()
        for port in self.get_input_ports():
            if port.is_continuous_input_port():
                ret.append(port)
        return ret

    def get_vector_state_symbols(self) -> List[VariableSymbol]:
        """
        Returns a list of all state symbols that are vectors
        :return: a list of vector state symbols
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        vector_state_symbols = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.STATE and \
                    not symbol.is_predefined and symbol.has_vector_parameter():
                vector_state_symbols.append(symbol)
        return vector_state_symbols

    def get_vector_symbols(self) -> List[VariableSymbol]:
        """
        Returns a list of all the vector variables declared in State, Parameters, and Internals block
        :return: a list of vector symbols
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        vector_symbols = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) \
                    and (symbol.block_type == BlockType.STATE or symbol.block_type == BlockType.PARAMETERS
                         or symbol.block_type == BlockType.INTERNALS) \
                    and not symbol.is_predefined \
                    and symbol.has_vector_parameter():
                vector_symbols.append(symbol)

        return vector_symbols

    def get_single_receptors(self) -> List[VariableSymbol]:
        """
        Returns a list of spike input ports that are defined as either excitatory or inhibitory.
        :return: a list of spike input port variable symbols
        """
        return list(set(self.get_spike_input_ports()) - set(self.get_multiple_receptors()))

    def has_vector_port(self) -> bool:
        """
        This method indicates whether this neuron contains input ports defined vector-wise.
        :return: True if vector ports defined, otherwise False.
        """
        ports = self.get_input_ports()
        for port in ports:
            if port.has_vector_parameter():
                return True
        return False

    def has_state_vectors(self) -> bool:
        """
        This method indicates if the neuron has variables defined as vectors.
        :return: True if vectors are defined, false otherwise.
        """
        state_symbols = self.get_state_symbols()
        for symbol in state_symbols:
            if symbol.has_vector_parameter():
                return True

        return False

    def get_parameter_invariants(self):
        """
        Returns a list of all invariants of all parameters.
        :return: a list of rhs representing invariants
        :rtype: list(ASTExpression)
        """
        ret = list()
        for block in self.get_parameters_blocks():
            for decl in block.get_declarations():
                if decl.has_invariant():
                    ret.append(decl.get_invariant())

        return ret

    def get_parent(self, ast) -> Optional[ASTNode]:
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        """
        if self.get_body() is ast:
            return self
        if self.get_body().get_parent(ast) is not None:
            return self.get_body().get_parent(ast)
        return None

    def equals(self, other: ASTNode) -> bool:
        """
        The equals method.
        :param other: a different object.
        :return: True if equal, otherwise False.
        """
        if not isinstance(other, ASTNeuron):
            return False
        return self.get_name() == other.get_name() and self.get_body().equals(other.get_body())
