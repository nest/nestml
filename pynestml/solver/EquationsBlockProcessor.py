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


            return _neuron
