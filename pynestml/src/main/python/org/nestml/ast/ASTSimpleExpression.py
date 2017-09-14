#
# ASTSimpleExpression.py
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


from pynestml.src.main.python.org.nestml.ast.ASTFunctionCall import ASTFunctionCall
from pynestml.src.main.python.org.nestml.ast.ASTVariable import ASTVariable
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTSimpleExpression(ASTElement):
    """
    This class is used to store a simple expression, e.g. +42mV.
    ASTSimpleExpression, consisting of a single element without combining operator, e.g.,10mV, inf, V_m.
    Grammar:
    simpleExpression : functionCall
                   | BOOLEAN_LITERAL // true & false;
                   | (INTEGER|FLOAT) (variable)?
                   | isInf='inf'
                   | variable;
    """
    __functionCall = None
    __numericLiteral = None
    __variable = None
    __isBooleanTrue = False
    __isBooleanFalse = False
    __isInf = False

    def __init__(self, _functionCall=None, _booleanLiteral=None, _numericLiteral=None, _isInf=False,
                 _variable=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _functionCall: a function call.
        :type _functionCall: ASTFunctionCall
        :param _name: a string, e.g., a certain index.
        :type _name: str
        :param _booleanLiteral: a boolean value.
        :type _booleanLiteral: str
        :param _numericLiteral: a numeric value.
        :type _numericLiteral: float/int
        :param _isInf: is inf symbol.
        :type _isInf: bool
        :param _variable: a variable object.
        :type _variable: ASTVariable
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_functionCall is None or isinstance(_functionCall, ASTFunctionCall)), \
            '(PyNestML.AST.SimpleExpression) Not a function call provided.'
        assert (_booleanLiteral is None or isinstance(_booleanLiteral, bool)), \
            '(PyNestML.AST.SimpleExpression) Not a bool provided.'
        assert (_isInf is None or isinstance(_isInf, bool)), \
            '(PyNestML.AST.SimpleExpression) Not a bool provided.'
        assert (_variable is None or isinstance(_variable, ASTVariable)), \
            '(PyNestML.AST.SimpleExpression) Not a variable provided.'
        assert (_numericLiteral is None or isinstance(_numericLiteral, int) or isinstance(_numericLiteral, float)), \
            '(PyNestML.AST.SimpleExpression) Not a number handed over!'
        super(ASTSimpleExpression, self).__init__(_sourcePosition)
        self.__functionCall = _functionCall
        if _booleanLiteral is not None:
            if _booleanLiteral is 'True' or _booleanLiteral is 'true':
                self.__isBooleanTrue = True
            else:
                self.__isBooleanFalse = True
        self.__numericLiteral = _numericLiteral
        self.__isInf = _isInf
        self.__variable = _variable

    @classmethod
    def makeASTSimpleExpression(cls, _functionCall=None, _booleanLiteral=None, _numericLiteral=None,
                                _isInf=False, _variable=None, _sourcePosition=None):
        """
        The factory method of the ASTSimpleExpression class.
        :param _functionCall: a function call.
        :type _functionCall: ASTFunctionCall
        :param _name: a string, e.g., a certain index.
        :type _name: str
        :param _booleanLiteral: a boolean value.
        :type _booleanLiteral: str
        :param _numericLiteral: a numeric value.
        :type _numericLiteral: float/int
        :param _isInf: is inf symbol.
        :type _isInf: bool
        :param _variable: a variable object.
        :type _variable: ASTVariable
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTSimpleExpression object.
        :rtype: ASTSimpleExpression
        """
        return cls(_functionCall, _booleanLiteral, _numericLiteral, _isInf, _variable, _sourcePosition)

    def isFunctionCall(self):
        """
        Returns whether it is a function call or not.
        :return: True if function call, otherwise False.
        :rtype: bool
        """
        return self.__functionCall is not None

    def getFunctionCall(self):
        """
        Returns the function call object.
        :return: the function call object.
        :rtype: ASTFunctionCall
        """
        return self.__functionCall

    def isBooleanTrue(self):
        """
        Returns whether it is a boolean true literal.
        :return: True if true literal, otherwise False.
        :rtype: bool 
        """
        return self.__isBooleanTrue

    def isBooleanFalse(self):
        """
        Returns whether it is a boolean false literal.
        :return: True if false literal, otherwise False.
        :rtype: bool
        """
        return self.__isBooleanFalse

    def isNumericLiteral(self):
        """
        Returns whether it is a numeric literal or not.
        :return: True if numeric literal, otherwise False.
        :rtype: bool
        """
        return self.__numericLiteral is not None

    def getNumericLiteral(self):
        """
        Returns the value of the numeric literal.
        :return: the value of the numeric literal.
        :rtype: int/float
        """
        return self.__numericLiteral

    def isInfLiteral(self):
        """
        Returns whether it is a infinity literal or not.
        :return: True if infinity literal, otherwise False.
        :rtype: bool
        """
        return self.__isInf

    def isVariable(self):
        """
        Returns whether it is a variable or not.
        :return: True if has a variable, otherwise False.
        :rtype: bool
        """
        return self.__variable is not None and self.__numericLiteral is None

    def hasUnit(self):
        """
        Returns whether this is a numeric literal with a defined unit.
        :return: True if numeric literal with unit, otherwise False. 
        :rtype: bool
        """
        return self.__variable is not None and self.__numericLiteral is not None

    def getVariable(self):
        """
        Returns the variable.
        :return: the variable object.
        :rtype: ASTVariable
        """
        return self.__variable

    def printAST(self):
        """
        Returns the string representation of the simple expression.
        :return: the operator as a string.
        :rtype: str
        """
        if self.isFunctionCall():
            return self.__functionCall.printAST()
        elif self.isBooleanTrue():
            return 'True'
        elif self.isBooleanFalse():
            return 'False'
        elif self.isInfLiteral():
            return 'inf'
        elif self.isNumericLiteral():
            if self.isVariable():
                return str(self.__numericLiteral) + self.__variable.printAST()
            else:
                return str(self.__numericLiteral)
        elif self.isVariable():
            return self.__variable.printAST()
        else:
            raise Exception("(PyNESTML.AST.SimpleExpression.Print) Simple expression not specified.")
