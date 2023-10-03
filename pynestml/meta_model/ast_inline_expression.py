# -*- coding: utf-8 -*-
#
# ast_inline_expression.py
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

from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_namespace_decorator import ASTNamespaceDecorator


class ASTInlineExpression(ASTNode):
    """
    Stores a single declaration of an inline expression, e.g.,
        inline v_init mV = V_m - 50mV.
    Grammar:
        inline : (recordable='recordable')? INLINE_KEYWORD variableName=NAME datatype '=' rhs;
    Attributes:
        is_recordable = False
        variable_name = None
        data_type = None
        expression = None
    """

    def __init__(self, is_recordable=False, variable_name=None, data_type=None, expression=None, decorators=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_recordable: (optional) is this function recordable or not.
        :type is_recordable: bool
        :param variable_name: the name of the variable.
        :type variable_name: str
        :param data_type: the datatype of the function.
        :type data_type: ASTDataType
        :param expression: the computation rhs
        :type expression: ASTExpression
        """
        super(ASTInlineExpression, self).__init__(*args, **kwargs)
        if decorators is None:
            decorators = []
        self.is_recordable = is_recordable
        self.variable_name = variable_name
        self.data_type = data_type
        self.expression = expression
        self.decorators = decorators

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTInlineExpression
        """
        data_type_dup = None
        if self.data_type:
            data_type_dup = self.data_type.clone()
        expression_dup = None
        if self.expression:
            expression_dup = self.expression.clone()
        decorators_dup = None
        if self.decorators:
            decorators_dup = [dec.clone() if isinstance(dec, ASTNamespaceDecorator) else str(dec) for dec in
                              self.decorators]
        dup = ASTInlineExpression(is_recordable=self.is_recordable,
                                  variable_name=self.variable_name,
                                  data_type=data_type_dup,
                                  expression=expression_dup,
                                  decorators=decorators_dup,
                                  # ASTNode common attributes:
                                  source_position=self.source_position,
                                  scope=self.scope,
                                  comment=self.comment,
                                  pre_comments=[s for s in self.pre_comments],
                                  in_comment=self.in_comment,
                                  implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_decorators(self):
        """
        """
        return self.decorators

    def get_variable_name(self):
        """
        Returns the variable name.
        :return: the name of the variable.
        :rtype: str
        """
        return self.variable_name

    def set_variable_name(self, variable_name: str):
        """
        Set the variable name.
        :param variable_name: the name of the variable.
        """
        self.variable_name = variable_name

    def get_data_type(self):
        """
        Returns the data type as an object of ASTDatatype.
        :return: the type as an object of ASTDatatype.
        :rtype: ast_data_type
        """
        return self.data_type

    def get_expression(self):
        """
        Returns the rhs as an object of ASTExpression.
        :return: the rhs as an object of ASTExpression.
        :rtype: ast_expression
        """
        return self.expression

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.get_data_type() is ast:
            return self
        if self.get_data_type().get_parent(ast) is not None:
            return self.get_data_type().get_parent(ast)
        if self.get_expression() is ast:
            return self
        if self.get_expression().get_parent(ast) is not None:
            return self.get_expression().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTInlineExpression):
            return False
        if self.is_recordable != other.is_recordable:
            return False
        if self.get_variable_name() != other.get_variable_name():
            return False
        if not self.get_data_type().equals(other.get_data_type()):
            return False
        return self.get_expression().equals(other.get_expression())
