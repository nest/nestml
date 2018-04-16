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
from pynestml.meta_model.ASTExpressionElement import ASTExpressionNode
from pynestml.meta_model.ASTFunctionCall import ASTFunctionCall
from pynestml.meta_model.ASTVariable import ASTVariable


class ASTSimpleExpression(ASTExpressionNode):
    """
    This class is used to store a simple rhs, e.g. +42mV.
    ASTSimpleExpression, consisting of a single element without combining operator, e.g.,10mV, inf, V_m.
    Grammar:
    simpleExpression : functionCall
                   | BOOLEAN_LITERAL // true & false;
                   | (INTEGER|FLOAT) (variable)?
                   | isInf='inf'
                   | STRING_LITERAL
                   | variable;
    Attributes:
        __functionCall (ASTFunctionCall): A function call reference.
        __numericLiteral (int or float): A numeric literal.
        __variable (ASTVariable): A variable reference.
        __isBooleanTrue (bool): True if this is a boolean true literal.
        __isBooleanFalse (bool): True if this is a boolean false literal.
        __isInf (bool): True if this is a infinity literal.
        __string (str): A string literal.

    """
    __functionCall = None
    __numericLiteral = None
    __variable = None
    __isBooleanTrue = False
    __isBooleanFalse = False
    __isInf = False
    __string = None

    def __init__(self, _functionCall=None, _booleanLiteral=None, _numericLiteral=None, _isInf=False,
                 _variable=None, _string=None, source_position=None):
        """
        Standard constructor.
        :param _functionCall: a function call.
        :type _functionCall: ASTFunctionCall
        :param _booleanLiteral: a boolean value.
        :type _booleanLiteral: bool
        :param _numericLiteral: a numeric value.
        :type _numericLiteral: float/int
        :param _isInf: is inf symbol.
        :type _isInf: bool
        :param _variable: a variable object.
        :type _variable: ASTVariable
        :param _string: a single string literal
        :type _string: str
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        assert (_functionCall is None or isinstance(_functionCall, ASTFunctionCall)), \
            '(PyNestML.AST.SimpleExpression) Not a function call provided (%s)!' % type(_functionCall)
        assert (_booleanLiteral is None or isinstance(_booleanLiteral, bool)), \
            '(PyNestML.AST.SimpleExpression) Not a bool provided (%s)!' % type(_booleanLiteral)
        assert (_isInf is None or isinstance(_isInf, bool)), \
            '(PyNestML.AST.SimpleExpression) Not a bool provided (%s)!' % type(_isInf)
        assert (_variable is None or isinstance(_variable, ASTVariable)), \
            '(PyNestML.AST.SimpleExpression) Not a variable provided (%s)!' % type(_variable)
        assert (_numericLiteral is None or isinstance(_numericLiteral, int) or isinstance(_numericLiteral, float)), \
            '(PyNestML.AST.SimpleExpression) Not a number provided (%s)!' % type(_numericLiteral)
        assert (_string is None or isinstance(_string, str)), \
            '(PyNestML.AST.SimpleExpression) Not a string provided (%s)!' % type(_string)
        super(ASTSimpleExpression, self).__init__(source_position)
        self.__functionCall = _functionCall
        if _booleanLiteral is not None:
            if _booleanLiteral:
                self.__isBooleanTrue = True
            else:
                self.__isBooleanFalse = True
        self.__numericLiteral = _numericLiteral
        self.__isInf = _isInf
        self.__variable = _variable
        self.__string = _string
        return

    def is_function_call(self):
        """
        Returns whether it is a function call or not.
        :return: True if function call, otherwise False.
        :rtype: bool
        """
        return self.__functionCall is not None

    def get_function_call(self):
        """
        Returns the function call object.
        :return: the function call object.
        :rtype: ASTFunctionCall
        """
        return self.__functionCall

    def get_function_calls(self):
        """
        This function is used for better interactions with the general rhs meta_model class.
        :return: returns a single list with this function call if such an exists, otherwise an empty list
        :rtype: list(ASTFunctionCall)
        """
        ret = list()
        if self.is_function_call():
            ret.append(self.get_function_call())
        return ret

    def is_boolean_true(self):
        """
        Returns whether it is a boolean true literal.
        :return: True if true literal, otherwise False.
        :rtype: bool 
        """
        return self.__isBooleanTrue

    def is_boolean_false(self):
        """
        Returns whether it is a boolean false literal.
        :return: True if false literal, otherwise False.
        :rtype: bool
        """
        return self.__isBooleanFalse

    def is_numeric_literal(self):
        """
        Returns whether it is a numeric literal or not.
        :return: True if numeric literal, otherwise False.
        :rtype: bool
        """
        return self.__numericLiteral is not None

    def get_numeric_literal(self):
        """
        Returns the value of the numeric literal.
        :return: the value of the numeric literal.
        :rtype: int/float
        """
        return self.__numericLiteral

    def is_inf_literal(self):
        """
        Returns whether it is a infinity literal or not.
        :return: True if infinity literal, otherwise False.
        :rtype: bool
        """
        return self.__isInf

    def is_variable(self):
        """
        Returns whether it is a variable or not.
        :return: True if has a variable, otherwise False.
        :rtype: bool
        """
        return self.__variable is not None and self.__numericLiteral is None

    def get_variables(self):
        """
        This function is used for better interactions with the general rhs meta_model class.
        :return: returns a single list with this variable if such an exists, otherwise an empty list
        :rtype: list(ASTVariable)
        """
        ret = list()
        if self.is_variable():
            ret.append(self.get_variable())
        return ret

    def has_unit(self):
        """
        Returns whether this is a numeric literal with a defined unit.
        :return: True if numeric literal with unit, otherwise False. 
        :rtype: bool
        """
        return self.__variable is not None and self.__numericLiteral is not None

    def get_units(self):
        """
        This function is used for better interactions with the general rhs meta_model class.
        :return: returns a single list with unit if such an exists, otherwise an empty list
        :rtype: list(ASTVariable)
        """
        ret = list()
        if self.has_unit():
            ret.append(self.get_variable())
        return ret

    def get_variable(self):
        """
        Returns the variable.
        :return: the variable object.
        :rtype: ASTVariable
        """
        return self.__variable

    def is_string(self):
        """
        Returns whether this simple rhs is a string.
        :return: True if string, False otherwise.
        :rtype: bool
        """
        return self.__string is not None and isinstance(self.__string, str)

    def get_string(self):
        """
        Returns the string as stored in this simple rhs.
        :return: a string as stored in this rhs.
        :rtype: str
        """
        return self.__string

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.is_function_call():
            if self.get_function_call() is ast:
                return self
            elif self.get_function_call().get_parent(ast) is not None:
                return self.get_function_call().get_parent(ast)
        if self.__variable is not None:
            if self.__variable is ast:
                return self
            elif self.__variable.get_parent(ast) is not None:
                return self.__variable.get_parent(ast)
        return None

    def set_variable(self, variable):
        """
        Updates the variable of this node.
        :param variable: a single variable
        :type variable: ASTVariable
        """
        assert (variable is None or isinstance(variable, ASTVariable)), \
            '(PyNestML.AST.SimpleExpression) No or wrong type of variable provided (%s)!' % type(variable)
        self.__variable = variable
        return

    def set_function_call(self, function_call):
        """
        Updates the function call of this node.
        :param function_call: a single function call
        :type function_call: Union(ASTFunctionCall,None)
        """
        assert (function_call is None or isinstance(function_call, ASTVariable)), \
            '(PyNestML.AST.SimpleExpression) No or wrong type of function call provided (%s)!' % type(function_call)
        self.__functionCall = function_call
        return

    def __str__(self):
        """
        Returns the string representation of the simple rhs.
        :return: the operator as a string.
        :rtype: str
        """
        if self.is_function_call():
            return str(self.__functionCall)
        elif self.is_boolean_true():
            return 'True'
        elif self.is_boolean_false():
            return 'False'
        elif self.is_inf_literal():
            return 'inf'
        elif self.is_numeric_literal():
            if self.__variable is not None:
                return str(self.__numericLiteral) + str(self.__variable)
            else:
                return str(self.__numericLiteral)
        elif self.is_variable():
            return str(self.__variable)
        elif self.is_string():
            return self.get_string()
        else:
            raise RuntimeError('Simple rhs at %s not specified!' % str(self.get_source_position()))

    def equals(self, other=None):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return:True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTSimpleExpression):
            return False
        if self.is_function_call() + other.is_function_call() == 1:
            return False
        if self.is_function_call() and other.is_function_call() and not self.get_function_call().equals(
                other.get_function_call()):
            return False
        if self.get_numeric_literal() != other.get_numeric_literal():
            return False
        if self.is_boolean_false() != other.is_boolean_false() or self.is_boolean_true() != other.is_boolean_true():
            return False
        if self.is_variable() + other.is_variable() == 1:
            return False
        if self.is_variable() and other.is_variable() and not self.get_variable().equals(other.get_variable()):
            return False
        if self.is_inf_literal() != other.is_inf_literal():
            return False
        if self.is_string() + other.is_string() == 1:
            return False
        if self.get_string() != other.get_string():
            return False
        return True
