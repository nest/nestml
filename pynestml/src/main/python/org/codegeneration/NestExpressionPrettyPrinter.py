#
# NestExpressionPrettyPrinter.py
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
from pynestml.src.main.python.org.nestml.ast.ASTExpression import ASTExpression
from pynestml.src.main.python.org.nestml.ast.ASTSimpleExpression import ASTSimpleExpression
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger


class NestExpressionPrettyPrinter(object):
    """
    This class is used to transform all types of ASTExpression/simple expression to the corresponding
    nest readable format.
    """

    def printExpression(self, _expression=None):
        """
        Returns a nest processable string representation of the handed over expression object.
        :param _expression: a single expression.
        :type _expression: ASTExpression
        :return: a string representation
        :rtype: str
        """
        assert (_expression is not None and (isinstance(_expression, ASTExpression)
                                             or (_expression, ASTSimpleExpression))), \
            '(PyNestML.CodeGeneration.PrettyPrinter) No or wrong type of expression provided (%s)!' % type(_expression)
        if isinstance(_expression, ASTSimpleExpression):
            return self.printSimpleExpression(_expression)
        else:
            return self.printComplexExpression(_expression)

    def printSimpleExpression(self, _expression=None):
        """
        Prints a single simple expression to a nest processable format.
        :param _expression: a single simple expression.
        :type _expression: ASTSimpleExpression
        :return: the corresponding string representation
        :rtype: str
        """
        pass

    def printComplexExpression(self, _expression=None):
        """
        Prints a single expression to a nest processable format.
        :param _expression: a single expression.
        :type _expression: ASTExpression
        :return: the corresponding string representation
        :rtype: str
        """
        pass

    def printArithmeticOperator(self, _op=None):
        """
        Returns a nest processable representation of the arithmetic operator.
        :param _op: a single arithmetic operator.
        :type _op: ASTArithmeticOperator
        :return: the corresponding representation
        :rtype: str
        """
        from pynestml.src.main.python.org.nestml.ast.ASTArithmeticOperator import ASTArithmeticOperator
        assert (_op is not None and isinstance(_op, ASTArithmeticOperator)), \
            '(PyNestML.CodeGeneration.PrettyPrinter) No or wrong type of arithmetic operator provided (%s)!' % type(_op)
        if _op.isTimesOp():
            return '*'
        elif _op.isDivOp():
            return '/'
        elif _op.isModuloOp():
            return '%'
        elif _op.isPlusOp():
            return '+'
        elif _op.isMinusOp():
            return '-'
        elif _op.isPowOp():
            return '**'

    def printBitOperator(self, _op=None):
        """
        Returns a nest processable representation of the bit operator.
        :param _op: a single bit operator
        :type _op: ASTBitOperator
        :return: the corresponding representation
        :rtype: str
        """
        from pynestml.src.main.python.org.nestml.ast.ASTBitOperator import ASTBitOperator
        assert (_op is not None and isinstance(_op, ASTBitOperator)), \
            '(PyNestML.CodeGeneration.PrettyPrinter) No or wrong type of bit operator provided (%s)!' % type(_op)
        if _op.isBitAnd():
            return '&'
        elif _op.isBitOr():
            return '|'
        elif _op.isBitXor():
            return '^'
        elif _op.isBitShiftLeft():
            return '<<'
        elif _op.isBitShiftRight():
            return '>>'
        else:
            Logger.logMessage('Cannot determine mathematical operator!', LOGGING_LEVEL.ERROR)
            return ''

    def printComparisonOperatpr(self, _op=None):
        """
        Returns a nest processable representation of the comparison operator.
        :param _op: a single comparison operator
        :type _op: ASTComparisonOperator
        :return: the corresponding representation
        :rtype: str
        """
        from pynestml.src.main.python.org.nestml.ast.ASTComparisonOperator import ASTComparisonOperator
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
            Logger.logMessage('Cannot determine mathematical operator!', LOGGING_LEVEL.ERROR)
            return ''

    def printFunctionCall(self, _functionCall=None):
        """
        Returns a nest processable representation of the function call.
        :param _functionCall: a single function call.
        :type _functionCall: ASTFunctionCall
        :return: the corresponding representation
        :rtype: str
        """
        pass
