#
# LegacyExpressionPrinter.py
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
from pynestml.meta_model.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.meta_model.ASTBitOperator import ASTBitOperator
from pynestml.meta_model.ASTComparisonOperator import ASTComparisonOperator
from pynestml.meta_model.ASTExpression import ASTExpression
from pynestml.meta_model.ASTLogicalOperator import ASTLogicalOperator
from pynestml.meta_model.ASTSimpleExpression import ASTSimpleExpression
from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from pynestml.codegeneration.IdempotentReferenceConverter import IdempotentReferenceConverter
from pynestml.utils.Logger import LoggingLevel, Logger


class LegacyExpressionPrinter(ExpressionsPrettyPrinter):
    """
    An adjusted version of the pretty printer which does not print units with literals.
    """
    __referenceConverter = None
    __typesPrinter = None

    def __init__(self, reference_converter=None):
        """
        Standard constructor.
        :param reference_converter: a single reference converter object.
        :type reference_converter: IReferenceConverter
        """
        from pynestml.codegeneration.ExpressionsPrettyPrinter import TypesPrinter
        super(LegacyExpressionPrinter, self).__init__(reference_converter)
        if reference_converter is not None:
            self.__referenceConverter = reference_converter
        else:
            self.__referenceConverter = IdempotentReferenceConverter()
        self.__typesPrinter = TypesPrinter()

    def doPrint(self, _expr=None):
        """
        Prints a single rhs.
        :param _expr: a single rhs.
        :type _expr: ASTExpression or ASTSimpleExpression.
        :return: string representation of the rhs
        :rtype: str
        """
        # todo : printing of literals etc. should be done by constant converter, not a type converter
        if isinstance(_expr, ASTSimpleExpression):
            if _expr.is_numeric_literal():
                return self.__typesPrinter.pretty_print(_expr.get_numeric_literal())
            elif _expr.is_inf_literal():
                return self.__referenceConverter.convertConstant('inf')
            elif _expr.is_string():
                return self.__typesPrinter.pretty_print(_expr.get_string())
            elif _expr.is_boolean_true():
                return self.__typesPrinter.pretty_print(True)
            elif _expr.is_boolean_false():
                return self.__typesPrinter.pretty_print(False)
            elif _expr.is_variable():
                return self.__referenceConverter.convertNameReference(_expr.get_variable())
            elif _expr.is_function_call():
                return self.print_function_call(_expr.get_function_call())
        elif isinstance(_expr, ASTExpression):
            if _expr.is_unary_operator():
                if _expr.get_unary_operator().isUnaryPlus():
                    return '(' + self.__referenceConverter.convertUnaryOp('+') + \
                           self.print_expression(_expr.get_expression()) + ')'
                elif _expr.get_unary_operator().isUnaryMinus():
                    return '(' + self.__referenceConverter.convertUnaryOp('-') + \
                           self.print_expression(_expr.get_expression()) + ')'
                elif _expr.get_unary_operator().isUnaryTilde():
                    return '(' + self.__referenceConverter.convertUnaryOp('~') + \
                           self.print_expression(_expr.get_expression()) + ')'
            elif _expr.is_encapsulated:
                return '(' + self.print_expression(_expr.get_expression()) + ')'
            # logical not
            elif _expr.is_logical_not:
                return self.__referenceConverter.convertUnaryOp('not') + ' ' + \
                       self.print_expression(_expr.get_expression())
            # compound rhs with lhs + rhs
            elif _expr.is_compound_expression():
                # arithmetic op, i.e. +,-,*,/
                if isinstance(_expr.get_binary_operator(), ASTArithmeticOperator) and \
                        (_expr.get_binary_operator().is_times_op or _expr.get_binary_operator().is_div_op or
                         _expr.get_binary_operator().is_minus_op() or _expr.get_binary_operator().is_plus_op() or
                         _expr.get_binary_operator().is_modulo_op):
                    # todo by kp: is this printer even used? if so, the printArithmeticOp function is not here
                    return self.print_expression(_expr.get_lhs()) + ' ' + \
                           self.printArithmeticOperator(_expr.get_binary_operator()) + ' ' + \
                           self.print_expression(_expr.get_rhs())
                # pow op
                elif isinstance(_expr.get_binary_operator(),
                                ASTArithmeticOperator) and _expr.get_binary_operator().is_pow_op():
                    lhs = self.print_expression(_expr.get_lhs())
                    pow = self.__referenceConverter.convertBinaryOp('**')
                    rhs = self.print_expression(_expr.get_rhs())
                    return pow % (lhs, rhs)
                # bit operator
                elif isinstance(_expr.get_binary_operator(), ASTBitOperator):
                    lhs = self.print_expression(_expr.get_lhs())
                    bit = self.printBitOperator(_expr.get_binary_operator())
                    rhs = self.print_expression(_expr.get_rhs())
                    return lhs + ' ' + bit + ' ' + rhs
                # comparison operator
                elif isinstance(_expr.get_binary_operator(), ASTComparisonOperator):
                    lhs = self.print_expression(_expr.get_lhs())
                    comp = self.printComparisonOperator(_expr.get_binary_operator())
                    rhs = self.print_expression(_expr.get_rhs())
                    return lhs + ' ' + comp + ' ' + rhs
                elif isinstance(_expr.get_binary_operator(), ASTLogicalOperator):
                    lhs = self.print_expression(_expr.get_lhs())
                    op = self.printLogicalOperator(_expr.get_binary_operator())
                    rhs = self.print_expression(_expr.get_rhs())
                    return op % (lhs, rhs)

            elif _expr.is_ternary_operator():
                condition = self.print_expression(_expr.get_condition())
                ifTrue = self.print_expression(_expr.get_if_true())
                ifNot = self.print_expression(_expr.get_if_not())
                return '(' + condition + ')?(' + ifTrue + '):(' + ifNot + ')'
        else:
            Logger.log_message('Unsupported rhs in rhs pretty printer!', LoggingLevel.ERROR)
            return ''
