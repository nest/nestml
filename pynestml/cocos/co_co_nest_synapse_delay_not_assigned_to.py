# -*- coding: utf-8 -*-
#
# co_co_nest_synapse_delay_not_assigned_to.py
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

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoNESTSynapseDelayNotAssignedTo(CoCo):
    r"""
    This coco checks that the delay variable or parameter is not assigned to inside of a NESTML model. (This could be possible in general, but is not supported for now.)
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"
        assert metadata is not None and node.name in metadata.keys() and "delay_variable" in metadata[node.name].keys()

        delay_variable: str = metadata[node.name]["delay_variable"]
        visitor = CoCoNESTSynapseDelayNotAssignedToVisitor()
        visitor.delay_variable_ = delay_variable
        node.accept(visitor)


class CoCoNESTSynapseDelayNotAssignedToVisitor(ASTVisitor):
    def visit_assignment(self, node: ASTAssignment) -> None:
        """
        Checks the coco on the current node.
        :param node: a single node.
        """
        variable = node.get_variable()
        if variable.get_name() == self.delay_variable_:
            Logger.log_message(error_position=node.get_source_position(),
                               code=None, message="Delay variable \"" + str(variable.get_name()) + "\" may not be assigned to in NEST synapse models",
                               log_level=LoggingLevel.ERROR)
