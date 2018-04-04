#
# ASTDeclaration.py
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


from pynestml.modelprocessor.ASTNode import ASTNode
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTDataType import ASTDataType


class ASTDeclaration(ASTNode):
    """
    This class is used to store declarations.
    ASTDeclaration A variable declaration. It can be a simple declaration defining one or multiple variables:
    'a,b,c real = 0'. Or an function declaration 'function a = b + c'.
    @attribute hide is true iff. declaration is not traceable.
    @attribute function is true iff. declaration is an function.
    @attribute vars          List with variables
    @attribute Datatype      Obligatory data type, e.g. 'real' or 'mV/s'
    @attribute sizeParameter An optional array parameter. E.g. 'tau_syn ms[n_receptors]'
    @attribute expr An optional initial rhs, e.g. 'a real = 10+10'
    @attribute invariants List with optional invariants.
    Grammar:
        declaration :
            ('recordable')? ('function')?
            variable (',' variable)*
            datatype
            ('[' sizeParameter=NAME ']')?
            ( '=' rhs)?
            ('[[' invariant=rhs ']]')?;
    """
    __isRecordable = False
    __isFunction = False
    __variables = None
    __dataType = None
    __sizeParameter = None
    __expression = None
    __invariant = None

    def __init__(self, is_recordable=False, is_function=False, _variables=list(), data_type=None, size_parameter=None,
                 expression=None, invariant=None, source_position=None):
        """
        Standard constructor.
        :param is_recordable: is a recordable declaration.
        :type is_recordable: bool
        :param is_function: is a function declaration.
        :type is_function: bool
        :param _variables: a list of variables.
        :type _variables: list(ASTVariable)
        :param data_type: the data type.
        :type data_type: ASTDataType
        :param size_parameter: an optional size parameter.
        :type size_parameter: str
        :param expression: an optional right-hand side rhs.
        :type expression: ASTExpression
        :param invariant: a optional invariant.
        :type invariant: ASTExpression.
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        super(ASTDeclaration, self).__init__(source_position)
        self.__isRecordable = is_recordable
        self.__isFunction = is_function
        self.__variables = _variables
        self.__dataType = data_type
        self.__sizeParameter = size_parameter
        self.__expression = expression
        self.__invariant = invariant
        return

    def is_recordable(self):
        """
        Returns whether the declaration is recordable or not.
        :return: True if recordable, else False.
        :rtype: bool
        """
        return isinstance(self.__isRecordable, bool) and self.__isRecordable

    def is_function(self):
        """
        Returns whether the declaration is a function or not.
        :return: True if function, else False.
        :rtype: bool
        """
        return isinstance(self.__isFunction, bool) and self.__isFunction

    def get_variables(self):
        """
        Returns the set of left-hand side variables.
        :return: a list of variables.
        :rtype: list(ASTVariables)
        """
        return self.__variables

    def get_data_type(self):
        """
        Returns the data type.
        :return: a data type object.
        :rtype: ASTDataType
        """
        return self.__dataType

    def has_size_parameter(self):
        """
        Returns whether the declaration has a size parameter or not.
        :return: True if has size parameter, else False.
        :rtype: bool
        """
        return self.__sizeParameter is not None

    def get_size_parameter(self):
        """
        Returns the size parameter.
        :return: the size parameter.
        :rtype: str
        """
        return self.__sizeParameter

    def set_size_parameter(self, _parameter):
        """
        Updates the current size parameter to a new value.
        :param _parameter: the size parameter
        :type _parameter: str
        """
        assert (_parameter is not None and isinstance(_parameter, str)), \
            '(PyNestML.AST.Declaration) No or wrong type of size parameter provided (%s)!' % type(_parameter)
        self.__sizeParameter = _parameter
        return

    def has_expression(self):
        """
        Returns whether the declaration has a right-hand side rhs or not.
        :return: True if right-hand side rhs declared, else False.
        :rtype: bool
        """
        return self.__expression is not None

    def get_expression(self):
        """
        Returns the right-hand side rhs.
        :return: the right-hand side rhs.
        :rtype: ASTExpression
        """
        return self.__expression

    def has_invariant(self):
        """
        Returns whether the declaration has a invariant or not.
        :return: True if has invariant, otherwise False.
        :rtype: bool
        """
        return self.__invariant is not None

    def get_invariant(self):
        """
        Returns the invariant.
        :return: the invariant
        :rtype: ASTExpression
        """
        return self.__invariant

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary ast node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for var in self.get_variables():
            if var is ast:
                return self
            elif var.get_parent(ast) is not None:
                return var.get_parent(ast)
        if self.get_data_type() is ast:
            return self
        elif self.get_data_type().get_parent(ast) is not None:
            return self.get_data_type().get_parent(ast)
        if self.has_expression():
            if self.get_expression() is ast:
                return self
            elif self.get_expression().get_parent(ast) is not None:
                return self.get_expression().get_parent(ast)
        if self.has_invariant():
            if self.get_invariant() is ast:
                return self
            elif self.get_invariant().get_parent(ast) is not None:
                return self.get_invariant().get_parent(ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the declaration.
        :return: a string representation.
        :rtype: str
        """
        ret = ''
        if self.is_recordable():
            ret += 'recordable '
        if self.is_function():
            ret += 'function '
        for var in self.get_variables():
            ret += str(var)
            if self.get_variables().index(var) < len(self.get_variables()) - 1:
                ret += ','
        ret += ' ' + str(self.get_data_type()) + ' '
        if self.has_size_parameter():
            ret += '[' + self.get_size_parameter() + ']'
        if self.has_expression():
            ret += ' = ' + str(self.get_expression()) + ' '
        if self.has_invariant():
            ret += ' [[' + str(self.get_invariant()) + ']]'
        return ret

    def equals(self, other=None):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTDeclaration):
            return False
        if not (self.is_function() == other.is_function() and self.is_recordable() == other.is_recordable()):
            return False
        if self.get_size_parameter() != other.get_size_parameter():
            return False
        if len(self.get_variables()) != len(other.get_variables()):
            return False
        my_vars = self.get_variables()
        your_vars = other.get_variables()
        for i in range(0, len(my_vars)):
            # caution, here the order is also checked
            if not my_vars[i].equals(your_vars[i]):
                return False
        if self.has_invariant() + other.has_invariant() == 1:
            return False
        if self.has_invariant() and other.has_invariant() and not self.get_invariant().equals(other.get_invariant()):
            return False
        return self.get_data_type().equals(other.get_data_type()) and self.get_expression().equals(other.get_expression())
