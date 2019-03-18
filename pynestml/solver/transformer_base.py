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
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
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
    Adds the variable as stored in the declaration tuple to the neuron.
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
    return neuron


def add_declarations_to_initial_values(neuron, declarations):
    # type: (ASTNeuron, map(str, str)) -> ASTNeuron
    """
    Adds a single declaration to the initial values block of the neuron.
    :param neuron: a neuron
    :param declarations: a single
    :return: a modified neuron
    """
    for variable in declarations:
        add_declaration_to_initial_values(neuron, variable, declarations[variable])
    return neuron


def add_declaration_to_initial_values(neuron, variable, initial_value):
    # type: (ASTNeuron, str, str) -> ASTNeuron
    """
    Adds a single declaration to the initial values block of the neuron.
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
    return neuron


def compute_state_shape_variables_declarations(solver_output):
    # type: (...) -> map[str, str]
    """
    Computes a set of state variables with the corresponding set of initial values from the given solver output.
    :param solver_output: a single solver output dictionary
    :return: Map of variable names to corresponding initial values
    """
    initial_values = []
    for initial_value_for_shape in solver_output["shape_initial_values"]:
        initial_values += initial_value_for_shape

    shape_state_variables = []

    for single_shape in solver_output["shape_state_variables"]:
        shape_state_variables += reversed(single_shape)  # cf. issue #7 on github

    state_shape_declarations = {}
    for i in range(0, len(initial_values)):
        state_shape_declarations[shape_state_variables[i]] = initial_values[i]

    return state_shape_declarations


def compute_state_shape_variables_updates(solver_output):
    # type: (...) -> map[str, str]
    """
    Computes which expression must be used to update state shape variables in update block.
    :param solver_output: a single solver output dictionary
    :return: Map of variable names to update ex
    """
    shape_state_updates = []
    for shape_state_update in solver_output["shape_state_updates"]:
        shape_state_updates += shape_state_update

    shape_state_variables = []

    for single_shape in solver_output["shape_state_variables"]:
        shape_state_variables += (single_shape)  # cf. issue #7 on github

    state_shape_updates = {}
    for i in range(0, len(shape_state_updates)):
        state_shape_updates[shape_state_variables[i]] = shape_state_updates[i]

    return state_shape_updates


def replace_integrate_call(neuron, update_instructions):
    # type: (...) -> ASTNeuron
    """
    Replaces all integrate calls to the corresponding references to propagation.
    :param neuron: a single neuron instance
    :return: The neuron without an integrate calls. The function calls are replaced through an
             incremental exact solution,
    """
    integrate_call = ASTUtils.get_function_call(neuron.get_update_blocks(), PredefinedFunctions.INTEGRATE_ODES)
    # by construction of a valid neuron, only a single integrate call should be there
    if isinstance(integrate_call, list):
        integrate_call = integrate_call[0]
    if integrate_call is not None:
        small_statement = neuron.get_parent(integrate_call)
        assert (small_statement is not None and isinstance(small_statement, ASTSmallStmt))

        block = neuron.get_parent(neuron.get_parent(small_statement))
        assert (block is not None and isinstance(block, ASTBlock))

        for i in range(0, len(block.get_stmts())):
            if block.get_stmts()[i].equals(neuron.get_parent(small_statement)):
                del block.get_stmts()[i]
                block.get_stmts()[i:i] = list((ModelParser.parse_stmt(prop) for prop in update_instructions))
                break
    return neuron


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
    return neuron


def add_state_updates(state_shape_variables_updates, neuron):
    # type: (map[str, str], ASTNeuron) -> ASTNeuron
    """
    Adds all update instructions as contained in the solver output to the update block of the neuron.
    :param state_shape_variables_updates: map of variables to corresponding updates during the update step.
    :param neuron: a single neuron
    :return: a modified version of the neuron
    """
    for variable in state_shape_variables_updates:
        declaration_statement = variable + '__tmp real = ' + state_shape_variables_updates[variable]
        add_declaration_to_update_block(ModelParser.parse_declaration(declaration_statement), neuron)
    for variable in state_shape_variables_updates:
        add_assignment_to_update_block(ModelParser.parse_assignment(variable + ' = ' + variable + '__tmp'), neuron)
    return neuron
