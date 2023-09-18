# -*- coding: utf-8 -*-
#
# co_co_internals_assigned_only_in_internals_block.py
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

from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.cocos.co_co import CoCo
from pynestml.symbol_table.scope import ScopeType
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoInternalsAssignedOnlyInInternalsBlock(CoCo):
    """
    This coco checks that no internals are assigned outside the internals block.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and (isinstance(node, ASTNeuron) or isinstance(node, ASTSynapse))), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(node)
        visitor = InternalsAssignmentVisitor()
        visitor.neuron_ = node
        node.accept(visitor)


class InternalsAssignmentVisitor(ASTVisitor):
    """
    This visitor checks that no internals have been assigned outside the internals block.
    """

    def visit_assignment(self, node: ASTAssignment) -> None:
        """
        Checks the coco on the current node.
        :param node: a single node.
        """
        internal = ASTUtils.get_internal_by_name(self.neuron_, node.get_variable().get_name())
        if internal:
            code, message = Messages.get_assignment_not_allowed(node.get_variable().get_complete_name())
            Logger.log_message(error_position=node.get_source_position(),
                               code=code, message=message,
                               log_level=LoggingLevel.ERROR)
