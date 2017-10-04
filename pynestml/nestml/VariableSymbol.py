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
from pynestml.nestml.Symbol import Symbol
from pynestml.nestml.ASTExpression import ASTExpression
from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression
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
        __typeSymbol          The concrete type of this variable.
        __odeDeclaration      Used to store the corresponding ode declaration. 
        __isConductanceBased  Indicates whether this buffer is used in a cond_sum expression.
        __initialValue        Indicates the initial value if such is declared.
    """
    __blockType = None
    __vectorParameter = None
    __declaringExpression = None
    __isPredefined = False
    __isFunction = False
    __isRecordable = False
    __typeSymbol = None
    __odeDeclaration = None
    __isConductanceBased = False
    __initialValue = None

    def __init__(self, _elementReference=None, _scope=None, _name=None, _blockType=None, _vectorParameter=None,
                 _declaringExpression=None, _isPredefined=False, _isFunction=False, _isRecordable=False,
                 _typeSymbol=None, _initialValue=None):
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
        :param _initialValue: the initial value if such an exists
        :type _initialValue: ASTExpression
        """
        assert (_blockType is not None and isinstance(_blockType, BlockType)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of block-type provided (%s)!' % type(_blockType)
        assert (_vectorParameter is None or isinstance(_vectorParameter, str)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of vector parameter provided (%s)!' % type(
                _vectorParameter)
        from pynestml.nestml.ASTExpression import ASTExpression
        assert (_declaringExpression is None or isinstance(_declaringExpression, ASTExpression)
                or isinstance(_declaringExpression, ASTSimpleExpression)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of declaring expression provided (%s)!' % type(
                _declaringExpression)
        assert (_isPredefined is not None and isinstance(_isPredefined, bool)), \
            '(PyNestML.SymbolTable.VariableSymbol) Is-predefined is not bool (%s)!' % type(_isPredefined)
        assert (_isFunction is not None and isinstance(_isFunction, bool)), \
            '(PyNestML.SymbolTable.VariableSymbol) Is-function is not bool (%s)!' % type(_isFunction)
        assert (_isRecordable is not None and isinstance(_isRecordable, bool)), \
            '(PyNestML.SymbolTable.VariableSymbol) Is-recordable is not bool (%s)!' % type(_isRecordable)
        from pynestml.nestml.TypeSymbol import TypeSymbol
        assert (_typeSymbol is not None and isinstance(_typeSymbol, TypeSymbol)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong of type-symbol provided (%s)!' % type(_typeSymbol)
        from pynestml.nestml.Symbol import SymbolKind
        assert (_initialValue is None or isinstance(_initialValue, ASTExpression) or
                isinstance(_initialValue, ASTSimpleExpression)), \
            '(PyNestML.SymbolTable.VariableSymbol) Wrong type of initial value provided (%s)!' % type(_initialValue)
        super(VariableSymbol, self).__init__(_elementReference=_elementReference, _scope=_scope,
                                             _name=_name, _symbolKind=SymbolKind.VARIABLE)
        self.__blockType = _blockType
        self.__vectorParameter = _vectorParameter
        self.__declaringExpression = _declaringExpression
        self.__isPredefined = _isPredefined
        self.__isFunction = _isFunction
        self.__isRecordable = _isRecordable
        self.__typeSymbol = _typeSymbol
        self.__initialValue = _initialValue
        return

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

    def setBlockType(self, _newType=None):
        """
        Updates the block type of this variable symbol.
        :param _newType: a new block type.
        :type _newType: BlockType
        """
        assert (_newType is not None and isinstance(_newType, BlockType)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of block-type provided (%s)!' % type(_newType)
        self.__blockType = _newType

    def getDeclaringExpression(self):
        """
        Returns the expression declaring the value of this symbol.
        :return: the expression declaring the value.
        :rtype: ASTExpression
        """
        return self.__declaringExpression

    def hasDeclaringExpression(self):
        """
        Indicates whether a declaring expression is present.
        :return: True if present, otherwise False.
        :rtype: bool
        """
        return self.__declaringExpression is not None and (isinstance(self.__declaringExpression, ASTSimpleExpression)
                                                           or isinstance(self.__declaringExpression, ASTExpression))

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
        from pynestml.nestml.ASTInputLine import ASTInputLine
        return isinstance(self.getReferencedObject(), ASTInputLine) and self.getReferencedObject().isSpike()

    def isCurrentBuffer(self):
        """
        Returns whether this symbol represents a current buffer.
        :return: True if current buffer, otherwise False.
        :rtype: bool
        """
        from pynestml.nestml.ASTInputLine import ASTInputLine
        return isinstance(self.getReferencedObject(), ASTInputLine) and self.getReferencedObject().isCurrent()

    def isExcitatory(self):
        """
        Returns whether this symbol represents a buffer of type excitatory.
        :return: True if is excitatory, otherwise False.
        :rtype: bool
        """
        from pynestml.nestml.ASTInputLine import ASTInputLine
        return isinstance(self.getReferencedObject(), ASTInputLine) and self.getReferencedObject().isExcitatory()

    def isInhibitory(self):
        """
        Returns whether this symbol represents a buffer of type inhibitory.
        :return: True if is inhibitory, otherwise False.
        :rtype: bool
        """
        from pynestml.nestml.ASTInputLine import ASTInputLine
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

    def isInitValues(self):
        """
        Returns whether this variable belongs to the definition of a initial value.
        :return: True if part of a initial value, otherwise False.
        :rtype: bool
        """
        return self.getBlockType() == BlockType.INITIAL_VALUES

    def printSymbol(self):
        if self.getReferencedObject() is not None:
            sourcePosition = self.getReferencedObject().getSourcePosition().printSourcePosition()
        else:
            sourcePosition = 'predefined'
        vectorValue = self.getVectorParameter() if self.hasVectorParameter() else 'none'
        typE = self.getTypeSymbol().printSymbol()
        recordable = 'recordable, ' if self.isRecordable() else ''
        func = 'function, ' if self.isFunction() else ''
        conductanceBased = 'conductance based, ' if self.isConductanceBased() else ''
        return 'VariableSymbol[' + self.getSymbolName() + ', type=' + typE + ', ' + str(self.getBlockType()) + ', ' \
               + recordable + func + conductanceBased + 'array parameter=' + vectorValue + ', @' + sourcePosition + ')'

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
        from pynestml.nestml.TypeSymbol import TypeSymbol
        assert (_typeSymbol is not None and isinstance(_typeSymbol, TypeSymbol)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of type symbol provided (%s)!' % type(_typeSymbol)
        self.__typeSymbol = _typeSymbol
        return

    def isOdeDefined(self):
        """
        Returns whether this element is defined by a ode.
        :return: True if ode defined, otherwise False.
        :rtype: bool
        """
        return self.__odeDeclaration is not None and (isinstance(self.__odeDeclaration, ASTExpression) or
                                                      isinstance(self.__odeDeclaration, ASTSimpleExpression))

    def getOdeDefinition(self):
        """
        Returns the ode defining the value of this variable symbol.
        :return: the expression defining the value.
        :rtype: ASTExpression
        """
        return self.__odeDeclaration

    def setOdeDefinition(self, _expression=None):
        """
        Updates the currently stored ode-definition to the handed-over one.
        :param _expression: a single expression object.
        :type _expression: ASTExpression
        """
        assert (_expression is not None and (isinstance(_expression, ASTExpression) or
                                             isinstance(_expression, ASTSimpleExpression))), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of expression provided (%s)!' % type(
                _expression)
        self.__odeDeclaration = _expression
        return

    def isConductanceBased(self):
        """
        Indicates whether this element is conductance based.
        :return: True if conductance based, otherwise False.
        :rtype: bool
        """
        return self.__isConductanceBased

    def setConductanceBased(self, _isConductanceBase=None):
        """
        Updates the information regarding the conductance property of this element.
        :param _isConductanceBase: the new status.
        :type _isConductanceBase: bool
        """
        assert (_isConductanceBase is not None and isinstance(_isConductanceBase, bool)), \
            '(PyNestML.SymbolTable.VariableSymbol) No or wrong type of conductance-based property provided (%s)!' \
            % type(_isConductanceBase)
        self.__isConductanceBased = _isConductanceBase
        return

    def hasInitialValue(self):
        """
        Returns whether this variable symbol has an initial value or not.
        :return: True if has initial value, otherwise False.
        :rtype: bool
        """
        return self.__initialValue is not None and (isinstance(self.__initialValue, ASTSimpleExpression) or
                                                    isinstance(self.__initialValue, ASTExpression))

    def getInitialValue(self):
        """
        Returns the initial value of this variable symbol if one exists.
        :return: the initial value expression.
        :rtype: ASTSimpleExpression or ASTExpression
        """
        return self.__initialValue

    def setInitialValue(self, _value=None):
        """
        Updates the initial value of this variable.
        :param _value: a new initial value.
        :type _value: ASTExpression or ASTSimpleExpression
        """
        assert (_value is not None and (isinstance(_value, ASTExpression) or isinstance(_value, ASTSimpleExpression))), \
            '(PyNestML.SymbolTable.VariableSymbol) Wrong type of initial value provided (%s)!' % type(_value)
        self.__initialValue = _value
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
               self.isConductanceBased() == _other.isConductanceBased() and \
               self.isRecordable() == _other.isRecordable()

    def hasComment(self):
        """
        Indicates whether this symbol stores a comment.
        :return: True if comment is stored, otherwise False.
        :rtype: bool
        """
        return True  # todo

    def printComment(self, _prefix=None):
        """
        Prints the stored comment.
        :return: the corresponding comment.
        :rtype: str
        """
        assert (_prefix is None or isinstance(_prefix,str)),\
            '(PyNestML.SymbolTable.VariableSymbol) Wrong type of prefix provided (%s)!' %type(_prefix)
        if _prefix is not None:
            return _prefix +'TODO comment in variable symbol'
        else:
            return 'TODO comment in variable symbol'

    def containsSumCall(self):
        """
        Indicates whether the declaring expression of this variable symbol has a x_sum or convolve in it.
        :return: True if contained, otherwise False.
        :rtype: bool
        """
        if not self.getDeclaringExpression():
            return False
        else:
            for func in self.getDeclaringExpression().getFunctions():
                if func.getName() == 'convolve' or func.getName() == 'cond_sum' or func.getName() == 'curr_sum':
                    return True
        return False


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
    INITIAL_VALUES = 10
    UNIT = 11