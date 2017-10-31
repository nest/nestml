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
from pynestml.nestml.CoCo import CoCo
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Symbol import SymbolKind
from pynestml.nestml.VariableSymbol import BlockType
from pynestml.nestml.Scope import ScopeType
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


class ParametersAssignmentVisitor(NESTMLVisitor):
    """
    This visitor checks that no parameters have been assigned outside the parameters block.
    """

    def visitAssignment(self, _assignment=None):
        """
        Checks the coco on the current node.
        :param _assignment: a single assignment.
        :type _assignment: ASTAssignment
        """
        from pynestml.nestml.ASTAssignment import ASTAssignment
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.CoCo.ParametersAssignedOutsideParametersBlock) No or wrong type of assignment provided (%s)!' \
            % type(_assignment)
        symbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getName(), SymbolKind.VARIABLE)
        if symbol is not None and symbol.getBlockType() == BlockType.PARAMETERS and \
                        _assignment.getScope().getScopeType() != ScopeType.GLOBAL:
            code, message = Messages.getAssignmentNotAllowed(_assignment.getVariable().getCompleteName())
            Logger.logMessage(_errorPosition=_assignment.getSourcePosition(),
                              _code=code, _message=message,
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
