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
from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression
from pynestml.nestml.ASTExpression import ASTExpression
from pynestml.nestml.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.nestml.ASTBitOperator import ASTBitOperator
from pynestml.nestml.ASTComparisonOperator import ASTComparisonOperator
from pynestml.nestml.ASTLogicalOperator import ASTLogicalOperator
from pynestml.nestml.ASTFunctionCall import ASTFunctionCall
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

    def __init__(self, _referenceConverter=None):
        """
        Standard constructor.
        :param _referenceConverter: a single reference converter object.
        :type _referenceConverter: IReferenceConverter
        """
        assert (_referenceConverter is None or isinstance(_referenceConverter, IReferenceConverter)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of reference converter provided (%s)!'
        if _referenceConverter is not None:
            self.__referenceConverter = _referenceConverter
        else:
            self.__referenceConverter = IdempotentReferenceConverter()

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
        return self.doPrint(_expr)

    def doPrint(self, _expr=None):
        """
        Prints a single expression.
        :param _expr: a single expression.
        :type _expr: ASTExpression or ASTSimpleExpression.
        :return: string representation of the expression
        :rtype: str
        """
        if isinstance(_expr, ASTSimpleExpression):
            if _expr.hasUnit():
                return str(_expr.getNumericLiteral()) + '*' + str(_expr.getVariable().getCompleteName())
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
            if _expr.isUnaryOperator():
                if _expr.getUnaryOperator().isUnaryPlus():
                    return '(' + self.__referenceConverter.convertUnaryOp('+') + \
                           self.printExpression(_expr.getExpression()) + ')'
                elif _expr.getUnaryOperator().isUnaryMinus():
                    return '(' + self.__referenceConverter.convertUnaryOp('-') + \
                           self.printExpression(_expr.getExpression()) + ')'
                elif _expr.getUnaryOperator().isUnaryTilde():
                    return '(' + self.__referenceConverter.convertUnaryOp('~') + \
                           self.printExpression(_expr.getExpression()) + ')'
            elif _expr.isEncapsulated():
                return '(' + self.printExpression(_expr.getExpression()) + ')'
            # logical not
            elif _expr.isLogicalNot():
                return self.__referenceConverter.convertUnaryOp('not') + ' ' + self.printExpression(_expr.getExpression)
            # compound expression with lhs + rhs
            elif _expr.isCompoundExpression():
                # arithmetic op, i.e. +,-,*,/
                if isinstance(_expr.getBinaryOperator(), ASTArithmeticOperator) and \
                        (_expr.getBinaryOperator().isTimesOp() or _expr.getBinaryOperator().isDivOp() or
                             _expr.getBinaryOperator().isMinusOp() or _expr.getBinaryOperator().isPlusOp() or
                             _expr.getBinaryOperator().isModuloOp()):
                    return self.printExpression(_expr.getLhs()) + ' ' + \
                           self.printArithmeticOperator(_expr.getBinaryOperator()) + ' ' + \
                           self.printExpression(_expr.getRhs())
                # pow op
                elif isinstance(_expr.getBinaryOperator(),
                                ASTArithmeticOperator) and _expr.getBinaryOperator().isPowOp():
                    lhs = self.printExpression(_expr.getLhs())
                    pow = self.__referenceConverter.convertBinaryOp('**')
                    rhs = self.printExpression(_expr.getRhs())
                    return pow % (lhs, rhs)
                # bit operator
                elif isinstance(_expr.getBinaryOperator(), ASTBitOperator):
                    lhs = self.printExpression(_expr.getLhs())
                    bit = self.printBitOperator(_expr.getBinaryOperator())
                    rhs = self.printExpression(_expr.getRhs())
                    return lhs + ' ' + bit + ' ' + rhs
                # comparison operator
                elif isinstance(_expr.getBinaryOperator(), ASTComparisonOperator):
                    lhs = self.printExpression(_expr.getLhs())
                    comp = self.printComparisonOperator(_expr.getBinaryOperator())
                    rhs = self.printExpression(_expr.getRhs())
                    return lhs + ' ' + comp + ' ' + rhs
                elif isinstance(_expr.getBinaryOperator(), ASTLogicalOperator):
                    lhs = self.printExpression(_expr.getLhs())
                    op = self.printLogicalOperator(_expr.getBinaryOperator())
                    rhs = self.printExpression(_expr.getRhs())
                    return op % (lhs, rhs)

            elif _expr.isTernaryOperator():
                condition = self.printExpression(_expr.getCondition())
                ifTrue = self.printExpression(_expr.getIfTrue())
                ifNot = self.printExpression(_expr.getIfNot())
                return '(' + condition + ')?(' + ifTrue + '):(' + ifNot + ')'
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

    def printArithmeticOperator(self, _arithmeticOperator=None):
        """
        Prints a single arithmetic operator.
        :param _arithmeticOperator: a single arithmetic operator.
        :type _arithmeticOperator: ASTArithmeticOperator
        :return: a string representation
        :rtype: str
        """
        assert (_arithmeticOperator is not None and isinstance(_arithmeticOperator, ASTArithmeticOperator)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of arithmetic operator provided (%s)!' \
            % type(_arithmeticOperator)
        if _arithmeticOperator.isPlusOp():
            return '+'
        if _arithmeticOperator.isMinusOp():
            return '-'
        if _arithmeticOperator.isTimesOp():
            return '*'
        if _arithmeticOperator.isDivOp():
            return '/'
        if _arithmeticOperator.isModuloOp():
            return '%'
        else:
            Logger.logMessage('Cannot determine arithmetic operator!', LOGGING_LEVEL.ERROR)
            return ''

    def printBitOperator(self, _bitOperator=None):
        """
        Prints a single bit operator.
        :param _bitOperator: a single bit operator
        :type _bitOperator: ASTBitOperator
        :return: a string representation
        :rtype: str
        """
        assert (_bitOperator is not None and isinstance(_bitOperator, ASTBitOperator)), \
            '(PyNestML.CodeGeneration.ExpressionPrettyPrinter) No or wrong type of bit operator provided (%s)!' \
            % type(_bitOperator)
        if _bitOperator.isBitShiftLeft():
            return '<<'
        if _bitOperator.isBitShiftRight():
            return '>>'
        if _bitOperator.isBitAnd():
            return '&'
        if _bitOperator.isBitOr():
            return '|'
        if _bitOperator.isBitXor():
            return '^'
        else:
            Logger.logMessage('Cannot determine bit operator!', LOGGING_LEVEL.ERROR)
            return ''

    def printComparisonOperator(self, _op=None):
        """
        Prints a single comparison operator.
        :param _op: a single comparison operator
        :type _op: ASTComparisonOperator
        :return: the corresponding representation
        :rtype: str
        """
        assert (_op is not None and isinstance(_op, ASTComparisonOperator)), \
            '(PyNestML.CodeGeneration.PrettyPrinter) No or wrong type of comparison operator provided (%s)!' % type(_op)
        if _op.isLt():
            return '<'
        elif _op.isLe():
            return '<='
        elif _op.isEq():
            return '=='
        elif _op.isNe() or _op.isNe2():
            return '!='
        elif _op.isGe():
            return '>='
        elif _op.isGt():
            return '>'
        else:
            Logger.logMessage('Cannot determine comparison operator!', LOGGING_LEVEL.ERROR)
            return ''

    def printLogicalOperator(self, _op=None):
        """
        Prints a single logical operator.
        :param _op: a single comparison operator
        :type _op: ASTComparisonOperator
        :return: the corresponding representation
        :rtype: str
        """
        assert (_op is not None and isinstance(_op, ASTLogicalOperator)), \
            '(PyNestML.CodeGeneration.PrettyPrinter) No or wrong type of logical operator provided (%s)!' % type(_op)
        if _op.isAnd():
            return self.__referenceConverter.convertBinaryOp('and')
        elif _op.isOr():
            return self.__referenceConverter.convertBinaryOp('or')
        else:
            Logger.logMessage('Cannot determine logical operator!', LOGGING_LEVEL.ERROR)
            return ''
