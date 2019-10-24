#
# transformer_base.py
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
import re as re

from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.symbols.variable_symbol import BlockType
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.meta_model.ast_source_location import ASTSourceLocation
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.ode_transformer import OdeTransformer


def add_declarations_to_internals(neuron, declarations):
    # type: (ASTNeuron, dict[str, str]) -> ASTNeuron
    """
    Adds the variables as stored in the declaration tuples to the neuron.
    :param neuron: a single neuron instance
    :param declarations: a list of declaration tuples
    :return: a modified neuron
    """
    for variable in declarations:
        add_declaration_to_internals(neuron, variable, declarations[variable])
    return neuron


def add_declaration_to_internals(neuron, variable_name, init_expression):
    # type: (ASTNeuron,  str, str) -> ASTNeuron
    """
    Adds the variable as stored in the declaration tuple to the neuron. The declared variable is of type real.
    :param neuron: a single neuron instance
    :param variable_name: the name of the variable to add
    :param init_expression: initialization expression
    :return: the neuron extended by the variable
    """
    tmp = ModelParser.parse_expression(init_expression)
    vector_variable = ASTUtils.get_vectorized_variable(tmp, neuron.get_scope())

    declaration_string = variable_name + ' real' + (
        '[' + vector_variable.get_vector_parameter() + ']'
        if vector_variable is not None and vector_variable.has_vector_parameter() else '') + ' = ' + init_expression
    ast_declaration = ModelParser.parse_declaration(declaration_string)
    if vector_variable is not None:
        ast_declaration.set_size_parameter(vector_variable.get_vector_parameter())
    neuron.add_to_internal_block(ast_declaration)
    ast_declaration.update_scope(neuron.get_internals_blocks().get_scope())
    symtable_visitor = ASTSymbolTableVisitor()
    symtable_visitor.block_type_stack.push(BlockType.INTERNALS)
    ast_declaration.accept(symtable_visitor)
    symtable_visitor.block_type_stack.pop()
    return neuron


def add_declarations_to_initial_values(neuron, variables, initial_values):
    # type: (ASTNeuron, map(str, str)) -> ASTNeuron
    """
    Adds a single declaration to the initial values block of the neuron.
    :param neuron: a neuron
    :param declarations: a single
    :return: a modified neuron
    """
    for variable, initial_value in zip(variables, initial_values):
        add_declaration_to_initial_values(neuron, variable, initial_value)
    return neuron


def add_declaration_to_initial_values(neuron, variable: str, initial_value: str):
    # type: (ASTNeuron, str, str) -> ASTNeuron
    """
    Adds a single declaration to the initial values block of the neuron. The declared variable is of type real.
    :param neuron: a neuron
    :param variable: state variable to add
    :param initial_value: corresponding initial value
    :return: a modified neuron
    """
    tmp = ModelParser.parse_expression(initial_value)
    vector_variable = ASTUtils.get_vectorized_variable(tmp, neuron.get_scope())
    declaration_string = variable + ' real' + (
        '[' + vector_variable.get_vector_parameter() + ']'
        if vector_variable is not None and vector_variable.has_vector_parameter() else '') + ' = ' + initial_value
    ast_declaration = ModelParser.parse_declaration(declaration_string)
    if vector_variable is not None:
        ast_declaration.set_size_parameter(vector_variable.get_vector_parameter())
    neuron.add_to_initial_values_block(ast_declaration)
    ast_declaration.update_scope(neuron.get_initial_values_blocks().get_scope())

    symtable_visitor = ASTSymbolTableVisitor()
    symtable_visitor.block_type_stack.push(BlockType.INITIAL_VALUES)
    ast_declaration.accept(symtable_visitor)
    symtable_visitor.block_type_stack.pop()

    return neuron


def declaration_in_initial_values(neuron, variable_name):
    assert type(variable_name) is str

    for decl in neuron.get_initial_values_blocks().get_declarations():
        for var in decl.get_variables():
            if var.get_complete_name() == variable_name:
                return True

    return False


