# -*- coding: utf-8 -*-
#
# ast_declaration.py
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

from typing import Optional, List

from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable


class ASTDeclaration(ASTNode):
    """
    This class is used to store declarations.
    ASTDeclaration A variable declaration. It can be a simple declaration defining one or multiple variables:
    'a,b,c real = 0'. Or an function declaration 'function a = b + c'.
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
    Attributes:
        is_recordable = False
        is_function = False
        variables = None
        data_type = None
        size_parameter = None
        expression = None
        invariant = None
    """

    def __init__(self, is_recordable: bool = False, is_function: bool = False, _variables: Optional[List[ASTVariable]] = None, data_type: Optional[ASTDataType] = None, size_parameter: Optional[str] = None,
                 expression: Optional[ASTExpression] = None, invariant: Optional[ASTExpression] = None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_recordable: is a recordable declaration.
        :type is_recordable: bool
        :param is_function: is a function declaration.
        :type is_function: bool
        :param _variables: a list of variables.
        :type _variables: Optional[List[ASTVariable]]
        :param data_type: the data type.
        :type data_type: Optional[ASTDataType]
        :param size_parameter: an optional size parameter.
        :type size_parameter: Optional[str]
        :param expression: an optional right-hand side rhs.
        :type expression: ASTExpression
        :param invariant: a optional invariant.
        :type invariant: ASTExpression
        """
        super(ASTDeclaration, self).__init__(*args, **kwargs)
        self.is_recordable = is_recordable
        self.is_function = is_function
        if _variables is None:
            _variables = []
        self.variables = _variables
        self.data_type = data_type
        self.size_parameter = size_parameter
        self.expression = expression
        self.invariant = invariant

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTDeclaration
        """
        variables_dup = None
        if self.variables:
            variables_dup = [var.clone() for var in self.variables]
        data_type_dup = None
        if self.data_type:
            data_type_dup = self.data_type.clone()
        expression_dup = None
        if self.expression:
            expression_dup = self.expression.clone()
        invariant_dup = None
        if self.invariant:
            invariant_dup = self.invariant.clone()
        dup = ASTDeclaration(is_recordable=self.is_recordable,
                             is_function=self.is_function,
                             _variables=variables_dup,
                             data_type=data_type_dup,
                             size_parameter=self.size_parameter,
                             expression=expression_dup,
                             invariant=invariant_dup,
                             # ASTNode common attributes:
                             source_position=self.source_position,
                             scope=self.scope,
                             comment=self.comment,
                             pre_comments=[s for s in self.pre_comments],
                             in_comment=self.in_comment,
                             post_comments=[s for s in self.post_comments],
                             implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_variables(self):
        """
        Returns the set of left-hand side variables.
        :return: a list of variables.
        :rtype: list(ASTVariables)
        """
        return self.variables

    def get_data_type(self):
        """
        Returns the data type.
        :return: a data type object.
        :rtype: ASTDataType
        """
        return self.data_type

    def has_size_parameter(self):
        """
        Returns whether the declaration has a size parameter or not.
        :return: True if has size parameter, else False.
        :rtype: bool
        """
        return self.size_parameter is not None

    def get_size_parameter(self):
        """
        Returns the size parameter.
        :return: the size parameter.
        :rtype: str
        """
        return self.size_parameter

    def set_size_parameter(self, _parameter):
        """
        Updates the current size parameter to a new value.
        :param _parameter: the size parameter
        :type _parameter: str
        """
        assert (_parameter is not None and isinstance(_parameter, str)), \
            '(PyNestML.AST.Declaration) No or wrong type of size parameter provided (%s)!' % type(_parameter)
        self.size_parameter = _parameter

    def has_expression(self):
        """
        Returns whether the declaration has a right-hand side rhs or not.
        :return: True if right-hand side rhs declared, else False.
        :rtype: bool
        """
        return self.expression is not None

    def get_expression(self):
        """
        Returns the right-hand side rhs.
        :return: the right-hand side rhs.
        :rtype: ASTExpression
        """
        return self.expression

    def set_expression(self, expr):
        # type: (ASTExpression) -> None
        self.expression = expr

    def has_invariant(self):
        """
        Returns whether the declaration has a invariant or not.
        :return: True if has invariant, otherwise False.
        :rtype: bool
        """
        return self.invariant is not None

    def get_invariant(self):
        """
        Returns the invariant.
        :return: the invariant
        :rtype: ASTExpression
        """
        return self.invariant

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for var in self.get_variables():
            if var is ast:
                return self
            if var.get_parent(ast) is not None:
                return var.get_parent(ast)
        if self.get_data_type() is ast:
            return self
        if self.get_data_type().get_parent(ast) is not None:
            return self.get_data_type().get_parent(ast)
        if self.has_expression():
            if self.get_expression() is ast:
                return self
            if self.get_expression().get_parent(ast) is not None:
                return self.get_expression().get_parent(ast)
        if self.has_invariant():
            if self.get_invariant() is ast:
                return self
            if self.get_invariant().get_parent(ast) is not None:
                return self.get_invariant().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTDeclaration):
            return False
        if not (self.is_function == other.is_function and self.is_recordable == other.is_recordable):
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
        return self.get_data_type().equals(other.get_data_type()) and self.get_expression().equals(
            other.get_expression())
