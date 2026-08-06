# -*- coding: utf-8 -*-
#
# co_co_priorities_correctly_specified.py
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
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages


class CoCoPrioritiesCorrectlySpecified(CoCo):
    """
    This Coco ensures that priorities for event handlers are correctly specified.
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Checks the context condition.
        :param node: a single model
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"

        priorities = {}   # type: Dict[str, int]
        for on_receive_block in node.get_on_receive_blocks():
            if "priority" in on_receive_block.get_const_parameters():
                priorities[on_receive_block.get_port_name()] = int(on_receive_block.get_const_parameters()["priority"])

        if len(priorities) == 1:
            on_receive_block_name = list(priorities.keys())[0]

            code, message = Messages.get_priority_defined_for_only_one_receive_block(on_receive_block_name)
            Logger.log_message(code=code,
                               message=message,
                               error_position=node.get_on_receive_block(on_receive_block_name).get_source_position(),
                               log_level=LoggingLevel.ERROR,
                               node=node)
            return

        unique_priorities = set(priorities.values())
        if len(unique_priorities) < len(priorities.values()):
            code, message = Messages.get_repeated_priorty_value()
            Logger.log_message(code=code,
                               message=message,
                               log_level=LoggingLevel.ERROR)
            return
