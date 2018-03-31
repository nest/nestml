#
# TransformerBase.py
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

from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from pynestml.modelprocessor.ASTBlock import ASTBlock
from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.utils.ASTCreator import ASTCreator
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.OdeTransformer import OdeTransformer


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
    try:
        tmp = ModelParser.parseExpression(init_expression)
        vector_variable = ASTUtils.getVectorizedVariable(tmp, neuron.getScope())

        declaration_string = variable_name + ' real' + (
            '[' + vector_variable.getVectorParameter() + ']'
            if vector_variable is not None and vector_variable.hasVectorParameter() else '') + ' = ' + init_expression
        ast_declaration = ModelParser.parseDeclaration(declaration_string)
        if vector_variable is not None:
            ast_declaration.setSizeParameter(vector_variable.getVectorParameter())
        neuron.addToInternalBlock(ast_declaration)
        return neuron

    except:
        raise RuntimeError('Must not fail by construction.')


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
    try:

        tmp = ModelParser.parseExpression(initial_value)
        vector_variable = ASTUtils.getVectorizedVariable(tmp, neuron.getScope())
        declaration_string = variable + ' real' + (
            '[' + vector_variable.getVectorParameter() + ']'
            if vector_variable is not None and vector_variable.hasVectorParameter() else '') + ' = ' + initial_value
        ast_declaration = ModelParser.parseDeclaration(declaration_string)
        if vector_variable is not None:
            ast_declaration.setSizeParameter(vector_variable.getVectorParameter())
        neuron.addToInitialValuesBlock(ast_declaration)
        return neuron
    except:
        raise RuntimeError('Must not fail by construction.')


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
    integrate_call = ASTUtils.getFunctionCall(neuron.getUpdateBlocks(), PredefinedFunctions.INTEGRATE_ODES)
    # by construction of a valid neuron, only a single integrate call should be there
    if isinstance(integrate_call, list):
        integrate_call = integrate_call[0]
    if integrate_call is not None:
        small_statement = neuron.getParent(integrate_call)
        assert (small_statement is not None and isinstance(small_statement, ASTSmallStmt))

        block = neuron.getParent(small_statement)
        assert (block is not None and isinstance(block, ASTBlock))

        for i in range(0, len(block.getStmts())):
            if block.getStmts()[i].equals(small_statement):
                del block.getStmts()[i]
                block.getStmts()[i:i] = list((ASTCreator.createStatement(prop) for prop in update_instructions))
                break
    return neuron


def applyIncomingSpikes(_neuron=None):
    """
    Adds a set of update instructions to the handed over neuron.
    :param _neuron: a single neuron instance
    :type _neuron: ASTNeuron
    :return: the modified neuron
    :rtype: ASTNeuron
    """
    assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
        '(PyNestML.Solver.BaseTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
    convCalls = OdeTransformer.get_sumFunctionCalls(_neuron)
    printer = ExpressionsPrettyPrinter()
    spikesUpdates = list()
    for convCall in convCalls:
        shape = convCall.getArgs()[0].getVariable().getCompleteName()
        buffer = convCall.getArgs()[1].getVariable().getCompleteName()
        initialValues = (_neuron.get_initial_values_blocks().getDeclarations()
                         if _neuron.get_initial_values_blocks() is not None else list())
        for astDeclaration in initialValues:
            for variable in astDeclaration.getVariables():
                if re.match(shape + "[\']*", variable.getCompleteName()) or re.match(shape + '__[\\d]+$',
                                                                                     variable.getCompleteName()):
                    spikesUpdates.append(ASTCreator.createAssignment(
                        variable.getCompleteName() + " += " + buffer + " * " + printer.printExpression(
                            astDeclaration.getExpression())))
    for update in spikesUpdates:
        add_assignment_to_update_block(update, _neuron)
    return _neuron


def add_assignment_to_update_block(assignment, neuron):
    """
    Adds a single assignment to the end of the update block of the handed over neuron.
    :param assignment: a single assignment
    :param neuron: a single neuron instance
    :return: the modified neuron
    """
    small_stmt = ASTSmallStmt(_assignment=assignment, _sourcePosition=ASTSourcePosition.getAddedSourcePosition())
    neuron.getUpdateBlocks().getBlock().getStmts().append(small_stmt)
    return neuron


def add_declaration_to_update_block(declaration, neuron):
    # type: (ASTDeclaration, ASTNeuron) -> ASTNeuron
    """
    Adds a single declaration to the end of the update block of the handed over neuron.
    :param declaration: ASTDeclaration node to add
    :param neuron: a single neuron instance
    :return: a modified neuron
    """
    small_stmt = ASTSmallStmt(_declaration=declaration, _sourcePosition=ASTSourcePosition.getAddedSourcePosition())
    neuron.getUpdateBlocks().getBlock().getStmts().append(small_stmt)
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
        add_declaration_to_update_block(ASTCreator.createDeclaration(declaration_statement), neuron)

    for variable in state_shape_variables_updates:
        add_assignment_to_update_block(ASTCreator.createAssignment(variable + ' = ' + variable + '__tmp'), neuron)
    return neuron