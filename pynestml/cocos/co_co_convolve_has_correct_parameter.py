# -*- coding: utf-8 -*-
#
# co_co_convolve_has_correct_parameter.py
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

from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.cocos.co_co import CoCo
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoConvolveHasCorrectParameter(CoCo):
    """
    This coco ensures that convolve gets only simple variable references as inputs.

    Not allowed:

    .. code-block::

        V mV = convolve(g_in + g_ex, spikes_in)

    """

    @classmethod
    @override
    def check_co_co(cls, node: ASTNode, metadata: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Ensures the coco for the handed over model.
        :param node: a single model instance.
        """
        assert isinstance(node, ASTModel), "This coco can only be called on ASTModels!"

        visitor = ConvolveParametersCorrectVisitor()
        node.accept(visitor)


class ConvolveParametersCorrectVisitor(ASTVisitor):
    def visit_function_call(self, node: ASTFunctionCall):
        """
        Checks the coco on the current function call.
        :param node: a single function call.
        """
        f_name = node.get_name()
        if f_name == PredefinedFunctions.CONVOLVE:
            for arg in node.get_args():
                if not isinstance(arg, ASTSimpleExpression) or not arg.is_variable():
                    code, message = Messages.get_not_a_variable(str(arg))
                    Logger.log_message(code=code, message=message,
                                       error_position=arg.get_source_position(), log_level=LoggingLevel.ERROR)
