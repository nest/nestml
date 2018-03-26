#
# ASTExpression.py
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


from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTNode import ASTNode
from pynestml.modelprocessor.Either import Either


class ASTExpression(ASTNode):
    """
    ASTExpr, i.e., several subexpressions combined by one or more operators, e.g., 10mV + V_m - (V_reset * 2)/ms ....
    or a simple expression, e.g. 10mV.
    Grammar: 
      expression : leftParentheses='(' expression rightParentheses=')'
             | <assoc=right> base=expression powOp='**' exponent=expression
             | unaryOperator term=expression
             | left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
             | left=expression (plusOp='+'  | minusOp='-') right=expression
             | left=expression bitOperator right=expression
             | left=expression comparisonOperator right=expression
             | logicalNot='not' expression
             | left=expression logicalOperator right=expression
             | condition=expression '?' ifTrue=expression ':' ifNot=expression
             | simpleExpression
             ;
    """
    # encapsulated or with unary operator or with a logical not or just a simple expression.
    __isEncapsulated = False
    __isLogicalNot = False
    __unaryOperator = None
    __expression = None
    # lhs and rhs combined by an operator
    __lhs = None
    __binaryOperator = None
    __rhs = None
    # ternary operator
    __condition = None
    __ifTrue = None
    __ifNot = None
    # simple expression
    __simpleExpression = None
    # the corresponding type symbol.
    __typeEither = None

    def __init__(self, is_encapsulated=False, unary_operator=None, is_logical_not=False,
                 expression=None, lhs=None, binary_operator=None, rhs=None, condition=None, if_true=None,
                 if_not=None, source_position=None):
        """
        Standard constructor.
        :param is_encapsulated: is encapsulated in brackets.
        :type is_encapsulated: bool
        :param unary_operator: combined by unary operator, e.g., ~.
        :type unary_operator: ASTUnaryOperator
        :param is_logical_not: is a negated expression.
        :type is_logical_not: bool
        :param expression: the expression either encapsulated in brackets or negated or with a with a unary op, or
        a simple expression.
        :type expression: ASTExpression
        :param lhs: the left-hand side expression.
        :type lhs: ASTExpression
        :param binary_operator: a binary operator, e.g., a comparison operator or a logical operator.
        :type binary_operator: ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        :param rhs: the right-hand side expression
        :type rhs: ASTExpression
        :param condition: the condition of a ternary operator
        :type condition: ASTExpression
        :param if_true: if condition holds, this expression is executed.
        :type if_true: ASTExpression
        :param if_not: if condition does not hold, this expression is executed.
        :type if_not: ASTExpression
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourcePosition.
        """
        assert ((unary_operator is None) or (isinstance(unary_operator, ASTUnaryOperator))), \
            '(PyNestML.AST.Expression) Wrong type of unary operator provided (%s)!' % type(unary_operator)
        assert ((expression is None) or (isinstance(expression, ASTExpression)) or (
            isinstance(expression, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) Wrong type of expression provided (%s)!' % type(expression)
        assert ((binary_operator is None) or (isinstance(binary_operator, ASTArithmeticOperator) or
                                              (isinstance(binary_operator, ASTBitOperator)) or
                                              (isinstance(binary_operator, ASTLogicalOperator)) or
                                              (isinstance(binary_operator, ASTComparisonOperator)))), \
            '(PyNestML.AST.Expression) Wrong type of binary operator provided (%s)!' % type(binary_operator)
        assert (is_encapsulated is None or isinstance(is_encapsulated, bool)), \
            '(PyNestML.AST.Expression) Wrong type of parenthesis parameter provided (%s)' \
            % type(is_encapsulated)
        assert (condition is None or isinstance(condition, ASTExpression)
                or isinstance(condition, ASTSimpleExpression)), \
            '(PyNestML.AST.Expression) Wrong type of condition provided (%s)!' % type(condition)
        assert (if_true is None or isinstance(if_true, ASTExpression) or isinstance(if_true, ASTSimpleExpression)), \
            '(PyNestML.AST.Expression) Wrong type of if-true consequence provided (%s)!' % type(if_true)
        assert (if_not is None or isinstance(if_not, ASTExpression) or isinstance(if_not, ASTSimpleExpression)), \
            '(PyNestML.AST.Expression) Wrong type of if-not consequence provided (%s)!' % type(if_not)
        super(ASTExpression, self).__init__(source_position)
        self.__isEncapsulated = is_encapsulated
        self.__isLogicalNot = is_logical_not
        self.__unaryOperator = unary_operator
        self.__expression = expression
        # lhs and rhs combined by an operator
        self.__lhs = lhs
        self.__binaryOperator = binary_operator
        self.__rhs = rhs
        # ternary operator
        assert (
                (condition is None) or (isinstance(condition, ASTExpression)) or (
            isinstance(condition, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) Condition not an expression!'
        assert (
                (if_true is None) or (isinstance(if_true, ASTExpression)) or (
            isinstance(if_true, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) If-true part of ternary operator not an expression!'
        assert ((if_not is None) or (isinstance(if_not, ASTExpression)) or (isinstance(if_not, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) If-not part of ternary operator not an expression!'
        self.__condition = condition
        self.__ifTrue = if_true
        self.__ifNot = if_not
        return

    def isExpression(self):
        """
        Returns whether it is a expression, e.g. ~10mV.
        :return: True if expression, otherwise false.
        :rtype: bool 
        """
        return self.__expression is not None

    def getExpression(self):
        """
        Returns the expression.
        :return: the expression.
        :rtype: ASTExpression
        """
        return self.__expression

    def isEncapsulated(self):
        """
        Returns whether this expression is encapsulated in brackets.
        :return: True if encapsulated, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isEncapsulated, bool) and self.__isEncapsulated

    def isLogicalNot(self):
        """
        Returns whether the expression is negated by a logical not.
        :return: True if negated, otherwise False.  
        :rtype: bool
        """
        return isinstance(self.__isLogicalNot, bool) and self.__isLogicalNot

    def isUnaryOperator(self):
        """
        Returns whether the expression uses an unary operator.
        :return: True if unary operator, otherwise False.  
        :rtype: bool
        """
        return self.__unaryOperator is not None

    def getUnaryOperator(self):
        """
        Returns the unary operator.
        :return: the unary operator.
        :rtype: ASTUnaryOperator.
        """
        return self.__unaryOperator

    def isCompoundExpression(self):
        """
        Returns whether it is a compound expression, e.g., 10+10
        :return: True if compound expression, otherwise False.
        :rtype: bool
        """
        return (self.__lhs is not None) and (self.__rhs is not None) and (self.__binaryOperator is not None)

    def getLhs(self):
        """
        Returns the left-hand side expression.
        :return: the left-hand side expression.
        :rtype: ASTExpression
        """
        return self.__lhs

    def getRhs(self):
        """
        Returns the right-hand side expression.
        :return: the right-hand side expression.
        :rtype: ASTExpression
        """
        return self.__rhs

    def getBinaryOperator(self):
        """
        Returns the binary operator.
        :return: the binary operator.
        :rtype: one of ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        """
        return self.__binaryOperator

    def isTernaryOperator(self):
        """
        Returns whether it is a ternary operator.
        :return: True if ternary operator, otherwise False.
        :rtype: bool
        """
        return (self.__condition is not None) and (self.__ifTrue is not None) and (self.__ifNot is not None)

    def getCondition(self):
        """
        Returns the condition expression.
        :return: the condition expression.
        :rtype: ASTExpression
        """
        return self.__condition

    def getIfTrue(self):
        """
        Returns the expression used in the case that the condition holds.
        :return: the if-true condition.
        :rtype: ASTExpression
        """
        return self.__ifTrue

    def getIfNot(self):
        """
        Returns the expression used in the case that the condition does not hold.
        :return: the if-not condition.
        :rtype: ASTExpression
        """
        return self.__ifNot

    def getVariables(self):
        """
        Returns a list of all variables as used in this expression.
        :return: a list of variables.
        :rtype: list(ASTVariable)
        """
        ret = list()
        if self.isExpression():
            ret.extend(self.getExpression().getVariables())
        elif self.isCompoundExpression():
            ret.extend(self.getLhs().getVariables())
            ret.extend(self.getRhs().getVariables())
        elif self.isTernaryOperator():
            ret.extend(self.getCondition().getVariables())
            ret.extend(self.getIfTrue().getVariables())
            ret.extend(self.getIfNot().getVariables())
        return ret

    def getUnits(self):
        """
        Returns a list of all units as use in this expression.
        :return: a list of all used units.
        :rtype: list(ASTVariable)
        """
        ret = list()
        if self.isExpression():
            ret.extend(self.getExpression().getUnits())
        elif self.isCompoundExpression():
            ret.extend(self.getLhs().getUnits())
            ret.extend(self.getRhs().getUnits())
        elif self.isTernaryOperator():
            ret.extend(self.getCondition().getUnits())
            ret.extend(self.getIfTrue().getUnits())
            ret.extend(self.getIfNot().getUnits())
        return ret

    def getFunctionCalls(self):
        """
        Returns a list of all function calls as used in this expression
        :return: a list of all function calls in this expression.
        :rtype: list(ASTFunctionCall)
        """
        ret = list()
        if self.isExpression():
            ret.extend(self.getExpression().getFunctionCalls())
        elif self.isCompoundExpression():
            ret.extend(self.getLhs().getFunctionCalls())
            ret.extend(self.getRhs().getFunctionCalls())
        elif self.isTernaryOperator():
            ret.extend(self.getCondition().getFunctionCalls())
            ret.extend(self.getIfTrue().getFunctionCalls())
            ret.extend(self.getIfNot().getFunctionCalls())
        return ret

    def getTypeEither(self):
        """
        Returns an Either object holding either the type symbol of
        this expression or the corresponding error message
        If it does not exist, run the ExpressionTypeVisitor on it to calculate it
        :return: Either a valid type or an error message
        :rtype: Either
        """
        from pynestml.modelprocessor.ExpressionTypeVisitor import ExpressionTypeVisitor
        if self.__typeEither is None:
            self.accept(ExpressionTypeVisitor())
        return self.__typeEither

    def setTypeEither(self, _typeEither=None):
        """
        Updates the current type symbol to the handed over one.
        :param _typeEither: a single type symbol object.
        :type _typeEither: TypeSymbol
        """
        assert (_typeEither is not None and isinstance(_typeEither, Either)), \
            '(PyNestML.AST.Expression) No or wrong type of type symbol provided (%s)!' % type(_typeEither)
        self.__typeEither = _typeEither
        return

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.isExpression():
            if self.getExpression() is _ast:
                return self
            elif self.getExpression().getParent(_ast) is not None:
                return self.getExpression().getParent(_ast)
        if self.isUnaryOperator():
            if self.getUnaryOperator() is _ast:
                return self
            elif self.getUnaryOperator().getParent(_ast) is not None:
                return self.getUnaryOperator().getParent(_ast)
        if self.isCompoundExpression():
            if self.getLhs() is _ast:
                return self
            elif self.getLhs().getParent(_ast) is not None:
                return self.getLhs().getParent(_ast)
            if self.getBinaryOperator() is _ast:
                return self
            elif self.getBinaryOperator().getParent(_ast) is not None:
                return self.getBinaryOperator().getParent(_ast)
            if self.getRhs() is _ast:
                return self
            elif self.getRhs().getParent(_ast) is not None:
                return self.getRhs().getParent(_ast)
        if self.isTernaryOperator():
            if self.getCondition() is _ast:
                return self
            elif self.getCondition().getParent(_ast) is not None:
                return self.getCondition().getParent(_ast)
            if self.getIfTrue() is _ast:
                return self
            elif self.getIfTrue().getParent(_ast) is not None:
                return self.getIfTrue().getParent(_ast)
            if self.getIfNot() is _ast:
                return self
            elif self.getIfNot().getParent(_ast) is not None:
                return self.getIfNot().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns the string representation of the expression.
        :return: the expression as a string.
        :rtype: str
        """
        ret = ''
        if self.isExpression():
            if self.isEncapsulated():
                ret += '('
            if self.isLogicalNot():
                ret += 'not '
            if self.isUnaryOperator():
                ret += str(self.getUnaryOperator())
            ret += str(self.getExpression())
            if self.isEncapsulated():
                ret += ')'
        elif self.isCompoundExpression():
            ret += str(self.getLhs())
            ret += str(self.getBinaryOperator())
            ret += str(self.getRhs())
        elif self.isTernaryOperator():
            ret += str(self.getCondition()) + '?' + str(self.getIfTrue()) + ':' + str(self.getIfNot())
        return ret

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTExpression):
            return False
        # we have to ensure that both either are encapsulated or not
        if self.isEncapsulated() + _other.isEncapsulated() == 1:
            return False
        if self.isLogicalNot() + _other.isLogicalNot() == 1:
            return False
        if self.isUnaryOperator() + _other.isUnaryOperator() == 1:
            return False
        if self.isUnaryOperator() and _other.isUnaryOperator() and \
                not self.getUnaryOperator().equals(_other.getUnaryOperator()):
            return False
        if self.isExpression() + _other.isExpression() == 1:
            return False
        if self.isExpression() and _other.isExpression() and not self.getExpression().equals(_other.getExpression()):
            return False
        if self.isCompoundExpression() + _other.isCompoundExpression() == 1:
            return False
        if self.isCompoundExpression() and _other.isCompoundExpression() and \
                not (self.getLhs().equals(_other.getLhs()) and self.getRhs().equals(_other.getRhs()) and
                     self.getBinaryOperator().equals(_other.getBinaryOperator())):
            return False
        if self.isTernaryOperator() + _other.isTernaryOperator() == 1:
            return False
        if self.isTernaryOperator() and _other.isTernaryOperator() and \
                not (self.getCondition().equals(_other.getCondition()) and
                     self.getIfTrue().equals(_other.getIfTrue()) and self.getIfNot().equals(_other.getIfNot())):
            return False
        return True
