# -*- coding: utf-8 -*-
#
# latex_expression_printer.py
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
from pynestml.codegeneration.latex_reference_converter import LatexReferenceConverter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.utils.ast_utils import ASTUtils


class LatexExpressionPrinter():
    """
    Pretty printer for LaTeX. Assumes to be printing in a LaTeX environment where math mode is already on.
    """

    def __init__(self, reference_converter=None, types_printer=None):
        # type: (IReferenceConverter,TypesPrinter) -> None
        # todo by kp: this should expect a ITypesPrinter as the second arg
        self.reference_converter = LatexReferenceConverter()
        if types_printer is not None:
            self.types_printer = types_printer
        else:
            self.types_printer = TypesPrinter()

    def print_expression(self, node):
        # type: (ASTExpressionNode) -> str
        return self.__do_print(node)
        if node.get_implicit_conversion_factor() is not None:
            return str(node.get_implicit_conversion_factor()) + ' * (' + self.__do_print(node) + ')'
        else:
            return self.__do_print(node)

    def __do_print(self, node):
        # type: (ASTExpressionNode) -> str
        if isinstance(node, ASTVariable):
            return self.reference_converter.convert_name_reference(node)
        elif isinstance(node, ASTSimpleExpression):
            if node.has_unit():
                # todo by kp: this should not be done in the typesPrinter, obsolete
                s = ""
                if node.get_numeric_literal() != 1:
                    s += "{0:E}".format(node.get_numeric_literal())
                    s += r"\cdot"
                s += self.reference_converter.convert_name_reference(node.get_variable())
                return s
            elif node.is_numeric_literal():
                return str(node.get_numeric_literal())
            elif node.is_inf_literal:
                return r"\infty"
            elif node.is_string():
                return self.types_printer.pretty_print(node.get_string())
            elif node.is_boolean_true:
                return self.types_printer.pretty_print(True)
            elif node.is_boolean_false:
                return self.types_printer.pretty_print(False)
            elif node.is_variable():
                return self.reference_converter.convert_name_reference(node.get_variable())
            elif node.is_function_call():
                return self.print_function_call(node.get_function_call())
        elif isinstance(node, ASTExpression):
            # a unary operator
            if node.is_unary_operator():
                op = self.reference_converter.convert_unary_op(node.get_unary_operator())
                rhs = self.print_expression(node.get_expression())
                return op % rhs
            # encapsulated in brackets
            elif node.is_encapsulated:
                return self.reference_converter.convert_encapsulated() % self.print_expression(node.get_expression())
            # logical not
            elif node.is_logical_not:
                op = self.reference_converter.convert_logical_not()
                rhs = self.print_expression(node.get_expression())
                return op % rhs
            # compound rhs with lhs + rhs
            elif node.is_compound_expression():
                lhs = self.print_expression(node.get_lhs())
                rhs = self.print_expression(node.get_rhs())
                wide = False
                if node.get_binary_operator().is_div_op \
                        and len(lhs) > 3 * len(rhs):
                    # if lhs (numerator) is much wider than rhs (denominator), rewrite as a factor
                    wide = True
                op = self.reference_converter.convert_binary_op(node.get_binary_operator(), wide=wide)
                return op % ({"lhs": lhs, "rhs": rhs})
            elif node.is_ternary_operator():
                condition = self.print_expression(node.get_condition())
                if_true = self.print_expression(node.get_if_true())
                if_not = self.print_expression(node.if_not)
                return self.reference_converter.convert_ternary_operator() % (condition, if_true, if_not)
        else:
            raise RuntimeError('Unsupported rhs in rhs pretty printer!')

    def print_function_call(self, function_call):
        # type: (ASTFunctionCall) -> str
        function_name = self.reference_converter.convert_function_call(function_call)
        if ASTUtils.needs_arguments(function_call):
            return function_name % self.print_function_call_argument_list(function_call)
        else:
            return function_name

    def print_function_call_argument_list(self, function_call):
        # type: (ASTFunctionCall) -> tuple of str
        ret = []
        for arg in function_call.get_args():
            ret.append(self.print_expression(arg))
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
