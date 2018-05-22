#
# solution_transformers.py
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
import re

from sympy import simplify, diff, Symbol, exp
from sympy.parsing.sympy_parser import parse_expr

from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_ode_shape import ASTOdeShape
from pynestml.solver.transformer_base import add_declarations_to_internals, \
    compute_state_shape_variables_declarations, add_declarations_to_initial_values, \
    compute_state_shape_variables_updates, replace_integrate_call, add_state_updates
from pynestml.utils.model_parser import ModelParser


def integrate_delta_solution(equations_block, neuron, shape, shape_to_buffers):
    def ode_is_lin_const_coeff(ode_symbol, ode_definition, shapes):
        """
        TODO: improve the original code: the function should take a list of shape names, not objects
        :param ode_symbol string encoding the LHS
        :param ode_definition string encoding RHS
        :param shapes A list with shape names
        :return true iff the ode definition is a linear and constant coefficient ODE
        """

        ode_symbol_sp = parse_expr(ode_symbol)
        ode_definition_sp = parse_expr(ode_definition)

        # Check linearity
        ddvar = diff(diff(ode_definition_sp, ode_symbol_sp), ode_symbol_sp)

        if simplify(ddvar) != 0:
            return False

        # Check coefficients
        dvar = diff(ode_definition_sp, ode_symbol_sp)

        for shape in shapes:
            for symbol in dvar.free_symbols:
                if shape == str(symbol):
                    return False
        return True

    ode_lhs = str(equations_block.get_ode_equations()[0].get_lhs().get_name())
    ode_rhs = str(equations_block.get_ode_equations()[0].get_rhs())
    shape_name = shape.get_variable().get_name()
    if not (ode_is_lin_const_coeff(ode_lhs, ode_rhs, [shape_name])):
        raise Exception("Cannot handle delta shape in a not linear constant coefficient ODE.")
    ode_lhs = parse_expr(ode_lhs)
    ode_rhs = parse_expr(ode_rhs)
    # constant input
    const_input = simplify(1 / diff(ode_rhs, parse_expr(shape_name)) *
                           (ode_rhs - diff(ode_rhs, ode_lhs) * ode_lhs) - (parse_expr(shape_name)))
    # ode var factor
    c1 = diff(ode_rhs, ode_lhs)
    # The symbol must be declared again. Otherwise, the right hand side will be used for the derivative
    c2 = diff(ode_rhs, parse_expr(shape_name))
    # tau is passed as the second argument of the 'delta' function
    tau_constant = parse_expr(str(shape.get_expression().get_function_call().get_args()[1]))
    ode_var_factor = exp(-Symbol('__h') / tau_constant)
    ode_var_update_instructions = [
        str(ode_lhs) + " = " + str(ode_var_factor * ode_lhs),
        str(ode_lhs) + " += " + str(simplify(c2 / c1 * (exp(Symbol('__h') * c1) - 1)) * const_input)]
    for k in shape_to_buffers:
        ode_var_update_instructions.append(str(ode_lhs) + " += " + shape_to_buffers[k])
    neuron.add_to_internal_block(ModelParser.parse_declaration('__h ms = resolution()'))
    replace_integrate_call(neuron, ode_var_update_instructions)
    return neuron


def integrate_exact_solution(neuron, exact_solution):
    # type: (ASTNeuron, map[str, list]) -> ASTNeuron
    """
    Adds a set of instructions to the given neuron as stated in the solver output.
    :param neuron: a single neuron instance
    :param exact_solution: exact solution
    :return: a modified neuron with integrated exact solution and without equations block
    """
    neuron.add_to_internal_block(ModelParser.parse_declaration('__h ms = resolution()'))
    neuron = add_declarations_to_internals(neuron, exact_solution["propagator"])

    state_shape_variables_declarations = compute_state_shape_variables_declarations(exact_solution)
    neuron = add_declarations_to_initial_values(neuron, state_shape_variables_declarations)

    state_shape_variables_updates = compute_state_shape_variables_updates(exact_solution)
    neuron = add_state_updates(state_shape_variables_updates, neuron)

    neuron = replace_integrate_call(neuron, exact_solution["ode_updates"])

    return neuron


