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

from pynestml.codegeneration.i_reference_converter import IReferenceConverter
from pynestml.codegeneration.nestml_reference_converter import NestMLReferenceConverter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils


class ExpressionsPrettyPrinter(object):
    """
    Converts expressions to the executable platform dependent code. By using different
    referenceConverters for the handling of variables, names, and functions can be adapted. For this,
    implement own IReferenceConverter specialisation.
    This class is used to transform only parts of the procedural language and not nestml in whole.
    """

    def __init__(self, reference_converter=None, types_printer=None):
        # type: (IReferenceConverter,TypesPrinter) -> None
        # todo by kp: this should expect a ITypesPrinter as the second arg
        if reference_converter is not None:
            self.reference_converter = reference_converter
        else:
            self.reference_converter = NestMLReferenceConverter()

        if types_printer is not None:
            self.types_printer = types_printer
        else:
            self.types_printer = TypesPrinter()

    def print_expression(self, node, prefix=''):
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
            return str(node.get_implicit_conversion_factor()) + ' * (' + self.__do_print(node, prefix=prefix) + ')'
        else:
            return self.__do_print(node, prefix=prefix)

    def __do_print(self, node, prefix=''):
        # type: (ASTExpressionNode) -> str
        if isinstance(node, ASTSimpleExpression):
            if node.has_unit():
                # todo by kp: this should not be done in the typesPrinter, obsolete
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
                return self.reference_converter.convert_name_reference(node.get_variable(), prefix=prefix)
            elif node.is_function_call():
                return self.print_function_call(node.get_function_call(), prefix=prefix)
        elif isinstance(node, ASTExpression):
            # a unary operator
            if node.is_unary_operator():
                op = self.reference_converter.convert_unary_op(node.get_unary_operator())
                rhs = self.print_expression(node.get_expression(), prefix=prefix)
                return op % rhs
            # encapsulated in brackets
            elif node.is_encapsulated:
                return self.reference_converter.convert_encapsulated() % self.print_expression(node.get_expression(),
                                                                                               prefix=prefix)
            # logical not
            elif node.is_logical_not:
                op = self.reference_converter.convert_logical_not()
                rhs = self.print_expression(node.get_expression(), prefix=prefix)
                return op % rhs
            # compound rhs with lhs + rhs
            elif node.is_compound_expression():
                lhs = self.print_expression(node.get_lhs(), prefix=prefix)
                op = self.reference_converter.convert_binary_op(node.get_binary_operator())
                rhs = self.print_expression(node.get_rhs(), prefix=prefix)
                return op % (lhs, rhs)
            elif node.is_ternary_operator():
                condition = self.print_expression(node.get_condition(), prefix=prefix)
                if_true = self.print_expression(node.get_if_true(), prefix=prefix)
                if_not = self.print_expression(node.if_not, prefix=prefix)
                return self.reference_converter.convert_ternary_operator() % (condition, if_true, if_not)
        else:
            raise RuntimeError('Unsupported rhs in rhs pretty printer (%s)!' % str(node))

    def print_function_call(self, function_call, prefix=''):
        """Print a function call, including bracketed arguments list.

        Parameters
        ----------
        node : ASTFunctionCall
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
                return function_name.format(*self.print_function_call_argument_list(function_call, prefix=prefix))
        else:
            return function_name

    def print_function_call_argument_list(self, function_call, prefix=''):
        # type: (ASTFunctionCall) -> tuple of str
        ret = []

        for arg in function_call.get_args():
            ret.append(self.print_expression(arg, prefix=prefix))

        return tuple(ret)


class TypesPrinter(object):
    """
    Returns a processable format of the handed over element.
    """

    @classmethod
    def pretty_print(cls, element):
        assert (element is not None), \
            '(PyNestML.CodeGeneration.PrettyPrinter) No element provided (%s)!' % element
        if isinstance(element, bool) and element:
            return 'true'
        elif isinstance(element, bool) and not element:
            return 'false'
        elif isinstance(element, int) or isinstance(element, float):
            return str(element)
        elif isinstance(element, str):
            return element
