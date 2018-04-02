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
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.codegeneration.IdempotentReferenceConverter import IdempotentReferenceConverter
from pynestml.codegeneration.IReferenceConverter import IReferenceConverter


class ExpressionsPrettyPrinter(object):
    """
    Converts expressions to the executable platform dependent code. By using different
    referenceConverters for the handling of variables, names, and functions can be adapted. For this,
    implement own IReferenceConverter specialisation.
    This class is used to transform only parts of the procedural language and not nestml in whole.
    """
    __referenceConverter = None
    __typesPrinter = None

    def __init__(self, _referenceConverter=None, _typesPrinter=None):
        """
        Standard constructor.
        :param _referenceConverter: a single reference converter object.
        :type _referenceConverter: IReferenceConverter
        :param _typesPrinter: a types Printer
        :type _typesPrinter: ITypesPrinter
        """
        assert (_referenceConverter is None or isinstance(_referenceConverter, IReferenceConverter)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of reference converter provided (%s)!'
        assert (_referenceConverter is None or isinstance(_referenceConverter, IReferenceConverter)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of reference converter provided (%s)!'
        if _referenceConverter is not None:
            self.__referenceConverter = _referenceConverter
        else:
            self.__referenceConverter = IdempotentReferenceConverter()
        if _typesPrinter is not None:
            self.__typesPrinter = _typesPrinter
        else:
            self.__typesPrinter = TypesPrinter()

    def printExpression(self, _expr=None):
        """
        Prints a single rhs.
        :param _expr: a single rhs.
        :type _expr: ASTExpression or ASTSimpleExpression.
        :return: string representation of the rhs
        :rtype: str
        """
        assert (_expr is not None and (isinstance(_expr, ASTSimpleExpression) or isinstance(_expr, ASTExpression))), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of rhs provided (%s)!' % type(
                _expr)
        return self.__doPrint(_expr)

    def __doPrint(self, _expr=None):
        """
        Prints a single rhs.
        :param _expr: a single rhs.
        :type _expr: ASTExpression or ASTSimpleExpression.
        :return: string representation of the rhs
        :rtype: str
        """
        if isinstance(_expr, ASTSimpleExpression):
            if _expr.has_unit():
                return self.__typesPrinter.prettyPrint(_expr.get_numeric_literal()) + '*' + \
                       self.__referenceConverter.convertNameReference(_expr.get_variable())
            elif _expr.is_numeric_literal():
                return str(_expr.get_numeric_literal())
            elif _expr.is_inf_literal():
                return self.__referenceConverter.convertConstant('inf')
            elif _expr.is_string():
                return self.__typesPrinter.prettyPrint(_expr.get_string())
            elif _expr.is_boolean_true():
                return self.__typesPrinter.prettyPrint(True)
            elif _expr.is_boolean_false():
                return self.__typesPrinter.prettyPrint(False)
            elif _expr.is_variable():
                return self.__referenceConverter.convertNameReference(_expr.get_variable())
            elif _expr.is_function_call():
                return self.printFunctionCall(_expr.get_function_call())
        elif isinstance(_expr, ASTExpression):
            # a unary operator
            if _expr.is_unary_operator():
                op = self.__referenceConverter.convertUnaryOp(_expr.get_unary_operator())
                rhs = self.printExpression(_expr.get_expression())
                return op % rhs
            # encapsulated in brackets
            elif _expr.is_encapsulated:
                return self.__referenceConverter.convertEncapsulated() % self.printExpression(_expr.get_expression())
            # logical not
            elif _expr.isLogicalNot():
                op = self.__referenceConverter.convertLogicalNot()
                rhs = self.printExpression(_expr.get_expression())
                return op % rhs
            # compound rhs with lhs + rhs
            elif _expr.is_compound_expression():
                lhs = self.printExpression(_expr.get_lhs())
                op = self.__referenceConverter.convertBinaryOp(_expr.get_binary_operator())
                rhs = self.printExpression(_expr.get_rhs())
                return op % (lhs, rhs)
            elif _expr.is_ternary_operator():
                condition = self.printExpression(_expr.get_condition())
                ifTrue = self.printExpression(_expr.get_if_true())
                ifNot = self.printExpression(_expr.if_not)
                return self.__referenceConverter.convertTernaryOperator() % (condition, ifTrue, ifNot)
        else:
            Logger.logMessage('Unsupported rhs in rhs pretty printer!', LOGGING_LEVEL.ERROR)
            return ''

    def printFunctionCall(self, _functionCall):
        """
        Prints a single function call.
        :param _functionCall: a single function call.
        :type _functionCall: ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        assert (_functionCall is not None and isinstance(_functionCall, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of function call provided (%s)!' \
            % type(_functionCall)
        functionName = self.__referenceConverter.convertFunctionCall(_functionCall)
        if ASTUtils.needs_arguments(_functionCall):
            return functionName % self.printFunctionCallArguments(_functionCall)
        else:
            return functionName

    def printFunctionCallArguments(self, _functionCall=None):
        """
        Prints the arguments of the handed over function call.
        :param _functionCall: a single function call
        :type _functionCall: ASTFunctionCall
        :return: a string representation
        :rtype: str
        """
        assert (_functionCall is not None and isinstance(_functionCall, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of function call provided (%s)!' \
            % type(_functionCall)
        ret = ''
        for arg in _functionCall.get_args():
            ret += self.printExpression(arg)
            if _functionCall.get_args().index(arg) < len(_functionCall.get_args()) - 1:
                ret += ', '
        return ret


class TypesPrinter(object):
    """
    Returns a processable format of the handed over element.
    """

    def prettyPrint(self, _element=None):
        assert (_element is not None), \
            '(PyNestML.CodeGeneration.PrettyPrinter) No element provided (%s)!' % _element
        if isinstance(_element, bool) and _element:
            return 'true'
        elif isinstance(_element, bool) and not _element:
            return 'false'
        elif isinstance(_element, int) or isinstance(_element, float):
            return str(_element)