def apply_incoming_spikes(neuron):
    """
    Adds a set of update instructions to the handed over neuron.
    :param neuron: a single neuron instance
    :type neuron: ASTNeuron
    :return: the modified neuron
    :rtype: ASTNeuron
    """
    assert (neuron is not None and isinstance(neuron, ASTNeuron)), \
        '(PyNestML.Solver.BaseTransformer) No or wrong type of neuron provided (%s)!' % type(neuron)
    conv_calls = OdeTransformer.get_sum_function_calls(neuron)
    printer = ExpressionsPrettyPrinter()
    spikes_updates = list()
    for convCall in conv_calls:
        shape = convCall.get_args()[0].get_variable().get_complete_name()
        buffer = convCall.get_args()[1].get_variable().get_complete_name()
        initial_values = (
            neuron.get_initial_values_blocks().get_declarations() if neuron.get_initial_values_blocks() is not None else list())
        for astDeclaration in initial_values:
            for variable in astDeclaration.get_variables():
                if re.match(shape + "[\']*", variable.get_complete_name()) or re.match(shape + '__[\\d]+$',
                                                                                       variable.get_complete_name()):
                    spikes_updates.append(ModelParser.parse_assignment(
                        variable.get_complete_name() + " += " + buffer + " * " + printer.print_expression(
                            astDeclaration.get_expression())))
    for update in spikes_updates:
        add_assignment_to_update_block(update, neuron)
    return neuron


def add_assignment_to_update_block(assignment, neuron):
    """
    Adds a single assignment to the end of the update block of the handed over neuron.
    :param assignment: a single assignment
    :param neuron: a single neuron instance
    :return: the modified neuron
    """
    small_stmt = ASTNodeFactory.create_ast_small_stmt(assignment=assignment,
                                                      source_position=ASTSourceLocation.get_added_source_position())
    stmt = ASTNodeFactory.create_ast_stmt(small_stmt=small_stmt,
                                          source_position=ASTSourceLocation.get_added_source_position())
    neuron.get_update_blocks().get_block().get_stmts().append(stmt)
    small_stmt.update_scope(neuron.get_update_blocks().get_block().get_scope())
    stmt.update_scope(neuron.get_update_blocks().get_block().get_scope())
    return neuron


def add_declaration_to_update_block(declaration, neuron):
    # type: (ASTDeclaration, ASTNeuron) -> ASTNeuron
    """
    Adds a single declaration to the end of the update block of the handed over neuron.
    :param declaration: ASTDeclaration node to add
    :param neuron: a single neuron instance
    :return: a modified neuron
    """
    small_stmt = ASTNodeFactory.create_ast_small_stmt(declaration=declaration,
                                                      source_position=ASTSourceLocation.get_added_source_position())
    stmt = ASTNodeFactory.create_ast_stmt(small_stmt=small_stmt,
                                          source_position=ASTSourceLocation.get_added_source_position())
    neuron.get_update_blocks().get_block().get_stmts().append(stmt)
    small_stmt.update_scope(neuron.get_update_blocks().get_block().get_scope())
    stmt.update_scope(neuron.get_update_blocks().get_block().get_scope())
    return neuron


def add_state_updates(neuron, update_expressions):
    # type: (map[str, str], ASTNeuron) -> ASTNeuron
    """
    Adds all update instructions as contained in the solver output to the update block of the neuron.
    :param state_shape_variables_updates: map of variables to corresponding updates during the update step.
    :param neuron: a single neuron
    :return: a modified version of the neuron
    """
    for variable, update_expression in update_expressions.items():
        declaration_statement = variable + '__tmp real = ' + update_expression
        add_declaration_to_update_block(ModelParser.parse_declaration(declaration_statement), neuron)
    for variable, update_expression in update_expressions.items():
        add_assignment_to_update_block(ModelParser.parse_assignment(variable + ' = ' + variable + '__tmp'), neuron)
    return neuron
