# -*- coding: utf-8 -*-
#
# co_co_function_calls_consistent.py
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
from pynestml.cocos.co_co import CoCo
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.template_type_symbol import TemplateTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.type_caster import TypeCaster
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoFunctionCallsConsistent(CoCo):
    """
    This context condition checker ensures that for all function calls in the handed over neuron, if the called function has been declared, whether the number and types of arguments correspond to the declaration, etc.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Checks the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        node.accept(FunctionCallConsistencyVisitor())


class FunctionCallConsistencyVisitor(ASTVisitor):
    """
    This visitor ensures that all function calls are consistent.
    """

    def visit_function_call(self, node):
        """
        Check consistency for a single function call: check if the called function has been declared, whether the number and types of arguments correspond to the declaration, etc.

        :param node: a single function call.
        :type node: ASTFunctionCall
        """
        func_name = node.get_name()
        if func_name == 'convolve':
            # check if the number of arguments is the same as in the symbol
            if len(node.get_args()) != 2:
                code, message = Messages.get_wrong_number_of_args(str(node), 2, len(node.get_args()))
                Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                                   error_position=node.get_source_position())
                return
            return

        symbol = node.get_scope().resolve_to_symbol(node.get_name(), SymbolKind.FUNCTION)

        # first check if the function has been declared
        if symbol is None:
            code, message = Messages.get_function_not_declared(node.get_name())
            Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                               code=code, message=message)
            return

        # check if the number of arguments is the same as in the symbol
        if len(node.get_args()) != len(symbol.get_parameter_types()):
            code, message = Messages.get_wrong_number_of_args(str(node), len(symbol.get_parameter_types()),
                                                              len(node.get_args()))
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                               error_position=node.get_source_position())
            return

        # finally check if the call is correctly typed
        expected_types = symbol.get_parameter_types()
        actual_args = node.get_args()
        actual_types = [arg.type for arg in actual_args]
        for actual_arg, actual_type, expected_type in zip(actual_args, actual_types, expected_types):
            if isinstance(actual_type, ErrorTypeSymbol):
                code, message = Messages.get_type_could_not_be_derived(actual_arg)
                Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                                   error_position=actual_arg.get_source_position())
                return

            if not actual_type.equals(expected_type) and not isinstance(expected_type, TemplateTypeSymbol):
                TypeCaster.try_to_recover_or_error(expected_type, actual_type, actual_arg)
