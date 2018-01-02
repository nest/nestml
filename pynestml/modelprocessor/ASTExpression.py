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
from pynestml.modelprocessor.ASTNode import ASTElement
from pynestml.modelprocessor.Either import Either


class ASTExpression(ASTElement):
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

    def __init__(self, _isEncapsulated=False, _unaryOperator=None, _isLogicalNot=False,
                 _expression=None, _lhs=None, _binaryOperator=None, _rhs=None, _condition=None, _ifTrue=None,
                 _ifNot=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _isEncapsulated: is encapsulated in brackets.
        :type _isEncapsulated: bool
        :param _unaryOperator: combined by unary operator, e.g., ~.
        :type _unaryOperator: ASTUnaryOperator
        :param _isLogicalNot: is a negated expression.
        :type _isLogicalNot: bool
        :param _expression: the expression either encapsulated in brackets or negated or with a with a unary op, or 
        a simple expression.
        :type _expression: ASTExpression
        :param _lhs: the left-hand side expression.
        :type _lhs: ASTExpression
        :param _binaryOperator: a binary operator, e.g., a comparison operator or a logical operator.
        :type _binaryOperator: ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression
        :param _condition: the condition of a ternary operator
        :type _condition: ASTExpression
        :param _ifTrue: if condition holds, this expression is executed.
        :type _ifTrue: ASTExpression
        :param _ifNot: if condition does not hold, this expression is executed.
        :type _ifNot: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert ((_unaryOperator is None) or (isinstance(_unaryOperator, ASTUnaryOperator))), \
            '(PyNestML.AST.Expression) Wrong type of unary operator provided (%s)!' % type(_unaryOperator)
        assert ((_expression is None) or (isinstance(_expression, ASTExpression)) or (
            isinstance(_expression, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) Wrong type of expression provided (%s)!' % type(_expression)
        assert ((_binaryOperator is None) or (isinstance(_binaryOperator, ASTArithmeticOperator) or
                                              (isinstance(_binaryOperator, ASTBitOperator)) or
                                              (isinstance(_binaryOperator, ASTLogicalOperator)) or
                                              (isinstance(_binaryOperator, ASTComparisonOperator)))), \
            '(PyNestML.AST.Expression) Wrong type of binary operator provided (%s)!' % type(_binaryOperator)
        assert (_isEncapsulated is None or isinstance(_isEncapsulated, bool)), \
            '(PyNestML.AST.Expression) Wrong type of parenthesis parameter provided (%s)' \
            % type(_isEncapsulated)
        assert (_condition is None or isinstance(_condition, ASTExpression)
                or isinstance(_condition, ASTSimpleExpression)), \
            '(PyNestML.AST.Expression) Wrong type of condition provided (%s)!' % type(_condition)
        assert (_ifTrue is None or isinstance(_ifTrue, ASTExpression) or isinstance(_ifTrue, ASTSimpleExpression)), \
            '(PyNestML.AST.Expression) Wrong type of if-true consequence provided (%s)!' % type(_ifTrue)
        assert (_ifNot is None or isinstance(_ifNot, ASTExpression) or isinstance(_ifNot, ASTSimpleExpression)), \
            '(PyNestML.AST.Expression) Wrong type of if-not consequence provided (%s)!' % type(_ifNot)
        super(ASTExpression, self).__init__(_sourcePosition)
        self.__isEncapsulated = _isEncapsulated
        self.__isLogicalNot = _isLogicalNot
        self.__unaryOperator = _unaryOperator
        self.__expression = _expression
        # lhs and rhs combined by an operator
        self.__lhs = _lhs
        self.__binaryOperator = _binaryOperator
        self.__rhs = _rhs
        # ternary operator
        assert (
            (_condition is None) or (isinstance(_condition, ASTExpression)) or (
                isinstance(_condition, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) Condition not an expression!'
        assert (
            (_ifTrue is None) or (isinstance(_ifTrue, ASTExpression)) or (isinstance(_ifTrue, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) If-true part of ternary operator not an expression!'
        assert ((_ifNot is None) or (isinstance(_ifNot, ASTExpression)) or (isinstance(_ifNot, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) If-not part of ternary operator not an expression!'
        self.__condition = _condition
        self.__ifTrue = _ifTrue
        self.__ifNot = _ifNot
        return

    @classmethod
    def makeExpression(cls, _isEncapsulated=False, _unaryOperator=None,
                       _isLogicalNot=False, _expression=None, _sourcePosition=None):
        """
        The factory method used to create expression which are either encapsulated in parentheses (e.g., (10mV)) 
        OR have a unary (e.g., ~bitVar), OR are negated (e.g., not logVar), or are simple expression (e.g., 10mV).
        :param _isEncapsulated: is encapsulated in brackets.
        :type _isEncapsulated: bool
        :param _unaryOperator: combined by unary operator, e.g., ~.
        :type _unaryOperator: ASTUnaryOperator
        :param _isLogicalNot: is a negated expression.
        :type _isLogicalNot: bool
        :param _expression: the expression either encapsulated in brackets or negated or with a with a unary op, or a 
        simple expression.
        :type _expression: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTExpression object.
        :rtype: ASTExpression
        """
        return cls(_isEncapsulated=_isEncapsulated, _unaryOperator=_unaryOperator, _isLogicalNot=_isLogicalNot,
                   _expression=_expression, _sourcePosition=_sourcePosition)

    @classmethod
    def makeCompoundExpression(cls, _lhs=None, _binaryOperator=None, _rhs=None, _sourcePosition=None):
        """
        The factory method used to create compound expressions, e.g. 10mV + V_m.
        :param _lhs: the left-hand side expression.
        :type _lhs: ASTExpression or ASTSimpleExpression
        :param _binaryOperator: a binary operator, e.g., a comparison operator or a logical operator.
        :type _binaryOperator: one of ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression or ASTSimpleExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTExpression object.
        :rtype: ASTExpression
        """
        assert (_lhs is not None and (isinstance(_lhs, ASTExpression) or isinstance(_lhs, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) The left-hand side is empty or not an expression (%s)!' % type(_lhs)
        assert (_rhs is not None and (isinstance(_rhs, ASTExpression) or isinstance(_rhs, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) The right-hand side is empty or not an expression (%s)!' % type(_rhs)
        assert (_binaryOperator is not None and (isinstance(_binaryOperator, ASTBitOperator) or
                                                 isinstance(_binaryOperator, ASTComparisonOperator) or
                                                 isinstance(_binaryOperator, ASTLogicalOperator) or
                                                 isinstance(_binaryOperator, ASTArithmeticOperator))), \
            '(PyNestML.AST.Expression) No or wrong type of binary operator provided (%s)!' % type(_binaryOperator)
        return cls(_lhs=_lhs, _binaryOperator=_binaryOperator, _rhs=_rhs, _sourcePosition=_sourcePosition)

    @classmethod
    def makeTernaryExpression(cls, _condition=None, _ifTrue=None, _ifNot=None, _sourcePosition=None):
        """
        The factory method used to create a ternary operator expression, e.g., 10mV<V_m?10mV:V_m
        :param _condition: the condition of a ternary operator
        :type _condition: ASTExpression
        :param _ifTrue: if condition holds, this expression is executed.
        :type _ifTrue: ASTExpression
        :param _ifNot: if condition does not hold, this expression is executed.
        :type _ifNot: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTExpression object.
        :rtype: ASTExpression
        """
        assert (_condition is not None and (isinstance(_condition, ASTExpression) or
                                            isinstance(_condition, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) No or wrong type of condition provided (%s)!' % type(_condition)
        assert (_ifTrue is not None and (isinstance(_ifTrue, ASTExpression) or
                                         isinstance(_ifTrue, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) No or wrong type of if-true case provided (%s)!' % type(_ifTrue)
        assert (_ifNot is not None and (isinstance(_ifNot, ASTExpression) or
                                        isinstance(_ifNot, ASTSimpleExpression))), \
            '(PyNestML.AST.Expression) No or wrong type of if-not case provided (%s)!' % type(_ifNot)
        return cls(_condition=_condition, _ifTrue=_ifTrue, _ifNot=_ifNot, _sourcePosition=_sourcePosition)

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
