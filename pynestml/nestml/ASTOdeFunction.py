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


from pynestml.nestml.ASTElement import ASTElement
from pynestml.nestml.ASTDatatype import ASTDatatype
from pynestml.nestml.ASTExpression import ASTExpression
from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression


class ASTOdeFunction(ASTElement):
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

    def __init__(self, _isRecordable=False, _variableName=None, _dataType=None, _expression=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _isRecordable: (optional) is this function recordable or not.
        :type _isRecordable: bool
        :param _variableName: the name of the variable.
        :type _variableName: str
        :param _dataType: the datatype of the function.
        :type _dataType: ASTDataType
        :param _expression: the computation expression.
        :type _expression: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_variableName is not None and isinstance(_variableName, str)), \
            '(PyNestML.AST.OdeFunction) No or wrong type of variable name provided (%s)!' % type(_variableName)
        assert (_dataType is not None and isinstance(_dataType, ASTDatatype)), \
            '(PyNestML.AST.OdeFunction) No or wrong type of variable datatype provided (%s)!' % type(_dataType)
        assert (_expression is not None and (isinstance(_expression, ASTExpression) or
                                             isinstance(_expression, ASTSimpleExpression))), \
            '(PyNestML.AST.OdeFunction) No or wrong type of computation expression provided (%s)!' % type(_expression)
        assert (_isRecordable is None or isinstance(_isRecordable, bool)), \
            '(PyNestML.AST.OdeFunction) No or wrong type of is-recordable parameter specified (%s)!' % type(
                _isRecordable)
        super(ASTOdeFunction, self).__init__(_sourcePosition)
        self.__isRecordable = _isRecordable
        self.__variableName = _variableName
        self.__dataType = _dataType
        self.__expression = _expression

    @classmethod
    def makeASTOdeFunction(cls, _isRecordable=False, _variableName=None, _dataType=None, _expression=None,
                           _sourcePosition=None):
        """
        A factory method used to generate new ASTOdeFunction.
        :param _isRecordable: is this function recordable or not.
        :type _isRecordable: bool
        :param _variableName: the name of the variable.
        :type _variableName: str
        :param _dataType: the datatype of the function.
        :type _dataType: ASTDataType
        :param _expression: the computation expression.
        :type _expression: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return a new ASTOdeFunction object
        :rtype ASTOdeFunction
        """
        return cls(_isRecordable=_isRecordable, _variableName=_variableName, _dataType=_dataType,
                   _expression=_expression, _sourcePosition=_sourcePosition)

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

    def printAST(self):
        """
        Returns a string representation of the ode function.
        :return: a string representation
        :rtype: str
        """
        ret = ''
        if self.isRecordable():
            ret += 'recordable'
        ret += 'function ' + self.getVariableName() + ' ' + self.getDataType().printAST() + \
               ' = ' + self.getExpression().printAST()
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
