# -*- coding: utf-8 -*-
#
# ast_model.py
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

from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_on_condition_block import ASTOnConditionBlock
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_output_block import ASTOutputBlock
from pynestml.meta_model.ast_model_body import ASTModelBody
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.symbols.variable_symbol import BlockType, VariableSymbol
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.utils.ast_source_location import ASTSourceLocation


class ASTModel(ASTNode):
    r"""
    This class is used to stuff common to neurons and synapses
    """

    def __init__(self, name: str, body: ASTModelBody, artifact_name=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param name: the name of the model.
        :param body: the body containing the definitions.
        :param source_position: the position of this element in the source file.
        :param artifact_name: the name of the file this neuron is contained in
        """
        super(ASTModel, self).__init__(*args, **kwargs)
        assert isinstance(name, str), \
            'No or wrong type of model name provided (%s)!' % type(name)
        assert isinstance(body, ASTModelBody) or isinstance(body, ASTModelBody), \
            'No or wrong type of model body provided (%s)!' % type(body)
        assert (artifact_name is not None and isinstance(artifact_name, str)), \
            'No or wrong type of artifact name provided (%s)!' % type(artifact_name)

        self.name = name
        self.body = body
        self.artifact_name = artifact_name

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTModel
        """
        dup = ASTModel(name=self.name,
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

    def get_name(self) -> str:
        """
        Returns the name of the model.
        :return: the name of the model.
        """
        return self.name

    def set_name(self, name):
        """
        Set the name of the model.
        """
        self.name = name

    def get_body(self) -> ASTModelBody:
        """
        Return the body of the model.
        :return: the model body
        """
        return self.body

    def get_artifact_name(self) -> str:
        """
        Returns the name of the artifact this model has been stored in.
        :return: the name of the file
        """
        return self.artifact_name

    def get_functions(self) -> List[ASTFunction]:
        """
        Returns a list of all function block declarations in this body.
        :return: a list of function declarations.
        """
        ret = list()
        from pynestml.meta_model.ast_function import ASTFunction
        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTFunction):
                ret.append(elem)
        return ret

    def get_state_blocks(self) -> List[ASTBlockWithVariables]:
        """
        Returns a list of all state blocks defined in this body.
        :return: a list of state-blocks.
        """
        return self.get_body().get_state_blocks()

    def get_parameters_blocks(self) -> List[ASTBlockWithVariables]:
        """
        Returns a list of all parameter blocks defined in this body.
        :return: a list of parameters-blocks.
        """
        return self.get_body().get_parameters_blocks()

    def get_internals_blocks(self) -> List[ASTBlockWithVariables]:
        """
        Returns a list of all internals blocks defined in this body.
        :return: a list of internals-blocks.
        """
        return self.get_body().get_internals_blocks()

    def get_equations_blocks(self) -> List[ASTEquationsBlock]:
        """
        Returns a list of all ``equations`` blocks defined in this body.
        :return: a list of equations-blocks.
        """
        return self.get_body().get_equations_blocks()

    def get_update_blocks(self) -> List[ASTUpdateBlock]:
        """
        Returns a list of all update blocks defined in this body.
        :return: a list of update-block elements.
        """
        return self.get_body().get_update_blocks()

    def remove_equations_block(self) -> None:
        """
        Deletes all equations blocks. By construction as checked through cocos there is only one there.
        """

        for elem in self.get_body().get_body_elements():
            if isinstance(elem, ASTEquationsBlock):
                self.get_body().get_body_elements().remove(elem)

    def get_state_declarations(self):
        """
        Returns a list of initial values declarations made in this neuron.
        :return: a list of initial values declarations
        :rtype: list(ASTDeclaration)
        """
        initial_values_declarations = list()
        for state_block in self.get_state_blocks():
            for decl in state_block.get_declarations():
                initial_values_declarations.append(decl)

        return initial_values_declarations

    def get_equations(self) -> List[ASTOdeEquation]:
        """
        Returns all ode equations as defined in this neuron.
        :return list of ode-equations
        """
        ret = list()

        for block in self.get_equations_blocks():
            ret.extend(block.get_ode_equations())

        return ret

    def get_input_blocks(self) -> List[ASTInputBlock]:
        """
        Returns a list of all input-blocks defined.
        :return: a list of defined input-blocks.
        """
        return self.get_body().get_input_blocks()

    def get_output_blocks(self) -> List[ASTOutputBlock]:
        """
        Returns a list of all output-blocks defined.
        :return: a list of defined output-blocks.
        """
        return self.get_body().get_output_blocks()

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
                if type(decl) is ASTKernel and kernel_name in [s.replace("$", "__DOLLAR").replace("'", "") for s in decl.get_variable_names()]:
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

    def get_parameter_variables(self) -> List[ASTVariable]:
        """
        Returns a list of all parameters.
        :return:
        """
        ret = []
        blocks = set(self.get_parameters_blocks())
        if not isinstance(blocks, list):
            blocks = [blocks]
        for block in blocks:
            for decl in block.get_declarations():
                ret.extend(decl.get_variables())
        return ret

    def get_state_variables(self) -> List[ASTVariable]:
        """
        Returns a list of all state variables.
        :return:
        """
        ret = []
        for block in self.get_state_blocks():
            for decl in block.get_declarations():
                ret.extend(decl.get_variables())

        return ret

    def create_empty_update_block(self):
        """
        Create an empty update block. Only makes sense if one does not already exist.
        """
        assert not self.get_update_blocks(), "create_empty_update_block() called although update block already present"
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        block = ASTNodeFactory.create_ast_stmts_body([], ASTSourceLocation.get_predefined_source_position())
        update_block = ASTNodeFactory.create_ast_update_block(block, ASTSourceLocation.get_predefined_source_position())
        self.get_body().get_body_elements().append(update_block)

    def add_to_internals_block(self, declaration: ASTDeclaration, index: int = -1) -> None:
        """
        Adds the handed over declaration the internals block
        :param declaration: a single declaration
        """
        from pynestml.utils.ast_utils import ASTUtils
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor

        assert len(self.get_internals_blocks()) <= 1, "Only one internals block supported for now"

        if not self.get_internals_blocks():
            ASTUtils.create_internal_block(self)

        n_declarations = len(self.get_internals_blocks()[0].get_declarations())
        if n_declarations == 0:
            index = 0
        else:
            index = 1 + (index % len(self.get_internals_blocks()[0].get_declarations()))

        self.get_internals_blocks()[0].get_declarations().insert(index, declaration)
        declaration.update_scope(self.get_internals_blocks()[0].get_scope())
        symtable_vistor = ASTSymbolTableVisitor()
        symtable_vistor.block_type_stack.push(BlockType.INTERNALS)
        self.accept(ASTParentVisitor())
        self.accept(symtable_vistor)
        symtable_vistor.block_type_stack.pop()

    def add_to_state_block(self, declaration: ASTDeclaration) -> None:
        """
        Adds the handed over declaration to an arbitrary state block. A state block will be created if none exists.
        :param declaration: a single declaration.
        """
        from pynestml.symbols.symbol import SymbolKind
        from pynestml.utils.ast_utils import ASTUtils
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        from pynestml.visitors.ast_parent_visitor import ASTParentVisitor

        assert len(self.get_state_blocks()) <= 1, "Only one internals block supported for now"

        if not self.get_state_blocks():
            ASTUtils.create_state_block(self)

        self.get_state_blocks()[0].get_declarations().append(declaration)
        declaration.update_scope(self.get_state_blocks()[0].get_scope())
        symtable_vistor = ASTSymbolTableVisitor()
        symtable_vistor.block_type_stack.push(BlockType.STATE)
        self.accept(ASTParentVisitor())
        self.accept(symtable_vistor)
        symtable_vistor.block_type_stack.pop()

        assert declaration.get_variables()[0].get_scope().resolve_to_symbol(declaration.get_variables()[0].get_name(), SymbolKind.VARIABLE) is not None
        assert declaration.get_scope().resolve_to_symbol(declaration.get_variables()[0].get_name(), SymbolKind.VARIABLE) is not None

    def print_comment(self, prefix: str = "") -> str:
        """
        Prints the header comment of this neuron.
        :param prefix: a prefix string
        :return: the comment.
        """
        if self.get_comment() is None or len(self.get_comment()) == 0:
            return prefix

        ret = ''
        for comment in self.get_comment():
            ret += prefix + comment + '\n'

        return ret

    def get_initial_value(self, variable_name: str):
        assert type(variable_name) is str

        for state_block in self.get_state_blocks():
            for decl in state_block.get_declarations():
                for var in decl.variables:
                    if var.get_complete_name() == variable_name:
                        return decl.get_expression()

        return None

    def has_delay_variables(self) -> bool:
        """
        This method indicates if the neuron has variables with a delay parameter.
        :return: True if variables with delay parameter exist, False otherwise.
        """
        state_symbols = self.get_state_symbols()
        for symbol in state_symbols:
            if symbol.has_delay_parameter():
                return True

        return False

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

    def get_spike_input_port_names(self) -> List[str]:
        """
        Returns a list of all spike input ports defined in the model.
        """
        return [port.get_symbol_name() for port in self.get_spike_input_ports()]

    def get_continuous_input_ports(self) -> List[VariableSymbol]:
        """
        Returns a list of all continuous time input ports defined in the model.
        """
        ret = list()
        for port in self.get_input_ports():
            if port.is_continuous_input_port():
                ret.append(port)
        return ret

    def get_continuous_input_port_names(self) -> List[str]:
        """
        Returns a list of all continuous time input ports defined in the model.
        """
        return [port.get_symbol_name() for port in self.get_continuous_input_ports()]

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

    def get_on_receive_blocks(self) -> List[ASTOnReceiveBlock]:
        if not self.get_body():
            return []
        return self.get_body().get_on_receive_blocks()

    def get_on_receive_block(self, port_name: str) -> Optional[ASTOnReceiveBlock]:
        if not self.get_body():
            return None

        return self.get_body().get_on_receive_block(port_name)

    def get_on_condition_blocks(self) -> List[ASTOnConditionBlock]:
        if not self.get_body():
            return []

        return self.get_body().get_on_condition_blocks()

    def get_input_buffers(self):
        """
        Returns a list of all defined input buffers.
        :return: a list of all input buffers.
        :rtype: list(VariableSymbol)
        """
        symbols = self.get_scope().get_symbols_in_this_scope()
        ret = list()
        for symbol in symbols:
            if isinstance(symbol, VariableSymbol) and (symbol.block_type == BlockType.INPUT_BUFFER_SPIKE
                                                       or symbol.block_type == BlockType.INPUT_BUFFER_CURRENT):
                ret.append(symbol)
        return ret

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        return [self.get_body()]

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTModel):
            return False
        return self.get_name() == other.get_name() and self.get_body().equals(other.get_body())
