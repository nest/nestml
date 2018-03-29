#
# DeltaSolutionTransformer.py
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
from pynestml.solver.SolverOutput import SolverOutput
from pynestml.solver.TransformerBase import TransformerBase
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter


class DeltaSolutionTransformer(TransformerBase):
    """
    This class contains a set of methods as used to add solutions to a handed over neuron.
    """

    @classmethod
    def addExactSolution(cls, _solverOutput=None, _neuron=None):
        """
        Adds the exact solution as computed by the solver to the neuron.
        :param _solverOutput: a single solver output object
        :type _solverOutput: SolverOutput
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        :return: the modified neuron
        :rtype: ASTNeuron
        """
        assert (_solverOutput is not None and isinstance(_solverOutput, SolverOutput)), \
            '(PyNestML.Solver.DeltaSolution) No or wrong type of output provided (%s)!' % _solverOutput
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.DeltaSolution) No or wrong type of neuron provided (%s)!' % _neuron
        _neuron.addToInternalBlock(ModelParser.parseDeclaration('__h ms = resolution()'))
        TransformerBase.addVariableToInternals(_neuron, _solverOutput.const_input)
        TransformerBase.addVariableToInternals(_neuron, _solverOutput.ode_var_factor)
        i_sum_calls = [func for func in ASTUtils.getAll(_neuron.getEquationsBlocks(), ASTFunctionCall)
                       if func.getName() == PredefinedFunctions.CURR_SUM]
        expression_printer = ExpressionsPrettyPrinter()
        # now apply spikes from the buffer to the state variables
        for call in i_sum_calls:
            buffer_name = expression_printer.printExpression(call.getArgs()[1])
            _solverOutput.ode_var_update_instructions.append(
                _neuron.getEquations()[0].getLhs().getName() + '+=' + buffer_name)

        _neuron = TransformerBase.replaceIntegrateCallThroughPropagation(_neuron, _solverOutput.const_input,
                                                                         _solverOutput.ode_var_update_instructions)
        return _neuron
