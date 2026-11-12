# -*- coding: utf-8 -*-
#
# co_co_resolution_func_used.py
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
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoResolutionOrStepsFuncUsed(CoCo):
    r"""
    This Coco emits a warning in case the ``resolution()`` or ``steps()`` predefined function is used.
    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Checks the coco.
        :param node: a single model instance
        """
        class CoCoResolutionOrStepsFuncUsedVisitor(ASTVisitor):
            def visit_simple_expression(self, node):
                if node.get_function_call() is None:
                    return

                function_name = node.get_function_call().get_name()
                if function_name in [PredefinedFunctions.TIME_RESOLUTION, PredefinedFunctions.TIME_STEPS]:
                    code, message = Messages.get_fixed_timestep_func_used()
                    Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.WARNING)

        visitor = CoCoResolutionOrStepsFuncUsedVisitor()
        visitor.neuron = node
        node.accept(visitor)
