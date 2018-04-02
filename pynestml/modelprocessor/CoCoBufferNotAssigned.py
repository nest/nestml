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
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.VariableSymbol import BlockType
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class CoCoBufferNotAssigned(CoCo):
    """
    This coco ensures that no values are assigned to buffers.
    Allowed:
        currentSum = current + 10mV # current being a buffer
    Not allowed:
        current = currentSum + 10mV
    
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(node)
        node.accept(NoBufferAssignedVisitor())
        return


class NoBufferAssignedVisitor(ASTVisitor):
    def visit_assignment(self, node):
        symbol = node.get_scope().resolveToSymbol(node.get_variable().get_name(), SymbolKind.VARIABLE)
        if symbol is not None and (symbol.get_block_type() == BlockType.INPUT_BUFFER_SPIKE or
                                   symbol.get_block_type() == BlockType.INPUT_BUFFER_CURRENT):
            code, message = Messages.getValueAssignedToBuffer(node.get_variable().get_complete_name())
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=node.get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
