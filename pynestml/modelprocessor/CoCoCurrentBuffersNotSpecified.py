#
# CoCoCurrentBuffersNotSpecified.py
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
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages


class CoCoCurrentBuffersNotSpecified(CoCo):
    """
    This coco ensures that current buffers are not specified with a keyword.
    Allowed:
        input:
            current <- current
        end
    Not allowed:
        input:
            current <- inhibitory current
        end     
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.CurrentBuffersNotSpecified) No or wrong type of neuron provided (%s)!' % type(node)
        node.accept(CurrentTypeSpecifiedVisitor())
        return


class CurrentTypeSpecifiedVisitor(ASTVisitor):
    """
    This visitor ensures that all current buffers are not specified with keywords.
    """

    def visit_input_line(self, node):
        if node.is_current() and node.has_input_types() and len(node.get_input_types()) > 0:
            code, message = Messages.getCurrentBufferSpecified(node.get_name(),
                                                               list((str(buf) for buf in node.get_input_types())))
            Logger.log_message(error_position=node.get_source_position(),
                               code=code, message=message, log_level=LoggingLevel.ERROR)
        return