def functional_shapes_to_odes(neuron, transformed_shapes):
    # type: (ASTNeuron, map[str, list]) -> ASTNeuron
    """
    Adds a set of instructions to the given neuron as stated in the solver output.
    :param neuron: a single neuron instance
    :param transformed_shapes: ode-toolbox output that encodes transformation of functional shapes to odes with IV
    :return: the source neuron with modified equations block without functional shapes
    """
    shape_names, shape_name_to_initial_values, shape_name_to_shape_state_variables, shape_state_variable_to_ode = \
        _convert_to_shape_specific(transformed_shapes)

    # delete original functions shapes. they will be replaced though ode-shapes computed through ode-toolbox.
    shapes_to_delete = []  # you should not delete elements from list during iterating the list
    for declaration in neuron.get_equations_block().get_declarations():
        if isinstance(declaration, ASTOdeShape):
            if declaration.get_variable().get_name() in shape_names:
                shapes_to_delete.append(declaration)
    for declaration in shapes_to_delete:
        neuron.get_equations_block().get_declarations().remove(declaration)

    state_shape_variables_declarations = {}
    for shape_name in shape_names:
        for variable, initial_value in zip(
                shape_name_to_shape_state_variables[shape_name],
                shape_name_to_initial_values[shape_name]):
            state_shape_variables_declarations[variable] = initial_value

        for variable, shape_state_ode in zip(
                shape_name_to_shape_state_variables[shape_name],
                shape_state_variable_to_ode[shape_name]):
            ode_shape = ModelParser.parse_ode_shape("shape " + variable + "' = " + shape_state_ode)
            neuron.add_shape(ode_shape)

    neuron = add_declarations_to_initial_values(neuron, state_shape_variables_declarations)

    return neuron


def _convert_to_shape_specific(transformed_shapes):
    """

    :param transformed_shapes: example input fo the alpha shape
    {
     'solver': 'numeric',
     'shape_ode_definitions': ['-1/tau_syn_in**2 * g_in + -2/tau_syn_in * g_in__d', '-1/tau_syn_ex**2 * g_ex +
                                -2/tau_syn_ex * g_ex__d'],
     'shape_state_variables': ['g_in__d', 'g_in', 'g_ex__d', 'g_ex'],
     'shape_initial_values': ['0', 'e*nS/tau_syn_in', '0', 'e*nS/tau_syn_ex'], # wrong order
    }
    :return:
    """
    shape_names = []
    for shape_state_variable in transformed_shapes["shape_state_variables"]:
        if '__' not in shape_state_variable:
            shape_names.append(shape_state_variable)
    shape_name_to_shape_state_variables = {}
    shape_name_to_initial_values = {}
    shape_state_variable_to_ode = {}
    working_index_variables = 0
    working_index_odes = 0
    for shape_name in shape_names:
        matcher_shape = re.compile(shape_name + r"(__\d+)?")
        initial_values = []
        shape_state_variables = []
        shape_state_odes = []

        while working_index_variables < len(transformed_shapes["shape_state_variables"]) and \
                matcher_shape.match(transformed_shapes["shape_state_variables"][working_index_variables]):
            initial_values.append(transformed_shapes["shape_initial_values"][
                                      working_index_variables])  # currently these variables are dis-ordered. fix it.
            shape_state_variables = [transformed_shapes["shape_state_variables"][
                                         working_index_variables]] + shape_state_variables
            shape_state_odes.append(transformed_shapes["shape_state_variables"][working_index_variables])
            working_index_variables = working_index_variables + 1
        shape_state_odes[len(shape_state_odes) - 1] = transformed_shapes["shape_ode_definitions"][working_index_odes]
        working_index_odes = working_index_odes + 1

        shape_name_to_shape_state_variables[shape_name] = shape_state_variables
        shape_name_to_initial_values[shape_name] = initial_values
        shape_state_variable_to_ode[shape_name] = shape_state_odes
    return shape_names, shape_name_to_initial_values, shape_name_to_shape_state_variables, shape_state_variable_to_ode
