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


from pynestml.src.main.python.org.nestml.ast.ASTUnaryOperator import ASTUnaryOperator
from pynestml.src.main.python.org.nestml.ast.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.src.main.python.org.nestml.ast.ASTComparisonOperator import ASTComparisonOperator
from pynestml.src.main.python.org.nestml.ast.ASTBitOperator import ASTBitOperator
from pynestml.src.main.python.org.nestml.ast.ASTLogicalOperator import ASTLogicalOperator
from pynestml.src.main.python.org.nestml.ast.ASTSimpleExpression import ASTSimpleExpression
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


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
    __hasLeftParentheses = False
    __hasRightParentheses = False
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
    # the corresponding type symbol.
    __typeSymbol = None

    def __init__(self, _hasLeftParentheses=False, _hasRightParentheses=False, _unaryOperator=None, _isLogicalNot=False,
                 _expression=None, _lhs=None, _binaryOperator=None, _rhs=None, _condition=None, _ifTrue=None,
                 _ifNot=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _hasLeftParentheses: is encapsulated in brackets (left). 
        :type _hasLeftParentheses: bool
        :param _hasRightParentheses: is encapsulated in brackets (right).
        :type _hasRightParentheses: bool
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
            '(PyNestML.AST.Expression) Not an unary operator!'
        assert ((_expression is None) or (isinstance(_expression, ASTExpression)) or (
            isinstance(_expression, ASTSimpleExpression))), '(NESTML) Not an expression!'
        assert ((_binaryOperator is None) or (isinstance(_binaryOperator, ASTArithmeticOperator) or
                                              (isinstance(_binaryOperator, ASTBitOperator)) or
                                              (isinstance(_binaryOperator, ASTLogicalOperator)) or
                                              (isinstance(_binaryOperator, ASTComparisonOperator)))), \
            '(PyNestML.AST.Expression) Not a binary operator!'
        super(ASTExpression, self).__init__(_sourcePosition)
        self.__hasLeftParentheses = _hasLeftParentheses
        self.__hasRightParentheses = _hasRightParentheses
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

    @classmethod
    def makeExpression(cls, _hasLeftParentheses=False, _hasRightParentheses=False, _unaryOperator=None,
                       _isLogicalNot=False, _expression=None, _sourcePosition=None):
        """
        The factory method used to create expression which are either encapsulated in parentheses (e.g., (10mV)) 
        OR have a unary (e.g., ~bitVar), OR are negated (e.g., not logVar), or are simple expression (e.g., 10mV).
        :param _hasLeftParentheses: is encapsulated in brackets (left). 
        :type _hasLeftParentheses: bool
        :param _hasRightParentheses: is encapsulated in brackets (right).
        :type _hasRightParentheses: bool
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
        assert ((_hasLeftParentheses ^ _hasRightParentheses) is False), \
            '(PyNestML.AST.Expression) Parenthesis on both sides of expression expected!'
        return cls(_hasLeftParentheses=_hasLeftParentheses, _hasRightParentheses=_hasRightParentheses,
                   _unaryOperator=_unaryOperator, _isLogicalNot=_isLogicalNot, _expression=_expression,
                   _sourcePosition=_sourcePosition)

    @classmethod
    def makeCompoundExpression(cls, _lhs=None, _binaryOperator=None, _rhs=None, _sourcePosition=None):
        """
        The factory method used to create compound expressions, e.g. 10mV + V_m.
        :param _lhs: the left-hand side expression.
        :type _lhs: ASTExpression
        :param _binaryOperator: a binary operator, e.g., a comparison operator or a logical operator.
        :type _binaryOperator: one of ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTExpression object.
        :rtype: ASTExpression
        """
        assert (_lhs is not None and isinstance(_lhs, ASTExpression)), \
            '(PyNestML.AST.Expression) The left-hand side is empty or not an expression!'
        assert (_rhs is not None and isinstance(_rhs, ASTExpression)), \
            '(PyNestML.AST.Expression) The right-hand side is empty or not an expression!'
        assert (_binaryOperator is not None), \
            '(PyNestML.AST.Expression) The binary operator is empty!'
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
        assert (_condition is not None and isinstance(_condition, ASTExpression)), \
            '(PyNestML.AST.Expression) Condition of ternary operator is empty or not an expression!'
        assert (_ifTrue is not None and isinstance(_ifTrue, ASTExpression)), \
            '(PyNestML.AST.Expression) The if-true case of ternary operator is empty or not an expression!'
        assert (_ifNot is not None and isinstance(_ifNot, ASTExpression)), \
            '(PyNestML.AST.Expression) The if-not case of ternary operator is empty or not an expression!'
        return cls(_condition=_condition, _ifTrue=_ifTrue, _ifNot=_ifNot, _sourcePosition=_sourcePosition)

    def isSimpleExpression(self):
        """
        Returns whether it is a simple expression, e.g. 10mV.
        :return: True if simple expression, otherwise false.
        :rtype: bool
        """
        return (self.__expression is not None) and isinstance(self.__expression, ASTSimpleExpression)

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

    def hasLeftParentheses(self):
        """
        Returns whether the expression has a left parenthesis on the left side.
        :return: True if parenthesis on the left side, otherwise False.
        :rtype: bool
        """
        return self.__hasLeftParentheses

    def hasRightParentheses(self):
        """
        Returns whether the expression has a left parenthesis on the right side.
        :return: True if parenthesis on the right side, otherwise False.
        :rtype: bool
        """
        return self.__hasRightParentheses

    def isLogicalNot(self):
        """
        Returns whether the expression is negated by a logical not.
        :return: True if negated, otherwise False.  
        :rtype: bool
        """
        return self.__isLogicalNot

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
        if self.isSimpleExpression() and self.getExpression().getVariables():
            ret.append(self.getExpression().getVariables())
        elif self.isUnaryOperator():
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
        if self.isSimpleExpression() and self.getExpression().hasUnit():
            ret.append(self.getExpression().getVariable())
        elif self.isUnaryOperator():
            ret.extend(self.getExpression().getUnits())
        elif self.isCompoundExpression():
            ret.extend(self.getLhs().getUnits())
            ret.extend(self.getRhs().getUnits())
        elif self.isTernaryOperator():
            ret.extend(self.getCondition().getUnits())
            ret.extend(self.getIfTrue().getUnits())
            ret.extend(self.getIfNot().getUnits())
        return ret

    def getFunctions(self):
        """
        Returns a list of all function calls as used in this expression
        :return: a list of all function calls in this expression.
        :rtype: list(ASTFunctionCall)
        """
        ret = list()
        if self.isSimpleExpression() and self.getExpression().getFunctionCall():
            ret.append(self.getExpression().getFunctionCall())
        elif self.isUnaryOperator():
            ret.extend(self.getExpression().getFunctions())
        elif self.isCompoundExpression():
            ret.extend(self.getLhs().getFunctions())
            ret.extend(self.getRhs().getFunctions())
        elif self.isTernaryOperator():
            ret.extend(self.getCondition().getFunctions())
            ret.extend(self.getIfTrue().getFunctions())
            ret.extend(self.getIfNot().getFunctions())
        return ret

    def getTypeSymbol(self):
        """
        Returns the type symbol of this expression.
        :return: a single type symbol.
        :rtype: TypeSymbol
        """
        return self.__typeSymbol

    def setTypeSymbol(self, _typeSymbol=None):
        """
        Updates the current type symbol to the handed over one.
        :param _typeSymbol: a single type symbol object.
        :type _typeSymbol: TypeSymbol
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        assert (_typeSymbol is not None and isinstance(_typeSymbol, TypeSymbol)), \
            '(PyNestML.AST.Expression) No or wrong type of type symbol provided (%s)!' % type(_typeSymbol)
        self.__typeSymbol = _typeSymbol

    def printAST(self):
        """
        Returns the string representation of the expression.
        :return: the expression as a string.
        :rtype: str
        """
        ret = ''
        if self.isExpression():
            if self.hasLeftParentheses():
                ret += '('
            if self.isLogicalNot():
                ret += 'not '
            if self.isUnaryOperator():
                ret += self.getUnaryOperator().printAST()
            ret += self.getExpression().printAST()
            if self.hasRightParentheses():
                ret += ')'
        elif self.isCompoundExpression():
            ret += self.getLhs().printAST()
            ret += self.getBinaryOperator().printAST()
            ret += self.getRhs().printAST()
        elif self.isTernaryOperator():
            ret += self.getCondition().printAST() + '?' + self.getIfTrue().printAST() + ':' + self.getIfNot().printAST()
        return ret
