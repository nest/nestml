#
# ExactSolutionTransformer.py
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
from pynestml.meta_model.ASTNeuron import ASTNeuron
from pynestml.solver.SolverOutput import SolverOutput
from pynestml.solver.TransformerBase import TransformerBase
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.ModelParser import ModelParser


class ExactSolutionTransformer(object):
    """
    Takes SymPy result with the linear solution of the ODE and the source AST.
    Produces an altered AST with the the exact solution.
    """

    @classmethod
    def addExactSolution(cls, _neuron=None, _solverOutput=None):
        """
        Adds a set of instructions to the given neuron as stated in the solver output.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :param _solverOutput: the generated solver output
        :type _solverOutput: SolverOutput
        :return: a modified neuron
        :rtype: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.ExactSolutionTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
        assert (_solverOutput is not None and isinstance(_solverOutput, SolverOutput)), \
            '(PyNestML.Solver.ExactSolutionTransformer) No or wrong type of solver output provided (%s)!' % type(
                _solverOutput)
        working_version = _neuron
        working_version.addToInternalBlock(ModelParser.parse_declaration('__h ms = resolution()'))
        working_version = TransformerBase.addVariableToInternals(working_version, _solverOutput.ode_var_factor)
        working_version = TransformerBase.addVariableToInternals(working_version, _solverOutput.const_input)
        working_version = TransformerBase.addVariablesToInternals(working_version, _solverOutput.propagator_elements)

        state_shape_variables_with_initial_values = TransformerBase.computeShapeStateVariablesWithInitialValues(
            _solverOutput)
        # copy initial block variables to the state block, since they are not backed through an ODE.
        for decl in _neuron.get_initial_values_declarations():
            _neuron.addToStateBlock(decl)
        working_version = TransformerBase.addVariablesToInitialValues(working_version,
                                                                      state_shape_variables_with_initial_values)
        cls.__addStateUpdates(_solverOutput, working_version)

        working_version = TransformerBase.replaceIntegrateCallThroughPropagation(working_version,
                                                                                 _solverOutput.const_input,
                                                                                 _solverOutput.ode_var_update_instructions)
        TransformerBase.applyIncomingSpikes(working_version)
        # get rid of the ODE stuff since the model is solved exactly and all ODEs are removed.
        working_version.get_equations_blocks().clear()

        for variable in state_shape_variables_with_initial_values:
            _neuron.addToStateBlock(ModelParser.parse_declaration(variable[0] + ' real'))

        if working_version.get_initial_blocks() is not None:
            working_version.get_initial_blocks().clear()
        return working_version

    @classmethod
    def __addStateUpdates(cls, _solverOutput=None, _neuron=None):
        """
        Adds all update instructions as contained in the solver output to the update block of the neuron.
        :param _solverOutput: a solver output
        :type _solverOutput: SolverOutput
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        :return: a modified version of the neuron
        :rtype: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.ExactSolutionTransformer) No or wrong type of neuron provided (%s)!' % type(_neuron)
        assert (_solverOutput is not None and isinstance(_solverOutput, SolverOutput)), \
            '(PyNestML.Solver.ExactSolutionTransformer) No or wrong type of solver output provided (%s)!' % type(
                _solverOutput)
        temp_variables = list()
        for tup in _solverOutput.updates_to_shape_state_variables:
            key, value = ASTUtils.get_tuple_from_single_dict_entry(tup)
            if key.startswith('__tmp'):
                temp_variables.append(key)
        for var in temp_variables:
            TransformerBase.addDeclarationToUpdateBlock(ModelParser.parse_declaration(var + ' real'), _neuron)
        for out in _solverOutput.updates_to_shape_state_variables:
            key, value = ASTUtils.get_tuple_from_single_dict_entry(out)
            assignment = ModelParser.parse_assignment(key + ' = ' + value)
            TransformerBase.addAssignmentToUpdateBlock(assignment, _neuron)
        return
