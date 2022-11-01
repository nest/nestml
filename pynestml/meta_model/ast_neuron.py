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

from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse
from pynestml.meta_model.ast_neuron_or_synapse_body import ASTNeuronOrSynapseBody
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_output_block import ASTOutputBlock
from pynestml.symbols.variable_symbol import BlockType, VariableSymbol
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages


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
                        post_comments=[s for s in self.post_comments],
                        implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_name(self) -> str:
        """
        Returns the name of the neuron.
        :return: the name of the neuron.
        """
        return self.name

    def get_body(self) -> ASTNeuronOrSynapseBody:
        """
        Return the body of the neuron.
        :return: the body containing the definitions.
        """
        return self.body

    def get_artifact_name(self) -> str:
        """
        Returns the name of the artifact this neuron has been stored in.
        :return: the name of the file
        """
        return self.artifact_name

    def remove_equations_block(self) -> None:
        """
        Deletes all equations blocks. By construction as checked through cocos there is only one there.
        """

        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTEquationsBlock):
                self.get_body().get_body_elements().remove(elem)

    def get_equations(self) -> List[ASTOdeEquation]:
        """
        Returns all ode equations as defined in this neuron.
        :return list of ode-equations
        """
        ret = list()

        for block in self.get_equations_blocks():
            ret.extend(block.get_ode_equations())

        return ret

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

    def get_parameter_symbols(self) -> List[VariableSymbol]:
        """
        Returns a list of all parameter symbol defined in the model.
        :return: a list of parameter symbols.
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type in [BlockType.PARAMETERS, BlockType.COMMON_PARAMETERS] and \
                    not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_state_symbols(self) -> List[VariableSymbol]:
        """
        Returns a list of all state symbol defined in the model.
        :return: a list of state symbols.
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.STATE and \
                    not symbol.is_predefined:
                ret.append(symbol)
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

    def get_internal_symbols(self) -> List[VariableSymbol]:
        """
        Returns a list of all internals symbol defined in the model.
        :return: a list of internals symbols.
        """
        from pynestml.symbols.variable_symbol import BlockType
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and symbol.block_type == BlockType.INTERNALS and \
                    not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_inline_expression_symbols(self) -> List[VariableSymbol]:
        """
        Returns a list of all inline expression symbols defined in the model.
        :return: a list of symbols
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) \
                    and (symbol.block_type == BlockType.EQUATION or symbol.block_type == BlockType.STATE) \
                    and symbol.is_inline_expression:
                ret.append(symbol)
        return ret

    def is_multisynapse_spikes(self) -> bool:
        """
        Returns whether this neuron uses multi-synapse inputs.
        :return: True if multi-synaptic, otherwise False.
        """
        ports = self.get_spike_input_ports()
        for port in ports:
            if port.has_vector_parameter():
                return True
        return False

    def get_multiple_receptors(self) -> List[VariableSymbol]:
        """
        Returns a list of all spike input ports which are defined as both inhibitory *and* excitatory at the same time.
        :return: a list of spike input port variable symbols
        """
        ret = list()
        for port in self.get_spike_input_ports():
            if port.is_excitatory() and port.is_inhibitory():
                if port is not None:
                    ret.append(port)
                else:
                    code, message = Messages.get_could_not_resolve(port.get_symbol_name())
                    Logger.log_message(
                        message=message,
                        code=code,
                        error_position=port.get_source_position(),
                        log_level=LoggingLevel.ERROR)
        return ret

    def get_kernel_by_name(self, kernel_name: str) -> Optional[ASTKernel]:
        assert type(kernel_name) is str
        kernel_name = kernel_name.split("__X__")[0]

        if not self.get_equations_blocks():
            return None

        # check if defined as a direct function of time
        for equations_block in self.get_equations_blocks():
            for decl in equations_block.get_declarations():
                if type(decl) is ASTKernel and kernel_name in decl.get_variable_names():
                    return decl

        # check if defined for a higher order of differentiation
        for equations_block in self.get_equations_blocks():
            for decl in equations_block.get_declarations():
                if type(decl) is ASTKernel and kernel_name in [s.replace("$", "__DOLLAR").replace("'", "") for s in
                                                               decl.get_variable_names()]:
                    return decl

        return None

    def get_all_kernels(self):
        kernels = []
        for equations_block in self.get_equations_blocks():
            for decl in equations_block.get_declarations():
                if type(decl) is ASTKernel:
                    kernels.append(decl)
        return kernels

    def get_non_inline_state_symbols(self) -> List[VariableSymbol]:
        """
        Returns a list of all state symbols as defined in the model which are not marked as inline expressions.
        :return: a list of symbols
        """
        ret = list()
        for symbol in self.get_state_symbols():
            if not symbol.is_inline_expression:
                ret.append(symbol)
        return ret

    def get_ode_defined_symbols(self):
        """
        Returns a list of all variable symbols which have been defined in th state blocks
        and are provided with an ode.
        :return: a list of state variables with odes
        :rtype: list(VariableSymbol)
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and \
                    symbol.block_type == BlockType.STATE and symbol.is_ode_defined() \
                    and not symbol.is_predefined:
                ret.append(symbol)
        return ret

    def get_state_symbols_without_ode(self):
        """
        Returns a list of all elements which have been defined in the state block.
        :return: a list of of state variable symbols.
        :rtype: list(VariableSymbol)
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and \
                    symbol.block_type == BlockType.STATE and not symbol.is_ode_defined() \
                    and not symbol.is_predefined:
                ret.append(symbol)
        return ret

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

    def add_to_state_block(self, declaration: ASTDeclaration):
        """
        Adds the handed over declaration an arbitrary state block.
        :param declaration: a single declaration.
        """
        from pynestml.utils.ast_utils import ASTUtils
        if not self.get_state_blocks():
            ASTUtils.create_state_block(self)
        self.get_state_blocks()[0].get_declarations().append(declaration)
        declaration.update_scope(self.get_state_blocks()[0].get_scope())
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor

        symtable_vistor = ASTSymbolTableVisitor()
        symtable_vistor.block_type_stack.push(BlockType.STATE)
        declaration.accept(symtable_vistor)
        symtable_vistor.block_type_stack.pop()
        from pynestml.symbols.symbol import SymbolKind
        assert declaration.get_variables()[0].get_scope().resolve_to_symbol(
            declaration.get_variables()[0].get_name(), SymbolKind.VARIABLE) is not None
        assert declaration.get_scope().resolve_to_symbol(declaration.get_variables()[0].get_name(),
                                                         SymbolKind.VARIABLE) is not None

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

    def equals(self, other) -> bool:
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        """
        if not isinstance(other, ASTNeuron):
            return False
        return self.get_name() == other.get_name() and self.get_body().equals(other.get_body())
