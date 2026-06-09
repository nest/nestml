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

from typing import Any, Dict, Optional

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.cocos.co_co import CoCo
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoInternalsAssignedOnlyInInternalsBlock(CoCo):
    """
    This coco checks that no internals are assigned outside the internals block.
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"

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
        internal = ASTUtils.get_internal_decl_by_name(self.neuron_, node.get_variable().get_name())
        if internal:
            code, message = Messages.get_assignment_not_allowed(node.get_variable().get_complete_name())
            Logger.log_message(error_position=node.get_source_position(),
                               code=code, message=message,
                               log_level=LoggingLevel.ERROR)
