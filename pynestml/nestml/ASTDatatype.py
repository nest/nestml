#
# ASTDatatype.py
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

from pynestml.nestml.ASTUnitType import ASTUnitType
from pynestml.nestml.ASTElement import ASTElement
from pynestml.utils.Logger import LOGGING_LEVEL, Logger


class ASTDatatype(ASTElement):
    """
    A datatype class as used to store a datatype of an element.
    ASTDatatype. Represents predefined datatypes and gives a possibility to use an unit
    datatype.
    @attribute boolean getters for integer, real, ...
    @attribute unitType a SI datatype
    datatype : 'integer'
               | 'real'
               | 'string'
               | 'boolean'
               | 'void'
               | unitType;
    """
    __isInteger = False
    __isReal = False
    __isString = False
    __isBoolean = False
    __isVoid = False
    __isUnitType = None  # a unit type is not a boolean, but a concrete object
    __typeSymbol = None  # the corresponding type symbol

    def __init__(self, _isInteger=False, _isReal=False, _isString=False, _isBoolean=False, _isVoid=False,
                 _isUnitType=None, _sourcePosition=None):
        """
        :param _isInteger: is an integer data type 
        :type _isInteger: boolean
        :param _isReal: is a real datatype 
        :type _isReal: boolean
        :param _isString: is a string data type
        :type _isString: boolean
        :param _isBoolean: is a boolean
        :type _isBoolean: boolean
        :param _isVoid: is a void data type
        :type _isVoid: boolean
        :param _isUnitType: an object of type ASTUnitType
        :type _isUnitType: ASTUnitType
        :param _sourcePosition: The source position of the assignment
        :type _sourcePosition: ASTSourcePosition
        """
        assert (_isInteger is not None and isinstance(_isInteger, bool)), \
            '(PyNestML.AST.Datatype) Wrong type of is-integer parameter provided (%s)' % type(_isInteger)
        assert (_isReal is not None and isinstance(_isReal, bool)), \
            '(PyNestML.AST.Datatype) Wrong type of is-real parameter provided (%s)' % type(_isReal)
        assert (_isString is not None and isinstance(_isString, bool)), \
            '(PyNestML.AST.Datatype) Wrong type of is-string parameter provided (%s)' % type(_isString)
        assert (_isBoolean is not None and isinstance(_isBoolean, bool)), \
            '(PyNestML.AST.Datatype) Wrong type of is-boolean parameter provided (%s)' % type(_isBoolean)
        assert (_isVoid is not None and isinstance(_isVoid, bool)), \
            '(PyNestML.AST.Datatype) Wrong type of is-void parameter provided (%s)' % type(_isVoid)
        assert (_isUnitType is None or isinstance(_isUnitType, ASTUnitType)), \
            '(PyNestML.AST.Datatype) Wrong type of unit-type parameter provided (%s)' % type(_isUnitType)
        super(ASTDatatype, self).__init__(_sourcePosition)
        self.__isUnitType = _isUnitType
        self.__isVoid = _isVoid
        self.__isBoolean = _isBoolean
        self.__isString = _isString
        self.__isReal = _isReal
        self.__isInteger = _isInteger

    @classmethod
    def makeASTDatatype(cls, _isInteger=False, _isReal=False, _isString=False, _isBoolean=False,
                        _isVoid=False, _isUnitType=None, _sourcePosition=None):
        """
        A factory method for creation of objects of this class.
        :param _isInteger: is an integer data type 
        :type _isInteger: boolean
        :param _isReal: is a real datatype 
        :type _isReal: boolean
        :param _isString: is a string data type
        :type _isString: boolean
        :param _isBoolean: is a boolean
        :type _isBoolean: boolean
        :param _isVoid: is a void data type
        :type _isVoid: boolean
        :param _isUnitType: an object of type ASTUnitType
        :type _isUnitType: ASTUnitType
        :param _sourcePosition: The source position of the assignment
        :type _sourcePosition: ASTSourcePosition
        :return a new ASTDatatype object
        :rtype ASTDatatype
        """
        return cls(_isInteger, _isReal, _isString, _isBoolean, _isVoid, _isUnitType, _sourcePosition)

    def isInteger(self):
        """
        Returns whether this is a integer type or not.
        :return: True if integer typed, otherwise False.
        :rtype: bool
        """
        return self.__isInteger

    def isReal(self):
        """
        Returns whether this is a real type or not.
        :return: True if real typed, otherwise False.
        :rtype: bool
        :return: 
        :rtype: 
        """
        return self.__isReal

    def isString(self):
        """
        Returns whether this is a string type or not.
        :return: True if string typed, otherwise False.
        :rtype: bool
        """
        return self.__isString

    def isBoolean(self):
        """
        Returns whether this is a boolean type or not.
        :return: True if boolean typed, otherwise False.
        :rtype: bool
        """
        return self.__isBoolean

    def isVoid(self):
        """
        Returns whether this is a void type or not.
        :return: True if void typed, otherwise False.
        :rtype: bool
        """
        return self.__isVoid

    def isUnitType(self):
        """
        Returns whether this is a unit type or not.
        :return: True if unit type typed, otherwise False.
        :rtype: bool
        """
        return self.__isUnitType is not None

    def getUnitType(self):
        """
        Returns the unit type.
        :return: the unit type object.
        :rtype: ASTUnitType
        """
        return self.__isUnitType

    def getTypeSymbol(self):
        """
        Returns the corresponding type symbol.
        :return: a single type symbol element.
        :rtype: TypeSymbol
        """
        return self.__typeSymbol

    def setTypeSymbol(self, _typeSymbol=None):
        """
        Updates the current type symbol to the handed over one.
        :param _typeSymbol: a new type symbol element.
        :type _typeSymbol: TypeSymbol.
        """
        from pynestml.nestml.TypeSymbol import TypeSymbol
        assert (_typeSymbol is not None and isinstance(_typeSymbol, TypeSymbol)), \
            '(PyNestML.AST.DataType) No or wrong type of type symbol provided (%s)!' % (type(_typeSymbol))
        self.__typeSymbol = _typeSymbol
        return

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.isUnitType():
            if self.getUnitType() is _ast:
                return self
            elif self.getUnitType().getParent(_ast) is not None:
                return self.getUnitType().getParent(_ast)
        return None

    def printAST(self):
        """
        Returns a string representation of the data type.
        :return: a string representation
        :rtype: str
        """
        if self.isVoid():
            return 'void'
        elif self.isString():
            return 'string'
        elif self.isBoolean():
            return 'boolean'
        elif self.isInteger():
            return 'integer'
        elif self.isReal():
            return 'real'
        elif self.isUnitType():
            return self.getUnitType().printAST()
        else:
            Logger.logMessage('Type of datatype not specified!', LOGGING_LEVEL.WARNING)
