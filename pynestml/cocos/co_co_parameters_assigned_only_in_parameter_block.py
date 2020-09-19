# -*- coding: utf-8 -*-
#
# co_co_parameters_assigned_only_in_parameter_block.py
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
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.cocos.co_co import CoCo
from pynestml.symbol_table.scope import ScopeType
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


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
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(node)
        node.accept(ParametersAssignmentVisitor())
        return


class ParametersAssignmentVisitor(ASTVisitor):
    """
    This visitor checks that no parameters have been assigned outside the parameters block.
    """

    def visit_assignment(self, node):
        """
        Checks the coco on the current node.
        :param node: a single node.
        :type node: ast_assignment
        """
        symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_name(), SymbolKind.VARIABLE)
        if (symbol is not None and symbol.block_type == BlockType.PARAMETERS
                and node.get_scope().get_scope_type() != ScopeType.GLOBAL):
            code, message = Messages.get_assignment_not_allowed(node.get_variable().get_complete_name())
            Logger.log_message(error_position=node.get_source_position(),
                               code=code, message=message,
                               log_level=LoggingLevel.ERROR)
        return
