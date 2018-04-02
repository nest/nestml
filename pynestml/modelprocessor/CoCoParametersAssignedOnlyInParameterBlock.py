#
# CoCoParametersAssignedOnlyInParameterBlock.py
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
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.VariableSymbol import BlockType
from pynestml.modelprocessor.Scope import ScopeType
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class CoCoParametersAssignedOnlyInParameterBlock(CoCo):
    """
    This coco checks that no parameters are assigned outside the parameters block.
    Allowed:
        parameters:
            par mV = 10mV
        end
    Not allowed:
        parameters:
            par mV = 10mV
        end
        ...
        update:
           par = 20mV
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
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(ParametersAssignmentVisitor())
        return


class ParametersAssignmentVisitor(ASTVisitor):
    """
    This visitor checks that no parameters have been assigned outside the parameters block.
    """

    def visit_assignment(self, node=None):
        """
        Checks the coco on the current node.
        :param assignment: a single node.
        :type node: ASTAssignment
        """
        from pynestml.modelprocessor.ASTAssignment import ASTAssignment
        assert (node is not None and isinstance(node, ASTAssignment)), \
            '(PyNestML.CoCo.ParametersAssignedOutsideParametersBlock) No or wrong type of node provided (%s)!' \
            % type(node)
        symbol = node.get_scope().resolveToSymbol(node.get_variable().get_name(), SymbolKind.VARIABLE)
        if symbol is not None and symbol.get_block_type() == BlockType.PARAMETERS and \
                        node.get_scope().getScopeType() != ScopeType.GLOBAL:
            code, message = Messages.getAssignmentNotAllowed(node.get_variable().get_complete_name())
            Logger.logMessage(_errorPosition=node.get_source_position(),
                              _code=code, _message=message,
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
