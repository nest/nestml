#
# legacy_expression_printer.py
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
from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.codegeneration.i_reference_converter import IReferenceConverter
from pynestml.codegeneration.idempotent_reference_converter import IdempotentReferenceConverter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression


class LegacyExpressionPrinter(ExpressionsPrettyPrinter):
    """
    An adjusted version of the pretty printer which does not print units with literals.
    """

    def __init__(self, reference_converter=None):
        """
        Standard constructor.
        :param reference_converter: a single reference converter object.
        :type reference_converter: IReferenceConverter
        """
        from pynestml.codegeneration.expressions_pretty_printer import TypesPrinter
        super(LegacyExpressionPrinter, self).__init__(reference_converter)
        if reference_converter is not None:
            self.reference_converter = reference_converter
        else:
            self.reference_converter = IdempotentReferenceConverter()
        self.types_printer = TypesPrinter()

    def do_print(self, node):
        """
        Prints a single rhs.
        :param node: a single rhs.
        :type node: ASTExpression or ASTSimpleExpression.
        :return: string representation of the rhs
        :rtype: str
        """
        # todo : printing of literals etc. should be done by constant converter, not a type converter
        if isinstance(node, ASTSimpleExpression):
            if node.is_numeric_literal():
                return self.types_printer.pretty_print(node.get_numeric_literal())
            elif node.is_inf_literal:
                return self.reference_converter.convert_constant('inf')
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
            if node.is_unary_operator():
                op = self.reference_converter.convert_unary_op(node.get_unary_operator())
                rhs = self.print_expression(node.get_expression())
                return op % rhs
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
                op = self.reference_converter.convert_binary_op(node.get_binary_operator())
                rhs = self.print_expression(node.get_rhs())
                return op % (lhs, rhs)
            elif node.is_ternary_operator():
                condition = self.print_expression(node.get_condition())
                if_true = self.print_expression(node.get_if_true())
                if_not = self.print_expression(node.if_not)
                return self.reference_converter.convert_ternary_operator() % (condition, if_true, if_not)
        else:
            raise RuntimeError('Unsupported rhs in rhs pretty printer (%s)!' % str(node))
