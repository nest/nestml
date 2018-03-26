#
# ASTOdeFunction.py
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
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression


class ASTOdeFunction(ASTNode):
    """
    Stores a single declaration of a ode function, e.g., 
        function v_init mV = V_m - 50mV.
    Grammar:    
        odeFunction : (recordable='recordable')? 'function' variableName=NAME datatype '=' expression;    
    """
    __isRecordable = False
    __variableName = None
    __dataType = None
    __expression = None

    def __init__(self, is_recordable=False, variable_name=None, data_type=None, expression=None, source_position=None):
        """
        Standard constructor.
        :param is_recordable: (optional) is this function recordable or not.
        :type is_recordable: bool
        :param variable_name: the name of the variable.
        :type variable_name: str
        :param data_type: the datatype of the function.
        :type data_type: ASTDataType
        :param expression: the computation expression.
        :type expression: ASTExpression
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourcePosition.
        """
        assert (variable_name is not None and isinstance(variable_name, str)), \
            '(PyNestML.AST.OdeFunction) No or wrong type of variable name provided (%s)!' % type(variable_name)
        assert (data_type is not None and isinstance(data_type, ASTDatatype)), \
            '(PyNestML.AST.OdeFunction) No or wrong type of variable datatype provided (%s)!' % type(data_type)
        assert (expression is not None and (isinstance(expression, ASTExpression) or
                                            isinstance(expression, ASTSimpleExpression))), \
            '(PyNestML.AST.OdeFunction) No or wrong type of computation expression provided (%s)!' % type(expression)
        assert (is_recordable is None or isinstance(is_recordable, bool)), \
            '(PyNestML.AST.OdeFunction) No or wrong type of is-recordable parameter specified (%s)!' % type(
                is_recordable)
        super(ASTOdeFunction, self).__init__(source_position)
        self.__isRecordable = is_recordable
        self.__variableName = variable_name
        self.__dataType = data_type
        self.__expression = expression

    def isRecordable(self):
        """
        Returns whether this ode function is recordable or not.
        :return: True if recordable, else False.
        :rtype: bool
        """
        return self.__isRecordable

    def getVariableName(self):
        """
        Returns the variable name.
        :return: the name of the variable.
        :rtype: str
        """
        return self.__variableName

    def getDataType(self):
        """
        Returns the data type as an object of ASTDatatype.
        :return: the type as an object of ASTDatatype.
        :rtype: ASTDatatype
        """
        return self.__dataType

    def getExpression(self):
        """
        Returns the expression as an object of ASTExpression.
        :return: the expression as an object of ASTExpression.
        :rtype: ASTExpression
        """
        return self.__expression

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
        if self.getExpression() is _ast:
            return self
        elif self.getExpression().getParent(_ast) is not None:
            return self.getExpression().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the ode function.
        :return: a string representation
        :rtype: str
        """
        ret = ''
        if self.isRecordable():
            ret += 'recordable'
        ret += 'function ' + str(self.getVariableName()) + ' ' + str(self.getDataType()) + \
               ' = ' + str(self.getExpression())
        return ret

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTOdeFunction):
            return False
        if self.isRecordable() != _other.isRecordable():
            return False
        if self.getVariableName() != _other.getVariableName():
            return False
        if not self.getDataType().equals(_other.getDataType()):
            return False
        return self.getExpression().equals(_other.getExpression())
