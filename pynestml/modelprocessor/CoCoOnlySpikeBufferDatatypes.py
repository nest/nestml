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
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


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


class BufferDatatypeVisitor(ASTVisitor):
    """
    This visitor checks if each buffer has a datatype selected according to the coco.
    """

    def visit_input_line(self, node=None):
        """
        Checks the coco on the current node.
        :param node: a single input line node.
        :type node: ASTInputLine
        """
        from pynestml.modelprocessor.ASTInputLine import ASTInputLine
        assert (node is not None and isinstance(node, ASTInputLine)), \
            '(PyNestML.CoCo.NoDatatypeOfCurrentBuffers) No or wrong type of input line provided (%s)!' % type(node)
        if node.is_spike() and not node.has_datatype():
            code, message = Messages.getDataTypeNotSpecified(node.get_name())
            Logger.logMessage(_errorPosition=node.get_source_position(), _logLevel=LOGGING_LEVEL.ERROR,
                              _code=code, _message=message)
        if node.is_current() and node.has_datatype():
            code, message = Messages.getNotTypeAllowed(node.get_name())
            Logger.logMessage(_errorPosition=str(node.get_source_position()),
                              _code=code, _message=message,
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
