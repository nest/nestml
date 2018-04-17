#
# ExpressionsPrettyPrinter.py
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
from pynestml.codegeneration.IReferenceConverter import IReferenceConverter
from pynestml.codegeneration.IdempotentReferenceConverter import IdempotentReferenceConverter
from pynestml.meta_model.ASTExpression import ASTExpression
from pynestml.meta_model.ASTFunctionCall import ASTFunctionCall
from pynestml.meta_model.ASTSimpleExpression import ASTSimpleExpression
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import LoggingLevel, Logger


class ExpressionsPrettyPrinter(object):
    """
    Converts expressions to the executable platform dependent code. By using different
    referenceConverters for the handling of variables, names, and functions can be adapted. For this,
    implement own IReferenceConverter specialisation.
    This class is used to transform only parts of the procedural language and not nestml in whole.
    """
    __referenceConverter = None
    __typesPrinter = None

    def __init__(self, reference_converter=None, types_printer=None):
        """
        Standard constructor.
        :param reference_converter: a single reference converter object.
        :type reference_converter: IReferenceConverter
        :param types_printer: a types Printer
        :type types_printer: ITypesPrinter
        """
        assert (reference_converter is None or isinstance(reference_converter, IReferenceConverter)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of reference converter provided (%s)!'
        assert (reference_converter is None or isinstance(reference_converter, IReferenceConverter)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of reference converter provided (%s)!'
        if reference_converter is not None:
            self.__referenceConverter = reference_converter
        else:
            self.__referenceConverter = IdempotentReferenceConverter()
        if types_printer is not None:
            self.__typesPrinter = types_printer
        else:
            self.__typesPrinter = TypesPrinter()

    def print_expression(self, expr):
        """
        Prints a single rhs.
        :param expr: a single rhs.
        :type expr: ASTExpression or ASTSimpleExpression.
        :return: string representation of the rhs
        :rtype: str
        """
        if expr.get_implicit_conversion_factor() is not None:
            return str(expr.get_implicit_conversion_factor()) + ' * (' + self.__do_print(expr) + ')'
        else:
            return self.__do_print(expr)

    def __do_print(self, _expr=None):
        """
        Prints a single rhs.
        :param _expr: a single rhs.
        :type _expr: ASTExpression or ASTSimpleExpression.
        :return: string representation of the rhs
        :rtype: str
        """
        if isinstance(_expr, ASTSimpleExpression):
            if _expr.has_unit():
                # todo by kp: this should not be done in the typesPrinter, obsolete
                return self.__typesPrinter.pretty_print(_expr.get_numeric_literal()) + '*' + \
                       self.__referenceConverter.convertNameReference(_expr.get_variable())
            elif _expr.is_numeric_literal():
                return str(_expr.get_numeric_literal())
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
            # a unary operator
            if _expr.is_unary_operator():
                op = self.__referenceConverter.convertUnaryOp(_expr.get_unary_operator())
                rhs = self.print_expression(_expr.get_expression())
                return op % rhs
            # encapsulated in brackets
            elif _expr.is_encapsulated:
                return self.__referenceConverter.convertEncapsulated() % self.print_expression(_expr.get_expression())
            # logical not
            elif _expr.is_logical_not:
                op = self.__referenceConverter.convertLogicalNot()
                rhs = self.print_expression(_expr.get_expression())
                return op % rhs
            # compound rhs with lhs + rhs
            elif _expr.is_compound_expression():
                lhs = self.print_expression(_expr.get_lhs())
                op = self.__referenceConverter.convertBinaryOp(_expr.get_binary_operator())
                rhs = self.print_expression(_expr.get_rhs())
                return op % (lhs, rhs)
            elif _expr.is_ternary_operator():
                condition = self.print_expression(_expr.get_condition())
                if_true = self.print_expression(_expr.get_if_true())
                if_not = self.print_expression(_expr.if_not)
                return self.__referenceConverter.convertTernaryOperator() % (condition, if_true, if_not)
        else:
            Logger.log_message('Unsupported rhs in rhs pretty printer!', LoggingLevel.ERROR)
            return ''

    def print_function_call(self, function_call):
        """
        Prints a single function call.
        :param function_call: a single function call.
        :type function_call: ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        assert (function_call is not None and isinstance(function_call, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of function call provided (%s)!' \
            % type(function_call)
        function_name = self.__referenceConverter.convertFunctionCall(function_call)
        if ASTUtils.needs_arguments(function_call):
            return function_name % self.print_function_call_arguments(function_call)
        else:
            return function_name

    def print_function_call_arguments(self, function_call):
        """
        Prints the arguments of the handed over function call.
        :param function_call: a single function call
        :type function_call: ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        ret = ''
        for arg in function_call.get_args():
            ret += self.print_expression(arg)
            if function_call.get_args().index(arg) < len(function_call.get_args()) - 1:
                ret += ', '
        return ret


class TypesPrinter(object):
    """
    Returns a processable format of the handed over element.
    """

    def pretty_print(self, _element=None):
        assert (_element is not None), \
            '(PyNestML.CodeGeneration.PrettyPrinter) No element provided (%s)!' % _element
        if isinstance(_element, bool) and _element:
            return 'true'
        elif isinstance(_element, bool) and not _element:
            return 'false'
        elif isinstance(_element, int) or isinstance(_element, float):
            return str(_element)
