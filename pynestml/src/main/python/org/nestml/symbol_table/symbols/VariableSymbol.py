#
# VariableSymbol.py
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
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import Symbol
from enum import Enum


class VariableSymbol(Symbol):
    """
    This class is used to store a single variable symbol containing all required information.
    
    Attributes:
        __blockType           The type of block in which this symbol has been declared. Type: BlockType
        __vectorParameter     The parameter indicating the position in an array. Type: str
        __declaringExpression The expression defining the value of this symbol. Type: ASTExpression  
        __isPredefined        Indicates whether this symbol is predefined, e.g., t or e. Type: bool
        __isFunction          Indicates whether this symbol belongs to a function. Type: bool
        __isRecordable        Indicates whether this symbol belongs to a recordable element. Type: bool
        __typeSymbol          The concrete type of this varible.
    """
    __blockType = None
    __vectorParameter = None
    __declaringExpression = None
    __isPredefined = False
    __isFunction = False
    __isRecordable = False
    __typeSymbol = None

    def __init__(self, _elementReference=None, _scope=None, _name=None, _blockType=None, _vectorParameter=None,
                 _declaringExpression=None, _isPredefined=False, _isFunction=False, _isRecordable=False,
                 _typeSymbol=None):
        """
        Standard constructor.
        :param _elementReference: a reference to the first element where this type has been used/defined
        :type _elementReference: Object (or None, if predefined) 
        :param _scope: the scope in which this type is defined in 
        :type _scope: Scope
        :param _name: the name of the type symbol
        :type _name: str
        :param _blockType: the type of block in which this element has been defined in
        :type _blockType: BlockType
        :param _vectorParameter: the parameter indicating a position in an array
        :type _vectorParameter: str
        :param _declaringExpression: a expression declaring the value of this symbol. 
        :type _declaringExpression: ASTExpression
        :param _isPredefined: indicates whether this element represents a predefined variable, e.g., e or t
        :type _isPredefined: bool
        :param _isFunction: indicates whether this element represents a function (aka. alias)
        :type _isFunction: bool
        :param _isRecordable: indicates whether this elements is recordable or not.
        :type _isRecordable: bool
        :param _typeSymbol: a type symbol representing the concrete type of this variable
        :type _typeSymbol: TypeSymbol
        """
        assert (_blockType is not None and isinstance(_blockType, BlockType)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of block-type provided (%s)!' % type(_blockType)
        assert (_vectorParameter is None or isinstance(_vectorParameter, str)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of vector parameter provided (%s)!' % type(
                _vectorParameter)
        from pynestml.src.main.python.org.nestml.ast.ASTExpression import ASTExpression
        assert (_declaringExpression is None or isinstance(_declaringExpression, ASTExpression)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of declaring expression provided (%s)!' % type(
                _declaringExpression)
        assert (_isPredefined is not None and isinstance(_isPredefined, bool)), \
            '(PyNestML.SymbolTable.VariableSymbol) Is-predefined is not bool (%s)!' % type(_isPredefined)
        assert (_isFunction is not None and isinstance(_isFunction, bool)), \
            '(PyNestML.SymbolTable.VariableSymbol) Is-function is not bool (%s)!' % type(_isFunction)
        assert (_isRecordable is not None and isinstance(_isRecordable, bool)), \
            '(PyNestML.SymbolTable.VariableSymbol) Is-recordable is not bool (%s)!' % type(_isRecordable)
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        assert (_typeSymbol is not None and isinstance(_typeSymbol, TypeSymbol)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong of type-symbol provided (%s)!' % type(_typeSymbol)
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolType
        super(VariableSymbol, self).__init__(_elementReference=_elementReference, _scope=_scope,
                                             _name=_name, _symbolType=SymbolType.VARIABLE)
        self.__blockType = _blockType
        self.__vectorParameter = _vectorParameter
        self.__declaringExpression = _declaringExpression
        self.__isPredefined = _isPredefined
        self.__isFunction = _isFunction
        self.__isRecordable = _isRecordable
        self.__typeSymbol = _typeSymbol

    def hasVectorParameter(self):
        """
        Returns whether this variable symbol has a vector parameter.
        :return: True if vector parameter available, otherwise False. 
        :rtype: bool
        """
        return self.__vectorParameter is not None and type(self.__vectorParameter) == str

    def getVectorParameter(self):
        """
        Returns the vector parameter of this symbol if any available, e.g., spike[12]
        :return: the vector parameter of this variable symbol.
        :rtype: str
        """
        return self.__vectorParameter

    def getBlockType(self):
        """
        Returns the type of the block in which this variable-symbol has been declared in.
        :return: the type of block.
        :rtype: BlockType
        """
        return self.__blockType

    def getDeclaringExpression(self):
        """
        Returns the expression declaring the value of this symbol.
        :return: the expression declaring the value.
        :rtype: ASTExpression
        """
        return self.__declaringExpression

    def isPredefined(self):
        """
        Returns whether this symbol is a predefined one or not.
        :return: True if predefined, False otherwise.
        :rtype: bool
        """
        return self.__isPredefined

    def isFunction(self):
        """
        Returns whether this symbol represents a function aka. alias.
        :return: True if function, False otherwise.
        :rtype: bool
        """
        return self.__isFunction

    def isRecordable(self):
        """
        Returns whether this symbol represents a recordable element.
        :return: True if recordable, False otherwise.
        :rtype: bool
        """
        return self.__isRecordable

    def isSpikeBuffer(self):
        """
        Returns whether this symbol represents a spike buffer.
        :return: True if spike buffer, otherwise False.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTInputLine import ASTInputLine
        return isinstance(self.getReferencedObject(), ASTInputLine) and self.getReferencedObject().isSpike()

    def isCurrentBuffer(self):
        """
        Returns whether this symbol represents a current buffer.
        :return: True if current buffer, otherwise False.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTInputLine import ASTInputLine
        return isinstance(self.getReferencedObject(), ASTInputLine) and self.getReferencedObject().isCurrent()

    def isExcitatory(self):
        """
        Returns whether this symbol represents a buffer of type excitatory.
        :return: True if is excitatory, otherwise False.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTInputLine import ASTInputLine
        return isinstance(self.getReferencedObject(), ASTInputLine) and self.getReferencedObject().isExcitatory()

    def isInhibitory(self):
        """
        Returns whether this symbol represents a buffer of type inhibitory.
        :return: True if is inhibitory, otherwise False.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTInputLine import ASTInputLine
        return isinstance(self.getReferencedObject(), ASTInputLine) and self.getReferencedObject().isInhibitory()

    def isState(self):
        """
        Returns whether this variable symbol has been declared in a state block.
        :return: True if declared in a state block, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.STATE

    def isParameters(self):
        """
        Returns whether this variable symbol has been declared in a parameters block.
        :return: True if declared in a parameters block, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.PARAMETERS

    def isInternals(self):
        """
        Returns whether this variable symbol has been declared in a internals block.
        :return: True if declared in a internals block, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.INTERNALS

    def isEquation(self):
        """
        Returns whether this variable symbol has been declared in a equation block.
        :return: True if declared in a equation block, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.EQUATION

    def isLocal(self):
        """
        Returns whether this variable symbol has been declared in a local (e.g., update) block.
        :return: True if declared in a local block, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.LOCAL

    def isInputBufferCurrent(self):
        """
        Returns whether this variable symbol has been declared as a input-buffer current element.
        :return: True if input-buffer current, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.INPUT_BUFFER_CURRENT

    def isInputBufferSpike(self):
        """
        Returns whether this variable symbol has been declared as a input-buffer spike element.
        :return: True if input-buffer spike, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.INPUT_BUFFER_SPIKE

    def isOutput(self):
        """
        Returns whether this variable symbol has been declared as a output-buffer element.
        :return: True if output element, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.OUTPUT

    def isShape(self):
        """
        Returns whether this variable belongs to the definition of a shape.
        :return: True if part of a shape definition, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.SHAPE

    def printSymbol(self):
        if self.getReferencedObject() is not None:
            sourcePosition = self.getReferencedObject().getSourcePosition().printSourcePosition()
        else:
            sourcePosition = 'predefined'
        vectorValue = self.getVectorParameter() if self.hasVectorParameter() else ' none'
        type = self.getTypeSymbol().printSymbol()

        return 'VariableSymbol[' + self.getSymbolName() + ', type=' + type + ', ' + str(self.getBlockType()) + ', ' \
               + 'array parameter=' + vectorValue + ', @' + sourcePosition + ')'

    def getTypeSymbol(self):
        """
        Returns the corresponding type symbol.
        :return: the current type symbol.
        :rtype: TypeSymbol
        """
        return self.__typeSymbol

    def setTypeSymbol(self, _typeSymbol=None):
        """
        Updates the current type symbol to a new one.
        :param _typeSymbol: a new type symbol.
        :type _typeSymbol: TypeSymbol
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        assert (_typeSymbol is not None and isinstance(_typeSymbol, TypeSymbol)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of type symbol provided (%s)!' % type(_typeSymbol)
        self.__typeSymbol = _typeSymbol
        return

    def equals(self, _other=None):
        """
        Compares the handed over object to this value-wise.
        :param _other: the element to which this is compared to.
        :type _other: Symbol or subclass
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        return type(self) != type(_other) and \
               self.getReferencedObject() == _other.getReferencedObject() and \
               self.getSymbolName() == _other.getSymbolName() and \
               self.getCorrespondingScope() == _other.getCorrespondingScope() and \
               self.getBlockType() == _other.getBlockType() and \
               self.getVectorParameter() == _other.getVectorParameter() and \
               self.getDeclaringExpression() == _other.getDeclaringExpression() and \
               self.isPredefined() == _other.isPredefined() and \
               self.isFunction() == _other.isFunction() and \
               self.isRecordable() == _other.isRecordable()


class BlockType(Enum):
    STATE = 1
    PARAMETERS = 2
    INTERNALS = 3
    EQUATION = 4
    LOCAL = 5
    INPUT_BUFFER_CURRENT = 6
    INPUT_BUFFER_SPIKE = 7
    OUTPUT = 8
    SHAPE = 9
