# -*- coding: utf-8 -*-
#
# co_co_output_port_defined_if_emit_call.py
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
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoOutputPortDefinedIfEmitCall(CoCo):
    """
    This context condition checker ensures that if an event is emitted, a corresponding output port is defined with the appropriate type.
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Checks the coco for the handed over model.
        :param node: a single model instance.
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"

        visitor = OutputPortDefinedIfEmitCalledVisitor()
        visitor.neuron = node
        node.accept(visitor)


class OutputPortDefinedIfEmitCalledVisitor(ASTVisitor):
    """
    This visitor ensures that all function calls are consistent.
    """

    neuron = None   # type: Optional[ASTModel]

    def visit_function_call(self, node: ASTFunctionCall):
        """
        If an emit_spike() function is found, check output block exists and has spike type.

        :param node: a single function call.
        """
        assert self.neuron is not None
        func_name = node.get_name()
        if func_name == PredefinedFunctions.EMIT_SPIKE:
            output_blocks = self.neuron.get_output_blocks()

            # exactly one output block should be defined
            if len(output_blocks) == 0:
                code, message = Messages.get_block_not_defined_correctly("output", missing=True)
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)
                return

            if len(output_blocks) > 1:
                code, message = Messages.get_block_not_defined_correctly("output", missing=False)
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)
                return

            assert len(output_blocks) == 1

            if not output_blocks[0].is_spike():
                code, message = Messages.get_emit_spike_function_but_no_output_port()
                Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                                   error_position=output_blocks[0].get_source_position())
                return
