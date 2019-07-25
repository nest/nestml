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
    add_declarations_to_initial_values
from pynestml.utils.model_parser import ModelParser


def integrate_exact_solution(neuron, solver_dict):
    # type: (ASTNeuron, map[str, list]) -> ASTNeuron
    """
    Adds declarations of state variables and initial value expressions to the AST, on the basis of an analytic solver dictionary returned from ode-toolbox.

    Note that the actual integration step takes place whenever `integrate_odes()` is called; refer to the corresponding Jinja template.

    Parameters
    -----------
    neuron: ASTNeuron
        An ASTNeuron instance. Will be modified.
    solver_dict: dict
        A dictionary returned by ode-toolbox analysis() call, such that solver_dict["solver"] == "analytical"

    Returns
    -------
    neuron : ASTNeuron
        the modified neuron with integrated exact solution
    """
    assert solver_dict["solver"] == "analytical"
    #neuron = add_declarations_to_internals(neuron, solver_dict["propagators"])
    #neuron = add_declarations_to_initial_values(neuron, solver_dict["state_variables"], solver_dict["initial_values"])

    return neuron


def functional_shapes_to_odes(neuron, transformed_shapes):
    # type: (ASTNeuron, map[str, list]) -> ASTNeuron
    """
    Adds a set of instructions to the given neuron as stated in the solver output.
    :param neuron: a single neuron instance
    :param transformed_shapes: ode-toolbox output that encodes transformation of functional shapes to odes with IV
    :return: the source neuron with modified equations block without functional shapes
    """

    # XXX: TODO
    #neuron = add_declarations_to_initial_values(neuron, state_shape_variables_declarations)

    return neuron
