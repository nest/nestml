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
    @attribute expr An optional initial expression, e.g. 'a real = 10+10'
    @attribute invariants List with optional invariants.
    Grammar:
        declaration :
            ('recordable')? ('function')?
            variable (',' variable)*
            datatype
            ('[' sizeParameter=NAME ']')?
            ( '=' expression)?
            ('[[' invariant=expression ']]')?;
    """
    __isRecordable = False
    __isFunction = False
    __variables = None
    __dataType = None
    __sizeParameter = None
    __expression = None
    __invariant = None

    def __init__(self, _isRecordable=False, _isFunction=False, _variables=list(), _dataType=None, _sizeParameter=None,
                 _expression=None, _invariant=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _isRecordable: is a recordable declaration.
        :type _isRecordable: bool
        :param _isFunction: is a function declaration.
        :type _isFunction: bool
        :param _variables: a list of variables.
        :type _variables: list(ASTVariable)
        :param _dataType: the data type.
        :type _dataType: ASTDataType
        :param _sizeParameter: an optional size parameter.
        :type _sizeParameter: str
        :param _expression: an optional right-hand side expression.
        :type _expression: ASTExpression
        :param _invariant: a optional invariant.
        :type _invariant: ASTExpression.
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_isRecordable is not None and isinstance(_isRecordable, bool)), \
            '(PyNestML.AST.Declaration) No or wrong type of is-recordable specification provided (%s)!' \
            % type(_isRecordable)
        assert (_isFunction is not None and isinstance(_isFunction, bool)), \
            '(PyNestML.AST.Declaration) No or wrong type of is-function specification provided (%s)!' \
            % type(_isFunction)
        assert (_variables is not None and isinstance(_variables, list)), \
            '(PyNestML.AST.Declaration) No or wrong type of variable-list provided (%s)!' \
            % type(_variables)
        assert (_dataType is not None and isinstance(_dataType, ASTDataType)), \
            '(PyNestML.AST.Declaration) No or wrong type of data-type provided (%s)!' \
            % type(_dataType)
        assert (_sizeParameter is None or isinstance(_sizeParameter, str)), \
            '(PyNestML.AST.Declaration) No or wrong type of index provided (%s)!' \
            % type(_sizeParameter)
        assert (_expression is None or (isinstance(_expression, ASTExpression)
                                        or isinstance(_expression, ASTSimpleExpression))), \
            '(PyNestML.AST.Declaration) No or wrong type of expression provided (%s)!' \
            % type(_expression)
        assert (_invariant is None or isinstance(_invariant, ASTExpression)
                or isinstance(_expression, ASTSimpleExpression)), \
            '(PyNestML.AST.Declaration) No or wrong type of expression provided (%s)!' \
            % type(_expression)
        super(ASTDeclaration, self).__init__(_sourcePosition)
        self.__isRecordable = _isRecordable
        self.__isFunction = _isFunction
        self.__variables = _variables
        self.__dataType = _dataType
        self.__sizeParameter = _sizeParameter
        self.__expression = _expression
        self.__invariant = _invariant
        return

    def isRecordable(self):
        """
        Returns whether the declaration is recordable or not.
        :return: True if recordable, else False.
        :rtype: bool
        """
        return isinstance(self.__isRecordable, bool) and self.__isRecordable

    def isFunction(self):
        """
        Returns whether the declaration is a function or not.
        :return: True if function, else False.
        :rtype: bool
        """
        return isinstance(self.__isFunction, bool) and self.__isFunction

    def getVariables(self):
        """
        Returns the set of left-hand side variables.
        :return: a list of variables.
        :rtype: list(ASTVariables)
        """
        return self.__variables

    def getDataType(self):
        """
        Returns the data type.
        :return: a data type object.
        :rtype: ASTDataType
        """
        return self.__dataType

    def hasSizeParameter(self):
        """
        Returns whether the declaration has a size parameter or not.
        :return: True if has size parameter, else False.
        :rtype: bool
        """
        return self.__sizeParameter is not None

    def getSizeParameter(self):
        """
        Returns the size parameter.
        :return: the size parameter.
        :rtype: str
        """
        return self.__sizeParameter

    def setSizeParameter(self, _parameter):
        """
        Updates the current size parameter to a new value.
        :param _parameter: the size parameter
        :type _parameter: str
        """
        assert (_parameter is not None and isinstance(_parameter, str)), \
            '(PyNestML.AST.Declaration) No or wrong type of size parameter provided (%s)!' % type(_parameter)
        self.__sizeParameter = _parameter
        return

    def hasExpression(self):
        """
        Returns whether the declaration has a right-hand side expression or not.
        :return: True if right-hand side expression declared, else False.
        :rtype: bool
        """
        return self.__expression is not None

    def getExpression(self):
        """
        Returns the right-hand side expression.
        :return: the right-hand side expression.
        :rtype: ASTExpression
        """
        return self.__expression

    def hasInvariant(self):
        """
        Returns whether the declaration has a invariant or not.
        :return: True if has invariant, otherwise False.
        :rtype: bool
        """
        return self.__invariant is not None

    def getInvariant(self):
        """
        Returns the invariant.
        :return: the invariant
        :rtype: ASTExpression
        """
        return self.__invariant

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for var in self.getVariables():
            if var is _ast:
                return self
            elif var.getParent(_ast) is not None:
                return var.getParent(_ast)
        if self.getDataType() is _ast:
            return self
        elif self.getDataType().getParent(_ast) is not None:
            return self.getDataType().getParent(_ast)
        if self.hasExpression():
            if self.getExpression() is _ast:
                return self
            elif self.getExpression().getParent(_ast) is not None:
                return self.getExpression().getParent(_ast)
        if self.hasInvariant():
            if self.getInvariant() is _ast:
                return self
            elif self.getInvariant().getParent(_ast) is not None:
                return self.getInvariant().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the declaration.
        :return: a string representation.
        :rtype: str
        """
        ret = ''
        if self.isRecordable():
            ret += 'recordable '
        if self.isFunction():
            ret += 'function '
        for var in self.getVariables():
            ret += str(var)
            if self.getVariables().index(var) < len(self.getVariables()) - 1:
                ret += ','
        ret += ' ' + str(self.getDataType()) + ' '
        if self.hasSizeParameter():
            ret += '[' + self.getSizeParameter() + ']'
        if self.hasExpression():
            ret += ' = ' + str(self.getExpression()) + ' '
        if self.hasInvariant():
            ret += ' [[' + str(self.getInvariant()) + ']]'
        return ret

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTDeclaration):
            return False
        if not (self.isFunction() == _other.isFunction() and self.isRecordable() == _other.isRecordable()):
            return False
        if self.getSizeParameter() != _other.getSizeParameter():
            return False
        if len(self.getVariables()) != len(_other.getVariables()):
            return False
        myVars = self.getVariables()
        yourVars = _other.getVariables()
        for i in range(0, len(myVars)):
            # caution, here the order is also checked
            if not myVars[i].equals(yourVars[i]):
                return False
        if self.hasInvariant() + _other.hasInvariant() == 1:
            return False
        if self.hasInvariant() and _other.hasInvariant() and not self.getInvariant().equals(_other.getInvariant()):
            return False
        return self.getDataType().equals(_other.getDataType()) and self.getExpression().equals(_other.getExpression())
