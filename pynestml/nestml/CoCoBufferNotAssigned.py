#
# CoCoBufferNotAssigned.py
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
from pynestml.nestml.CoCo import CoCo
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.nestml.Symbol import SymbolKind
from pynestml.nestml.VariableSymbol import BlockType
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor


class CoCoBufferNotAssigned(CoCo):
    """
    This coco ensures that no values are assigned to buffers.
    Allowed:
        currentSum = current + 10mV # current being a buffer
    Not allowed:
        current = currentSum + 10mV
    
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(NoBufferAssignedVisitor())
        return


class NoBufferAssignedVisitor(NESTMLVisitor):
    def visitAssignment(self, _assignment=None):
        symbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getName(), SymbolKind.VARIABLE)
        if symbol is not None and (symbol.getBlockType() == BlockType.INPUT_BUFFER_SPIKE or
                                           symbol.getBlockType() == BlockType.INPUT_BUFFER_CURRENT):
            Logger.logMessage(
                'Value assigned to buffer "%s" at %s!'
                % (_assignment.getVariable().getCompleteName(), _assignment.getSourcePosition().printSourcePosition()),
                LOGGING_LEVEL.ERROR)
        return
