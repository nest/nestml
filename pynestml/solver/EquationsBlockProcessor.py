#
# EquationsBlockProcessor.py
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
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.solver.SymPySolver import SymPySolver
from pynestml.solver.DeltaSolutionTransformer import DeltaSolutionTransformer
from pynestml.solver.ShapesToOdesTransformer import ShapesToOdesTransformer
from pynestml.utils.Messages import Messages
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from copy import deepcopy


class EquationsBlockProcessor(object):
    """
    This class contains several methods as used to solve shapes to sets of equations.
    """

    @classmethod
    def solveOdeWithShapes(cls, _neuron=None):
        """
        Solves the odes and shapes in the handed over neuron.
        :param _neuron: a neuron instance
        :type _neuron: ASTNeuron
        :return: the neuron with modified equation block
        :rtype: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.Solver.EquationsBlockProcessor) No or wrong type of neuron provided (%s)!' % _neuron
        # if no equations block is present, just return it
        if _neuron.getEquationsBlocks() is None:
            return _neuron
        else:
            workingCopy = deepcopy(_neuron)
            if len(workingCopy.getEquationsBlocks().getOdeShapes()) > 0 and \
                            len(workingCopy.getEquationsBlocks().getOdeEquations()) == 1:
                output = SymPySolver.solveOdeWithShapes(_neuron.getEquationsBlocks())
                if not output.status == 'success':
                    code, message = Messages.getCouldNotBeSolved()
                    Logger.logMessage(_neuron=_neuron,
                                      _message=message, _code=code,
                                      _errorPosition=_neuron.getEquationsBlocks().getSourcePosition(),
                                      _logLevel=LOGGING_LEVEL.INFO)
                    return _neuron
                if output.solver == 'exact':
                    code, message = Messages.getEquationsSolvedExactly()
                    Logger.logMessage(_neuron=_neuron,
                                      _message=message, _code=code,
                                      _errorPosition=_neuron.getEquationsBlocks().getSourcePosition(),
                                      _logLevel=LOGGING_LEVEL.INFO)

                elif output.solver == 'numeric':
                    code, message = Messages.getEquationsSolvedByGLS()
                    Logger.logMessage(_neuron=_neuron,
                                      _message=message, _code=code,
                                      _errorPosition=_neuron.getEquationsBlocks().getSourcePosition(),
                                      _logLevel=LOGGING_LEVEL.INFO)
                    _neuron = ShapesToOdesTransformer.transformShapesToOdeForm(_neuron=_neuron, _solverOutput=output)
                elif output.solver == 'delta':
                    return DeltaSolutionTransformer.addExactSolution(_solverOutput=output, _neuron=_neuron)
                else:
                    code, message = Messages.getCouldNotBeSolved()
                    Logger.logMessage(_neuron=_neuron,
                                      _message=message, _code=code,
                                      _errorPosition=_neuron.getEquationsBlocks().getSourcePosition(),
                                      _logLevel=LOGGING_LEVEL.INFO)
                    return _neuron

            return _neuron
