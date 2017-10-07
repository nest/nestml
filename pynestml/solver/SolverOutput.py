#
# SolverOutput.py
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
import json


class SolverOutput(object):
    """
    Encapsulates solver response. Contains the following fields: status (failed, success), initial_values,
    ode_var_update_instructions, solver, ode_var_factor, const_input, propagator_elements,shape_state_variables
    """
    status = ''
    initial_values = None
    ode_var_update_instructions = None
    solver = ''
    ode_var_factor = ''
    const_input = ''
    propagator_elements = ''
    shape_state_variables = list()
    updates_to_shape_state_variables = list()
    shape_state_odes = list()

    @classmethod
    def getErrorResult(cls):
        """
        Returns an error result.
        :return: an object of solver output type.
        :rtype: SolverOutput
        """
        solver = cls()
        solver.status = 'failed'
        return solver

    def fromJSON(self, _solverResult=None):
        """
        Creates an output from the handed over solver result.
        :param _solverResult: the solver result
        :type _solverResult:  str
        """
        result = json.load(_solverResult)
        for instruction in result['ode_var_update_instructions']:
            self.ode_var_update_instructions.append(instruction)
        for element in result['propagator_elements']:
            self.propagator_elements.append(element)
        for state in result['shape_state_odes']:
            self.shape_state_odes.append(state)
        for initValue in result['initial_values']:
