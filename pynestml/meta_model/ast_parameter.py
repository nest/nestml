# -*- coding: utf-8 -*-
#
# ast_parameter.py
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


from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_node import ASTNode


class ASTParameter(ASTNode):
    """
    This class is used to store a single function parameter definition.
    ASTParameter represents singe:
      output: spike
    @attribute compartments Lists with compartments.
    Grammar:
        parameter : NAME datatype;
    Attributes:
        name (str): The name of the parameter.
        data_type (ASTDataType): The data type of the parameter.
    """

    def __init__(self, name=None, data_type=None, *args, **kwargs):
        """
        Standard constructor.
        :param name: the name of the parameter.
        :type name: str
        :param data_type: the type of the parameter.
        :type data_type: ASTDataType
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.AST.Parameter) No or wrong type of name provided (%s)!' % type(name)
        assert (data_type is not None and isinstance(data_type, ASTDataType)), \
            '(PyNestML.AST.Parameter) No or wrong type of datatype provided (%s)!' % type(data_type)
        super(ASTParameter, self).__init__(*args, **kwargs)
        self.data_type = data_type
        self.name = name

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTParameter
        """
        dup = ASTParameter(name=self.name,
                           data_type=self.data_type.clone(),
                           # ASTNode common attributes:
                           source_position=self.source_position,
                           scope=self.scope,
                           comment=self.comment,
                           pre_comments=[s for s in self.pre_comments],
                           in_comment=self.in_comment,
                           post_comments=[s for s in self.post_comments],
                           implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_name(self):
        """
        Returns the name of the parameter.
        :return: the name of the parameter.
        :rtype: str
        """
        return self.name

    def get_data_type(self):
        """
        Returns the data type of the parameter.
        :return: the data type of the parameter.
        :rtype: ASTDataType
        """
        return self.data_type

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
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTParameter):
            return False
        return self.get_name() == other.get_name() and self.get_data_type().equals(other.get_data_type())
