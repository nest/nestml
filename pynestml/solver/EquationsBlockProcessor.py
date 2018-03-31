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
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.solver.SymPySolver import SymPySolver
from pynestml.solver.DeltaSolutionTransformer import DeltaSolutionTransformer
from pynestml.solver.ShapesToOdesTransformer import ShapesToOdesTransformer
from pynestml.solver.TransformerBase import TransformerBase
from pynestml.solver.ExactSolutionTransformer import ExactSolutionTransformer
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
        working_version = _neuron
        if working_version.getEquationsBlocks() is not None:
            deep_copy = deepcopy(_neuron)
            if len(working_version.getEquationsBlocks().getOdeShapes()) > 0 and \
                    not cls.__odeShapeExists(working_version.getEquationsBlocks().getOdeShapes()) and \
                    len(working_version.getEquationsBlocks().getOdeEquations()) == 1:
                output = SymPySolver.solveOdeWithShapes(deep_copy.getEquationsBlocks())
                if not output.status == 'success':
                    code, message = Messages.getCouldNotBeSolved()
                    Logger.logMessage(_neuron=_neuron,
                                      _message=message, _code=code,
                                      _errorPosition=_neuron.getEquationsBlocks().get_source_position(),
                                      _logLevel=LOGGING_LEVEL.ERROR)
                    return _neuron
                if output.solver == 'exact':
                    code, message = Messages.getEquationsSolvedExactly()
                    Logger.logMessage(_neuron=_neuron,
                                      _message=message, _code=code,
                                      _errorPosition=_neuron.getEquationsBlocks().get_source_position(),
                                      _logLevel=LOGGING_LEVEL.INFO)
                    working_version = ExactSolutionTransformer.addExactSolution(_neuron=working_version,
                                                                                _solverOutput=output)
                elif output.solver == 'numeric':
                    code, message = Messages.getEquationsSolvedByGLS()
                    Logger.logMessage(_neuron=_neuron,
                                      _message=message, _code=code,
                                      _errorPosition=_neuron.getEquationsBlocks().get_source_position(),
                                      _logLevel=LOGGING_LEVEL.INFO)
                    working_version = ShapesToOdesTransformer.transformShapesToOdeForm(_neuron=_neuron,
                                                                                       _solverOutput=output)
                elif output.solver == 'delta':
                    return DeltaSolutionTransformer.addExactSolution(_solverOutput=output, _neuron=_neuron)
                else:
                    code, message = Messages.getCouldNotBeSolved()
                    Logger.logMessage(_neuron=_neuron,
                                      _message=message, _code=code,
                                      _errorPosition=_neuron.getEquationsBlocks().get_source_position(),
                                      _logLevel=LOGGING_LEVEL.INFO)
                    return working_version
            elif len(working_version.getEquationsBlocks().getOdeShapes()) > 0 and \
                    not cls.__odeShapeExists(working_version.getEquationsBlocks().getOdeShapes()):
                code, message = Messages.getEquationsSolvedByGLS()
                Logger.logMessage(_neuron=_neuron,
                                  _message=message, _code=code,
                                  _errorPosition=_neuron.getEquationsBlocks().get_source_position(),
                                  _logLevel=LOGGING_LEVEL.INFO)
                solver_output = SymPySolver.solveShapes(deep_copy.getEquationsBlocks().getOdeShapes())
                working_version = ShapesToOdesTransformer.transformShapesToOdeForm(_neuron, solver_output)
            else:
                TransformerBase.applyIncomingSpikes(working_version)
        return working_version

    @classmethod
    def __odeShapeExists(cls, _shapes):
        """
        Checks if there exists a shape with differential order > 0.
        :param _shapes: a list of shapes
        :type _shapes: list(ASTOdeShape)
        :return: True if an ode shape exits, otherwise False.
        :rtype: bool
        """
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        for shape in _shapes:
            if isinstance(shape, ASTOdeShape) and shape.getVariable().getDifferentialOrder() > 0:
                return True
        return False
