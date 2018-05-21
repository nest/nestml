#
# CoCoOnlySpikeBufferDataTypes.py
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
from pynestml.cocos.CoCo import CoCo
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoOnlySpikeBufferDataTypes(CoCo):
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
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        node.accept(BufferDatatypeVisitor())


class BufferDatatypeVisitor(ASTVisitor):
    """
    This visitor checks if each buffer has a datatype selected according to the coco.
    """

    def visit_input_line(self, node):
        """
        Checks the coco on the current node.
        :param node: a single input line node.
        :type node: ASTInputLine
        """
        if node.is_spike() and not node.has_datatype():
            code, message = Messages.get_data_type_not_specified(node.get_name())
            Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                               code=code, message=message)
        if node.is_current() and node.has_datatype():
            code, message = Messages.get_not_type_allowed(node.get_name())
            Logger.log_message(error_position=str(node.get_source_position()),
                               code=code, message=message,
                               log_level=LoggingLevel.ERROR)
        return
