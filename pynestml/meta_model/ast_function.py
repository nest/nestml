# -*- coding: utf-8 -*-
#
# ast_function.py
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

from copy import copy

from pynestml.meta_model.ast_node import ASTNode


class ASTFunction(ASTNode):
    """
    This class is used to store a user-defined function.
    ASTFunction a function definition:
      function set_V_m(v mV):
        y3 = v - E_L
      end
    @attribute name Functionname.
    @attribute parameter A single parameter.
    @attribute returnType Complex return type, e.g. String
    @attribute primitiveType Primitive return type, e.g. int
    @attribute block Implementation of the function.
    Grammar:
    function: 'function' NAME '(' (parameter (',' parameter)*)? ')' (returnType=datatype)?
           BLOCK_OPEN
             block
           BLOCK_CLOSE;
    Attributes:
        name = None
        parameters = None
        return_type = None
        block = None
        # the corresponding type symbol
        type_symbol = None
    """

    def __init__(self, name, parameters, return_type, block, type_symbol=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param name: the name of the defined function.
        :type name: str
        :param parameters: (Optional) Set of parameters.
        :type parameters: List[ASTParameter]
        :param return_type: (Optional) Return type.
        :type return_type: ASTDataType
        :param block: a block of declarations.
        :type block: ASTBlock
        """
        super(ASTFunction, self).__init__(*args, **kwargs)
        self.block = block
        self.return_type = return_type
        self.parameters = parameters
        self.name = name
        self.type_symbol = type_symbol

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTFunction
        """
        block_dup = None
        if self.block:
            block_dup = self.block.clone()
        return_type_dup = None
        if self.return_type:
            return_type_dup = self.return_type.clone()
        parameters_dup = None
        if self.parameters:
            parameters_dup = [parameter.clone() for parameter in self.parameters]
        dup = ASTFunction(name=self.name,
                          parameters=parameters_dup,
                          return_type=return_type_dup,
                          block=block_dup,
                          type_symbol=self.type_symbol,
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
        Returns the name of the function.
        :return: the name of the function.
        :rtype: str
        """
        return self.name

    def has_parameters(self):
        """
        Returns whether parameters have been defined.
        :return: True if parameters defined, otherwise False.
        :rtype: bool
        """
        return (self.parameters is not None) and (len(self.parameters) > 0)

    def get_parameters(self):
        """
        Returns the list of parameters.
        :return: a parameters object containing the list.
        :rtype: list(ASTParameter)
        """
        return self.parameters

    def has_return_type(self):
        """
        Returns whether return a type has been defined.
        :return: True if return type defined, otherwise False.
        :rtype: bool
        """
        return self.return_type is not None

    def get_return_type(self):
        """
        Returns the return type of function.
        :return: the return type
        :rtype: ast_data_type
        """
        return self.return_type

    def get_block(self):
        """
        Returns the block containing the definitions.
        :return: the block of the definitions.
        :rtype: ast_block
        """
        return self.block

    def get_type_symbol(self):
        """
        Returns the type symbol of this rhs.
        :return: a single type symbol.
        :rtype: type_symbol
        """
        return copy(self.type_symbol)

    def set_type_symbol(self, type_symbol):
        """
        Updates the current type symbol to the handed over one.
        :param type_symbol: a single type symbol object.
        :type type_symbol: type_symbol
        """
        self.type_symbol = type_symbol

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for param in self.get_parameters():
            if param is ast:
                return self
            if param.get_parent(ast) is not None:
                return param.get_parent(ast)
        if self.has_return_type():
            if self.get_return_type() is ast:
                return self
            if self.get_return_type().get_parent(ast) is not None:
                return self.get_return_type().get_parent(ast)
        if self.get_block() is ast:
            return self
        if self.get_block().get_parent(ast) is not None:
            return self.get_block().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTFunction):
            return False
        if self.get_name() != other.get_name():
            return False
        if len(self.get_parameters()) != len(other.get_parameters()):
            return False
        my_parameters = self.get_parameters()
        your_parameters = other.get_parameters()
        for i in range(0, len(my_parameters)):
            if not my_parameters[i].equals(your_parameters[i]):
                return False
        if self.has_return_type() + other.has_return_type() == 1:
            return False
        if (self.has_return_type() and other.has_return_type()
                and not self.get_return_type().equals(other.get_return_type())):
            return False
        return self.get_block().equals(other.get_block())
