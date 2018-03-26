#
# ASTParameter.py
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
from pynestml.modelprocessor.ASTDatatype import ASTDatatype


class ASTParameter(ASTNode):
    """
    This class is used to store a single function parameter definition.
    ASTParameter represents singe:
      output: spike
    @attribute compartments Lists with compartments.
    Grammar:
        parameter : NAME datatype;
    Attributes:
        __name (str): The name of the parameter.
        __dataType (ASTDatatype): The data type of the parameter.
    """
    __name = None
    __dataType = None

    def __init__(self, name=None, data_type=None, source_position=None):
        """
        Standard constructor.
        :param name: the name of the parameter.
        :type name: str
        :param data_type: the type of the parameter.
        :type data_type: ASTDatatype
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourcePosition.
        """
        assert (name is not None and isinstance(name, str)), \
            '(PyNestML.AST.Parameter) No or wrong type of name provided (%s)!' % type(name)
        assert (data_type is not None and isinstance(data_type, ASTDatatype)), \
            '(PyNestML.AST.Parameter) No or wrong type of datatype provided (%s)!' % type(data_type)
        super(ASTParameter, self).__init__(source_position)
        self.__dataType = data_type
        self.__name = name

    def getName(self):
        """
        Returns the name of the parameter.
        :return: the name of the parameter.
        :rtype: str
        """
        return self.__name

    def getDataType(self):
        """
        Returns the data type of the parameter.
        :return: the data type of the parameter.
        :rtype: ASTDatatype
        """
        return self.__dataType

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.getDataType() is _ast:
            return self
        elif self.getDataType().getParent(_ast) is not None:
            return self.getDataType().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the parameter.
        :return: a string representation.
        :rtype: str
        """
        return self.getName() + ' ' + str(self.getDataType())

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTParameter):
            return False
        return self.getName() == _other.getName() and self.getDataType().equals(_other.getDataType())
