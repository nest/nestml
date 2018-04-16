#
# ASTFunction.py
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

from pynestml.meta_model.ASTNode import ASTNode


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
    """
    __name = None
    __parameters = None
    __returnType = None
    __block = None
    # the corresponding type symbol
    __typeSymbol = None

    def __init__(self, name, parameters, return_type, block, source_position):
        """
        Standard constructor.
        :param name: the name of the defined function.
        :type name: str
        :param parameters: (Optional) Set of parameters.
        :type parameters: list(ASTParameter)
        :param return_type: (Optional) Return type.
        :type return_type: ASTDataType
        :param block: a block of declarations.
        :type block: ASTBlock
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        super(ASTFunction, self).__init__(source_position)
        self.__block = block
        self.__returnType = return_type
        self.__parameters = parameters
        self.__name = name

    def get_name(self):
        """
        Returns the name of the function.
        :return: the name of the function.
        :rtype: str
        """
        return self.__name

    def has_parameters(self):
        """
        Returns whether parameters have been defined.
        :return: True if parameters defined, otherwise False.
        :rtype: bool
        """
        return (self.__parameters is not None) and (len(self.__parameters) > 0)

    def get_parameters(self):
        """
        Returns the list of parameters.
        :return: a parameters object containing the list.
        :rtype: list(ASTParameter)
        """
        return self.__parameters

    def has_return_type(self):
        """
        Returns whether return a type has been defined.
        :return: True if return type defined, otherwise False.
        :rtype: bool
        """
        return self.__returnType is not None

    def get_return_type(self):
        """
        Returns the return type of function.
        :return: the return type 
        :rtype: ASTDataType
        """
        return self.__returnType

    def get_block(self):
        """
        Returns the block containing the definitions.
        :return: the block of the definitions.
        :rtype: ASTBlock
        """
        return self.__block

    def get_type_symbol(self):
        """
        Returns the type symbol of this rhs.
        :return: a single type symbol.
        :rtype: TypeSymbol
        """
        return copy(self.__typeSymbol)

    def set_type_symbol(self, type_symbol):
        """
        Updates the current type symbol to the handed over one.
        :param type_symbol: a single type symbol object.
        :type type_symbol: TypeSymbol
        """
        self.__typeSymbol = type_symbol

    def get_parent(self, ast=None):
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
            elif param.get_parent(ast) is not None:
                return param.get_parent(ast)
        if self.has_return_type():
            if self.get_return_type() is ast:
                return self
            elif self.get_return_type().get_parent(ast) is not None:
                return self.get_return_type().get_parent(ast)
        if self.get_block() is ast:
            return self
        elif self.get_block().get_parent(ast) is not None:
            return self.get_block().get_parent(ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the function definition.
        :return: a string representation.
        :rtype: str
        """
        ret = 'function ' + self.get_name() + '('
        if self.has_parameters():
            for par in self.get_parameters():
                ret += str(par)
        ret += ')'
        if self.has_return_type():
            ret += str(self.get_return_type())
        ret += ':\n' + str(self.get_block()) + '\nend'
        return ret

    def equals(self, other=None):
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
        if (self.has_return_type() and other.has_return_type() and
                not self.get_return_type().equals(other.get_return_type())):
            return False
        return self.get_block().equals(other.get_block())
