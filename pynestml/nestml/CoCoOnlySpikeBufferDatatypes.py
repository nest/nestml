#
# CoCoOnlySpikeBufferDatatypes.py
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
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.utils.Logger import LOGGING_LEVEL, Logger


class CoCoOnlySpikeBufferDatatypes(CoCo):
    """
    This coco ensures that all spike buffers have a data type and all current buffers no data type stated.
    Allowed:
        input:
            spikeIn integer <- inhibitory spike
        end
        
    Not allowed:
        input:
            current integer <- current
        end
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.NoDatatypeOfCurrentBuffers) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(BufferDatatypeVisitor())
        return


class BufferDatatypeVisitor(NESTMLVisitor):
    """
    This visitor checks if each buffer has a datatype selected according to the coco.
    """

    def visitInputLine(self, _line=None):
        """
        Checks the coco on the current node.
        :param _line: a single input line node.
        :type _line: ASTInputLine
        """
        if _line.isSpike() and not _line.hasDatatype():
            Logger.logMessage(
                'Data type of spike buffer "%s" at %s not specified!'
                % (_line.getName(), _line.getSourcePosition().printSourcePosition()),
                LOGGING_LEVEL.ERROR)
        if _line.isCurrent() and _line.hasDatatype():
            Logger.logMessage(
                'No datatype allowed for current buffer "%s" at %s!'
                % (_line.getName(), _line.getSourcePosition().printSourcePosition()),
                LOGGING_LEVEL.ERROR)
        return
