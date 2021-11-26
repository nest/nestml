# -*- coding: utf-8 -*-
#
# expressions_pretty_printer.py
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

from typing import Tuple

from pynestml.codegeneration.cpp_types_printer import CppTypesPrinter
from pynestml.codegeneration.nest_reference_converter import NESTReferenceConverter
from pynestml.codegeneration.nestml_reference_converter import NestMLReferenceConverter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils


class ExpressionsPrettyPrinter:
    """
    Converts expressions to the executable platform dependent code. By using different
    referenceConverters for the handling of variables, names, and functions can be adapted. For this,
    implement own IReferenceConverter specialisation.
    This class is used to transform only parts of the procedural language and not nestml in whole.
    """

    def __init__(self, reference_converter=None, types_printer=None):
        if reference_converter is not None:
            self.reference_converter = reference_converter
        else:
            self.reference_converter = NestMLReferenceConverter()

        if types_printer is not None:
            self.types_printer = types_printer
        else:
            self.types_printer = CppTypesPrinter()

    def print_expression(self, node, prefix='', with_origins = True):
        """Print an expression.

        Parameters
        ----------
        node : ASTExpressionNode
            The expression node to print.
        prefix : str
            *See documentation for the function print_function_call().*

        Returns
        -------
        s : str
            The expression string.
        """
        if (node.get_implicit_conversion_factor() is not None) \
                and (not node.get_implicit_conversion_factor() == 1):
            return str(node.get_implicit_conversion_factor()) + ' * (' + self.__do_print(node, prefix=prefix, with_origins=with_origins) + ')'
        else:
            return self.__do_print(node, prefix=prefix, with_origins = with_origins)

    def __do_print(self, node: ASTExpressionNode, prefix: str='', with_origins = True) -> str:
        if isinstance(node, ASTSimpleExpression):
            if node.has_unit():
                # todo by kp: this should not be done in the typesPrinter, obsolete
                if isinstance(self.reference_converter, NESTReferenceConverter):
                    # NESTReferenceConverter takes the extra with_origins parameter 
                    # which is used in compartmental models
                    return self.types_printer.pretty_print(node.get_numeric_literal()) + '*' + \
                        self.reference_converter.convert_name_reference(node.get_variable(), prefix=prefix, with_origins = with_origins)
                else:
                    return self.types_printer.pretty_print(node.get_numeric_literal()) + '*' + \
                        self.reference_converter.convert_name_reference(node.get_variable(), prefix=prefix)
            elif node.is_numeric_literal():
                return str(node.get_numeric_literal())
            elif node.is_inf_literal:
                return self.reference_converter.convert_constant('inf')
            elif node.is_string():
                return self.types_printer.pretty_print(node.get_string())
            elif node.is_boolean_true:
                return self.types_printer.pretty_print(True)
            elif node.is_boolean_false:
                return self.types_printer.pretty_print(False)
            elif node.is_variable():
                # NESTReferenceConverter takes the extra with_origins parameter 
                # which is used in cm models
                if isinstance(self.reference_converter, NESTReferenceConverter):
                    return self.reference_converter.convert_name_reference\
                    (node.get_variable(), prefix=prefix, with_origins = with_origins)
                else:
                    return self.reference_converter.convert_name_reference(node.get_variable(), prefix=prefix)
            elif node.is_function_call():
                return self.print_function_call(node.get_function_call(), prefix=prefix, with_origins = with_origins)
            raise Exception('Unknown node type')
        elif isinstance(node, ASTExpression):
            # a unary operator
            if node.is_unary_operator():
                op = self.reference_converter.convert_unary_op(node.get_unary_operator())
                rhs = self.print_expression(node.get_expression(), prefix=prefix, with_origins = with_origins)
                return op % rhs
            # encapsulated in brackets
            elif node.is_encapsulated:
                return self.reference_converter.convert_encapsulated() % self.print_expression(node.get_expression(),
                                                                                               prefix=prefix,
                                                                                               with_origins = with_origins)
            # logical not
            elif node.is_logical_not:
                op = self.reference_converter.convert_logical_not()
                rhs = self.print_expression(node.get_expression(), prefix=prefix, with_origins = with_origins)
                return op % rhs
            # compound rhs with lhs + rhs
            elif node.is_compound_expression():
                lhs = self.print_expression(node.get_lhs(), prefix=prefix, with_origins = with_origins)
                op = self.reference_converter.convert_binary_op(node.get_binary_operator())
                rhs = self.print_expression(node.get_rhs(), prefix=prefix, with_origins = with_origins)
                return op % (lhs, rhs)
            elif node.is_ternary_operator():
                condition = self.print_expression(node.get_condition(), prefix=prefix, with_origins = with_origins)
                if_true = self.print_expression(node.get_if_true(), prefix=prefix, with_origins = with_origins)
                if_not = self.print_expression(node.if_not, prefix=prefix, with_origins = with_origins)
                return self.reference_converter.convert_ternary_operator() % (condition, if_true, if_not)
            raise Exception('Unknown node type')
        else:
            raise RuntimeError('Unsupported rhs in rhs pretty printer (%s)!' % str(node))

    def print_function_call(self, function_call, prefix='', with_origins = True):
        """Print a function call, including bracketed arguments list.

        Parameters
        ----------
        function_call : ASTFunctionCall
            The function call node to print.
        prefix : str
            Optional string that will be prefixed to the function call. For example, to refer to a function call in the class "node", use a prefix equal to "node." or "node->".

            Predefined functions will not be prefixed.

        Returns
        -------
        s : str
            The function call string.
        """
        function_name = self.reference_converter.convert_function_call(function_call, prefix=prefix)
        if ASTUtils.needs_arguments(function_call):
            if function_call.get_name() == PredefinedFunctions.PRINT or function_call.get_name() == PredefinedFunctions.PRINTLN:
                return function_name.format(self.reference_converter.convert_print_statement(function_call))
            else:
                return function_name.format(*self.print_function_call_argument_list(function_call, prefix=prefix, with_origins = with_origins))
        else:
            return function_name

    def print_function_call_argument_list(self, function_call: ASTFunctionCall, prefix: str='', with_origins = True) -> Tuple[str, ...]:
        ret = []

        for arg in function_call.get_args():
            ret.append(self.print_expression(arg, prefix=prefix, with_origins = with_origins))

        return tuple(ret)
