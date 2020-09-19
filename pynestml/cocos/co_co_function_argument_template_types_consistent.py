# -*- coding: utf-8 -*-
#
# co_co_function_argument_template_types_consistent.py
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

from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.cocos.co_co import CoCo
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.logging_helper import LoggingHelper
from pynestml.utils.messages import Messages
from pynestml.utils.type_caster import TypeCaster
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.template_type_symbol import TemplateTypeSymbol
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.void_type_symbol import VoidTypeSymbol


class CoCoFunctionArgumentTemplateTypesConsistent(CoCo):
    """
    This coco checks that if template types are used for function parameters, the types are mutually consistent.
    """

    @classmethod
    def check_co_co(cls, neuron):
        """
        Ensures the coco for the handed over neuron.
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """
        neuron.accept(CorrectTemplatedArgumentTypesVisitor())


class CorrectTemplatedArgumentTypesVisitor(ASTVisitor):
    """
    This visitor checks that all expression correspond to the expected type.
    """

    def visit_simple_expression(self, node):
        """
        Visits a single function call as stored in a simple expression and, if template types are used for function parameters, checks if all actual parameter types are mutually consistent.

        :param node: a simple expression
        :type node: ASTSimpleExpression
        :rtype None:
        """
        assert isinstance(node, ASTSimpleExpression), \
            '(PyNestML.Visitor.FunctionCallVisitor) No or wrong type of simple expression provided (%s)!' % tuple(node)
        assert (node.get_scope() is not None), \
            "(PyNestML.Visitor.FunctionCallVisitor) No scope found, run symboltable creator!"
        scope = node.get_scope()
        if node.get_function_call() is None:
            return
        function_name = node.get_function_call().get_name()
        method_symbol = scope.resolve_to_symbol(function_name, SymbolKind.FUNCTION)
        # check if this function exists
        if method_symbol is None:
            code, message = Messages.get_could_not_resolve(function_name)
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
            self._failure_occurred = True
            return
        return_type = method_symbol.get_return_type()

        template_symbol_to_actual_symbol = {}
        template_symbol_to_parameter_indices = {}
        # loop over all function parameters
        for arg_idx, arg_type in enumerate(method_symbol.param_types):
            if isinstance(arg_type, TemplateTypeSymbol):
                actual_symbol = node.get_function_call().get_args()[arg_idx].type
                if arg_type._i in template_symbol_to_actual_symbol.keys():
                    if (not template_symbol_to_actual_symbol[arg_type._i].differs_only_in_magnitude(actual_symbol)) \
                            and (not template_symbol_to_actual_symbol[arg_type._i].is_castable_to(actual_symbol)):
                        # if the one cannot be cast into the other
                        code, message = Messages.templated_arg_types_inconsistent(function_name, arg_idx, template_symbol_to_parameter_indices[arg_type._i], failing_arg_type_str=actual_symbol.print_nestml_type(
                        ), other_type_str=template_symbol_to_actual_symbol[arg_type._i].print_nestml_type())
                        Logger.log_message(code=code, message=message,
                                           error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)
                        self._failure_occurred = True
                        return

                    template_symbol_to_parameter_indices[arg_type._i] += [arg_idx]

                else:
                    template_symbol_to_actual_symbol[arg_type._i] = actual_symbol
                    template_symbol_to_parameter_indices[arg_type._i] = [arg_idx]
