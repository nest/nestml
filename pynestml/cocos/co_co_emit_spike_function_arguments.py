# -*- coding: utf-8 -*-
#
# co_co_emit_spike_function_arguments.py
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

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.template_type_symbol import TemplateTypeSymbol
from pynestml.symbols.variadic_type_symbol import VariadicTypeSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.type_caster import TypeCaster
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoEmitSpikeFunctionArguments(CoCo):
    """
    This context condition checker ensures that all calls to the ``emit_spike()`` function contain zero or one parameter.
    """

    @classmethod
    def check_co_co(cls, node: ASTNode):
        """
        Checks the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTModel
        """
        node.accept(EmitSpikeFunctionArgumentsVisitor())


class EmitSpikeFunctionArgumentsVisitor(ASTVisitor):

    @override
    def visit_function_call(self, node: ASTFunctionCall):
        func_name = node.get_name()

        if func_name == PredefinedFunctions.EMIT_SPIKE and len(node.get_args()) > 1:
            code, message = Messages.get_wrong_number_of_args(str(node), "zero or one", len(node.get_args()))
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR, error_position=node.get_source_position())
            return
