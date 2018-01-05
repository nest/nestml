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

    def __init__(self, _referenceConverter=None,_typesPrinter=None ):
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
        Prints a single expression.
        :param _expr: a single expression.
        :type _expr: ASTExpression or ASTSimpleExpression.
        :return: string representation of the expression
        :rtype: str
        """
        assert (_expr is not None and (isinstance(_expr, ASTSimpleExpression) or isinstance(_expr, ASTExpression))), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of expression provided (%s)!' % type(
                _expr)
        return self.__doPrint(_expr)

    def __doPrint(self, _expr=None):
        """
        Prints a single expression.
        :param _expr: a single expression.
        :type _expr: ASTExpression or ASTSimpleExpression.
        :return: string representation of the expression
        :rtype: str
        """
        if isinstance(_expr, ASTSimpleExpression):
            if _expr.hasUnit():
                return self.__typesPrinter.prettyPrint(_expr.getNumericLiteral()) + '*' + \
                       self.__referenceConverter.convertNameReference(_expr.getVariable())
            elif _expr.isNumericLiteral():
                return str(_expr.getNumericLiteral())
            elif _expr.isInfLiteral():
                return self.__referenceConverter.convertConstant('inf')
            elif _expr.isString():
                return self.__typesPrinter.prettyPrint(_expr.getString())
            elif _expr.isBooleanTrue():
                return self.__typesPrinter.prettyPrint(True)
            elif _expr.isBooleanFalse():
                return self.__typesPrinter.prettyPrint(False)
            elif _expr.isVariable():
                return self.__referenceConverter.convertNameReference(_expr.getVariable())
            elif _expr.isFunctionCall():
                return self.printFunctionCall(_expr.getFunctionCall())
        elif isinstance(_expr, ASTExpression):
            # a unary operator
            if _expr.isUnaryOperator():
                op = self.__referenceConverter.convertUnaryOp(_expr.getUnaryOperator())
                rhs = self.printExpression(_expr.getExpression())
                return op % rhs
            # encapsulated in brackets
            elif _expr.isEncapsulated():
                return self.__referenceConverter.convertEncapsulated() % self.printExpression(_expr.getExpression())
            # logical not
            elif _expr.isLogicalNot():
                op = self.__referenceConverter.convertLogicalNot()
                rhs = self.printExpression(_expr.getExpression)
                return op % rhs
            # compound expression with lhs + rhs
            elif _expr.isCompoundExpression():
                lhs = self.printExpression(_expr.getLhs())
                op = self.__referenceConverter.convertBinaryOp(_expr.getBinaryOperator())
                rhs = self.printExpression(_expr.getRhs())
                return op % (lhs, rhs)
            elif _expr.isTernaryOperator():
                condition = self.printExpression(_expr.getCondition())
                ifTrue = self.printExpression(_expr.getIfTrue())
                ifNot = self.printExpression(_expr.getIfNot())
                return self.__referenceConverter.convertTernaryOperator() % (condition, ifTrue, ifNot)
        else:
            Logger.logMessage('Unsupported expression in expression pretty printer!', LOGGING_LEVEL.ERROR)
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
        if self.__referenceConverter.needsArguments(_functionCall):
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
        for arg in _functionCall.getArgs():
            ret += self.printExpression(arg)
            if _functionCall.getArgs().index(arg) < len(_functionCall.getArgs()) - 1:
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
