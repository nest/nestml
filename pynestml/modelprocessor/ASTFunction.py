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

from pynestml.modelprocessor.ASTNode import ASTNode
from pynestml.modelprocessor.ASTBlock import ASTBlock
from pynestml.modelprocessor.ASTDatatype import ASTDatatype


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

    def __init__(self, _name=None, _parameters=None, _returnType=None, _block=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _name: the name of the defined function.
        :type _name: str 
        :param _parameters: (Optional) Set of parameters.  
        :type _parameters: list(ASTParameter)
        :param _returnType: (Optional) Return type. 
        :type _returnType: ASTDataType
        :param _block: a block of declarations.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.AST.Function) No name or wrong type provided (%s)!' % type(_name)
        assert (_block is not None and isinstance(_block, ASTBlock)), \
            '(PyNestML.AST.Function) No block or wrong type provided (%s)!' % type(_block)
        assert (_parameters is None or isinstance(_parameters, list)), \
            '(PyNestML.AST.Function) Wrong type of parameters provided (%s)!' % type(_parameters)
        assert (_returnType is None or isinstance(_returnType, ASTDatatype)), \
            '(PyNestML.AST.Function) Wrong type of return provided (%s)!' % type(_returnType)
        super(ASTFunction, self).__init__(_sourcePosition)
        self.__block = _block
        self.__returnType = _returnType
        self.__parameters = _parameters
        self.__name = _name
        return

    @classmethod
    def makeASTFunction(cls, _name=None, _parameters=None, _returnType=None, _block=None, _sourcePosition=None):
        """
        Factory method of the ASTFunction class.
        :param _name: the name of the defined function.
        :type _name: str 
        :param _parameters: (Optional) Set of parameters.  
        :type _parameters: list(ASTParameter)
        :param _returnType: (Optional) Return type. 
        :type _returnType: ASTDataType
        :param _block: a block of declarations.
        :type _block: ASTBlock
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTFunction object.
        :rtype: ASTFunction
        """
        return cls(_name, _parameters, _returnType, _block, _sourcePosition)

    def getName(self):
        """
        Returns the name of the function.
        :return: the name of the function.
        :rtype: str
        """
        return self.__name

    def hasParameters(self):
        """
        Returns whether parameters have been defined.
        :return: True if parameters defined, otherwise False.
        :rtype: bool
        """
        return (self.__parameters is not None) and (len(self.__parameters) > 0)

    def getParameters(self):
        """
        Returns the list of parameters.
        :return: a parameters object containing the list.
        :rtype: list(ASTParameter)
        """
        return self.__parameters

    def hasReturnType(self):
        """
        Returns whether return a type has been defined.
        :return: True if return type defined, otherwise False.
        :rtype: bool
        """
        return self.__returnType is not None

    def getReturnType(self):
        """
        Returns the return type of function.
        :return: the return type 
        :rtype: ASTDataType
        """
        return self.__returnType

    def getBlock(self):
        """
        Returns the block containing the definitions.
        :return: the block of the definitions.
        :rtype: ASTBlock
        """
        return self.__block

    def getTypeSymbol(self):
        """
        Returns the type symbol of this expression.
        :return: a single type symbol.
        :rtype: TypeSymbol
        """
        return self.__typeSymbol

    def setTypeSymbol(self, _typeSymbol=None):
        """
        Updates the current type symbol to the handed over one.
        :param _typeSymbol: a single type symbol object.
        :type _typeSymbol: TypeSymbol
        """
        from pynestml.modelprocessor.TypeSymbol import TypeSymbol
        assert (_typeSymbol is not None and isinstance(_typeSymbol, TypeSymbol)), \
            '(PyNestML.AST.Expression) No or wrong type of type symbol provided (%s)!' % type(_typeSymbol)
        self.__typeSymbol = _typeSymbol

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        for param in self.getParameters():
            if param is _ast:
                return self
            elif param.getParent(_ast) is not None:
                return param.getParent(_ast)
        if self.hasReturnType():
            if self.getReturnType() is _ast:
                return self
            elif self.getReturnType().getParent(_ast) is not None:
                return self.getReturnType().getParent(_ast)
        if self.getBlock() is _ast:
            return self
        elif self.getBlock().getParent(_ast) is not None:
            return self.getBlock().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the function definition.
        :return: a string representation.
        :rtype: str
        """
        ret = 'function ' + self.getName() + '('
        if self.hasParameters():
            for par in self.getParameters():
                ret += str(par)
        ret += ')'
        if self.hasReturnType():
            ret += str(self.getReturnType())
        ret += ':\n' + str(self.getBlock()) + '\nend'
        return ret

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTFunction):
            return False
        if self.getName() != _other.getName():
            return False
        if len(self.getParameters()) != len(_other.getParameters()):
            return False
        myParameters = self.getParameters()
        yourParameters = _other.getParameters()
        for i in range(0, len(myParameters)):
            if not myParameters[i].equals(yourParameters[i]):
                return False
        if self.hasReturnType() + _other.hasReturnType() == 1:
            return False
        if self.hasReturnType() and _other.hasReturnType() and not self.getReturnType().equals(_other.getReturnType()):
            return False
        return self.getBlock().equals(_other.getBlock())
