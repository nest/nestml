#
# Messages.py.py
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
from enum import Enum


class Messages(object):
    """
    This class contains a collection of error messages which enables a centralized maintaining and modifications of
    those.
    """

    @classmethod
    def getStartProcessingFile(cls, _filePath=None):
        """
        Returns a message indicating that processing of a file has started
        :param _filePath: the path to the file
        :type _filePath: str
        :return: message code tuple
        :rtype: (MessageCode,str)
        """
        message = 'Start processing \'' + _filePath + '\''
        return MessageCode.START_PROCESSING_FILE, message

    @classmethod
    def getNewTypeRegistered(cls, _typeName=None):
        """
        Returns a message which indicates that a new type has been registred.
        :param _typeName: a type name
        :type _typeName: str
        :return: message code tuple
        :rtype: (MessageCode,str)
        """
        message = 'New type registered \'%s\'!' % (_typeName)
        return MessageCode.TYPE_REGISTERED, message

    @classmethod
    def getStartBuildingSymbolTable(cls):
        """
        Returns a message that the building for a neuron has been started.
        :return: a message
        :rtype: (MessageCode,str)
        """
        return MessageCode.START_SYMBOL_TABLE_BUILDING, 'Start building symbol table!'

    @classmethod
    def getFunctionCallImplicitCast(cls, _argNr=None, _functionCall=None, _expectedType=None, _gotType=None,
                                    _castable=False):
        """
        Returns a message indicating that an implicit cast has been performed.
        :param _argNr: the number of the argument which is cast
        :type _argNr: int
        :param _functionCall: a single function call
        :type _functionCall: ASTFunctionCall
        :param _expectedType: the expected type
        :type _expectedType: TypeSymbol
        :param _gotType: the got-type
        :type _gotType: TypeSymbol
        :param _castable: is the type castable
        :type _castable: bool
        :return: a message
        :rtype: str
        """
        if not _castable:
            message = str(_argNr) + '. argument of function-call \'%s\' at is wrongly typed! Expected \'%s\',' \
                                    ' found \'%s\'.' % (_functionCall.getName(), _gotType.getValue().printSymbol(),
                                                        _expectedType.printSymbol())
        else:
            message = str(_argNr) + '. argument of function-call \'%s\' is wrongly typed! ' \
                                    'Implicit cast from \'%s\' to \'%s\'.' % (_functionCall.getName(),
                                                                              _gotType.getValue().printSymbol(),
                                                                              _expectedType.printSymbol())
        return MessageCode.FUNCTION_CALL_TYPE_ERROR, message

    @classmethod
    def getTypeCouldNotBeDerived(cls, _rhs=None):
        """
        Returns a message indicating that the type of the rhs expression could not be derived.
        :param _rhs: an expression
        :type _rhs: ASTExpression or ASTSimpleExpression
        :return: a message
        :rtype: str

        """
        message = 'Type of \'%s\' could not be derived!' % _rhs.printAST()
        return MessageCode.TYPE_NOT_DERIVABLE, message

    @classmethod
    def getImplicitCastRhsToLhs(cls, _rhsExpression=None, _lhsExpression=None,
                                _rhsType=None, _lhsType=None):
        """
        Returns a message indicating that the type of the lhs does not correspond to the one of the rhs, but the rhs
        can be cast down to lhs type.
        :param _rhsExpression: the rhs expression
        :type _rhsExpression: ASTExpression or ASTSimpleExpression
        :param _lhsExpression: the lhs expression
        :type _lhsExpression: ASTExpression or ASTSimpleExpression
        :param _rhsType: the type of the rhs
        :type _rhsType: TypeSymbol
        :param _lhsType: the type of the lhs
        :type _lhsType: TypeSymbol
        :return: a message
        :rtype:str
        """
        message = 'Type of lhs \'%s\' does not correspond to expression type of \'%s\'! LHS=\'%s\', RHS=\'%s.\'' \
                  % (
                      _lhsExpression.printAST(), _rhsExpression.printAST(), _lhsType.printSymbol(),
                      _rhsType.printSymbol())
        return MessageCode.IMPLICIT_CAST, message

    @classmethod
    def getDifferentTypeRhsLhs(cls, _rhsExpression=None, _lhsExpression=None,
                               _rhsType=None, _lhsType=None):
        """
        Returns a message indicating that the type of the lhs does not correspond to the one of the rhs and can not
        be cast down to a common type.
        :param _rhsExpression: the rhs expression
        :type _rhsExpression: ASTExpression or ASTSimpleExpression
        :param _lhsExpression: the lhs expression
        :type _lhsExpression: ASTExpression or ASTSimpleExpression
        :param _rhsType: the type of the rhs
        :type _rhsType: TypeSymbol
        :param _lhsType: the type of the lhs
        :type _lhsType: TypeSymbol
        :return: a message
        :rtype:str
        """
        message = 'Type of lhs \'%s\' does not correspond to rhs \'%s\'! LHS: \'%s\', RHS: \'%s\'.' % (
            _lhsExpression.printAST(),
            _rhsExpression.printAST(),
            _lhsType.printSymbol(),
            _rhsType.printSymbol())
        return MessageCode.CAST_NOT_POSSIBLE, message

    @classmethod
    def getTypeDifferentFromExpected(cls, _expectedType=None, _gotType=None):
        """
        Returns a message indicating that the received type is different from the expected one.
        :param _expectedType: the expected type
        :type _expectedType: TypeSymbol
        :param _gotType: the actual type
        :type _gotType: TypeSymbol
        :return: a message
        :rtype: str
        """
        message = 'Actual type different from expected. Expected: \'%s\', got: \'%s\'!' % (
            _expectedType.printSymbol(), _gotType.printSymbol())
        return MessageCode.TYPE_DIFFERENT_FROM_EXPECTED, message

    @classmethod
    def getBufferSetToConductanceBased(cls, _buffer=None):
        """
        Returns a message indicating that a buffer has been set to conductance based.
        :param _buffer: the name of the buffer
        :type _buffer: str
        :return: a message
        :rtype: str
        """
        assert (_buffer is not None and isinstance(_buffer, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _buffer
        message = 'Buffer \'%s\' set to conductance based!' % _buffer
        return MessageCode.BUFFER_SET_TO_CONDUCTANCE_BASED, message

    @classmethod
    def getOdeUpdated(cls, _variableName=None):
        """
        Returns a message indicating that the ode of a variable has been updated.
        :param _variableName: the name of the variable
        :type _variableName: str
        :return: a message
        :rtype: str
        """
        assert (_variableName is not None and isinstance(_variableName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _variableName
        message = 'Ode of \'%s\' updated!' % _variableName
        return MessageCode.ODE_UPDATED, message

    @classmethod
    def getNoVariableFound(cls, _variableName=None):
        """
        Returns a message indicating that a variable has not been found.
        :param _variableName: the name of the variable
        :type _variableName: str
        :return: a message
        :rtype: str
        """
        assert (_variableName is not None and isinstance(_variableName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _variableName
        message = 'No variable \'%s\' found!' % _variableName
        return MessageCode.NO_VARIABLE_FOUND, message

    @classmethod
    def getBufferTypeNotDefined(cls, _bufferName=None):
        """
        Returns a message indicating that a buffer type has not been defined, thus nS is assumed.
        :param _bufferName: a buffer name
        :type _bufferName: str
        :return: a message
        :rtype: str
        """
        assert (_bufferName is not None and isinstance(_bufferName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _bufferName
        from pynestml.nestml.PredefinedTypes import PredefinedTypes
        message = 'No buffer type declared of \'%s\', \'%s\' is assumed!' \
                  % (_bufferName, PredefinedTypes.getTypeIfExists('nS').printSymbol())
        return MessageCode.SPIKE_BUFFER_TYPE_NOT_DEFINED, message

    @classmethod
    def getNeuronContainsErrors(cls, _neuronName=None):
        """
        Returns a message indicating that a neuron contains errors thus no code is generated.
        :param _neuronName: the name of the neuron
        :type _neuronName: str
        :return: a message
        :rtype: str
        """
        assert (_neuronName is not None and isinstance(_neuronName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _neuronName
        message = 'Neuron \'' + _neuronName + '\' contains errors. No code generated!'
        return MessageCode.NEURON_CONTAINS_ERRORS, message

    @classmethod
    def getStartProcessingNeuron(cls, _neuronName=None):
        """
        Returns a message indicating that the processing of a neuron is started.
        :param _neuronName: the name of the neuron
        :type _neuronName: str
        :return: a message
        :rtype: str
        """
        assert (_neuronName is not None and isinstance(_neuronName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _neuronName
        message = 'Starts processing of the neuron \'' + _neuronName + '\''
        return MessageCode.START_PROCESSING_NEURON, message

    @classmethod
    def getCodeGenerated(cls, _neuronName=None, _path=None):
        """
        Returns a message indicating that code has been successfully generated for a neuron in a certain path.
        :param _neuronName: the name of the neuron.
        :type _neuronName: str
        :param _path: the path to the file
        :type _path: str
        :return: a message
        :rtype: str
        """
        assert (_neuronName is not None and isinstance(_neuronName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _neuronName
        assert (_path is not None and isinstance(_path, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _path
        message = 'Successfully generated NEST code for the neuron: \'' + _neuronName + '\' in: \'' + _path + '\''
        return MessageCode.CODE_SUCCESSFULLY_GENERATED, message

    @classmethod
    def getModuleGenerated(cls, _path):
        """
        Returns a message indicating that a module has been successfully generated.
        :param _path: the path to the generated file
        :type _path: str
        :return: a message
        :rtype: str
        """
        assert (_path is not None and isinstance(_path, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _path
        message = 'Successfully generated NEST module code in \'' + _path + '\''
        return MessageCode.MODULE_SUCCESSFULLY_GENERATED, message

    @classmethod
    def getDryRun(cls):
        """
        Retrurns a message indicating that a dry run is performed.
        :return: a message
        :rtype: str
        """
        message = 'Dry mode selected with -dry parameter, no models generated!'
        return MessageCode.DRY_RUN, message

    @classmethod
    def getVariableUsedBeforeDeclaration(cls, _variableName=None):
        """
        Returns a message indicating that a variable is used before declaration.
        :param _variableName: a variable name
        :type _variableName: str
        :return: a message
        :rtype: str
        """
        assert (_variableName is not None and isinstance(_variableName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _variableName
        message = 'Variable \'%s\' used before declaration!' % _variableName
        return MessageCode.VARIABLE_USED_BEFORE_DECLARATION, message

    @classmethod
    def getVariableDefinedRecursively(cls, _variableName):
        """
        Returns a message indicating that a variable is defined recursively.
        :param _variableName: a variable name
        :type _variableName: str
        :return: a message
        :rtype: str
        """
        assert (_variableName is not None and isinstance(_variableName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _variableName
        message = 'Variable \'%s\' defined recursively!' % _variableName
        return MessageCode.VARIABLE_DEFINED_RECURSIVELY, message

    @classmethod
    def getValueAssignedToBuffer(cls, _bufferName=None):
        """
        Returns a message indicating that a value has been assigned to a buffer.
        :param _bufferName: a buffer name
        :type _bufferName: str
        :return: a message
        :rtype: str
        """
        assert (_bufferName is not None and isinstance(_bufferName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _bufferName
        message = 'Value assigned to buffer \'%s\'!' % _bufferName
        return MessageCode.VALUE_ASSIGNED_TO_BUFFER, message

    @classmethod
    def getFirstArgNotShapeOrEquation(cls, _funcName=None):
        assert (_funcName is not None and isinstance(_funcName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _funcName
        message = 'First argument of \'%s\' not a shape or equation!' % _funcName
        return MessageCode.ARG_NOT_SHAPE_OR_EQUATION, message

    @classmethod
    def getSecondArgNotABuffer(cls, _funcName=None):
        assert (_funcName is not None and isinstance(_funcName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _funcName
        message = 'Second argument of \'%s\' not a buffer!' % _funcName
        return MessageCode.ARG_NOT_BUFFER, message

    @classmethod
    def getWrongNumerator(cls, _unit=None):
        assert (_unit is not None and isinstance(_unit, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _unit
        message = 'Numeric numerator of unit \'%s\' not 1!' % _unit
        return MessageCode.NUMERATOR_NOT_ONE, message

    @classmethod
    def getOrderNotDeclared(cls, _lhs=None):
        assert (_lhs is not None and isinstance(_lhs, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _lhs
        message = 'Order of differential equation for %s is not declared!' % _lhs
        return MessageCode.ORDER_NOT_DECLARED, message

    @classmethod
    def getCurrentBufferSpecified(cls, _name=None, _keyword=None):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Current buffer \'%s\' specified with type keywords (%s)' % (_name, _keyword)
        return MessageCode.CURRENT_BUFFER_SPECIFIED, message

    @classmethod
    def getBlockNotDefinedCorrectly(cls, _block=None, _missing=False):
        if _missing:
            message = _block + ' block not defined, model not correct!'
        else:
            message = _block + ' block not unique, model not correct!!'
        return MessageCode.BLOCK_NOT_CORRECT, message

    @classmethod
    def getEquationVarNotInInitValuesBlock(cls, _variableName=None):
        assert (_variableName is not None and isinstance(_variableName, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _variableName
        message = 'Ode equation lhs-variable \'%s\' not defined in initial-values block!' % _variableName
        return MessageCode.VARIABLE_NOT_IN_INIT, message

    @classmethod
    def getWrongNumberOfArgs(cls, _functionCall=None, _expected=None, _got=None):
        message = 'Wrong number of arguments in function-call \'%s\'! Expected \'%s\', found \'%s\'.' % (
            _functionCall, _expected, _got)
        return MessageCode.WRONG_NUMBER_OF_ARGS, message

    @classmethod
    def getNoRhs(cls, _name=None):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Function variable \'%s\' has no right-hand side!' % _name
        return MessageCode.NO_RHS, message

    @classmethod
    def getSeveralLhs(cls, _names=None):
        message = 'Function declared with several variables (%s)!' % _names
        return MessageCode.SEVERAL_LHS, message

    @classmethod
    def getFunctionRedeclared(cls, _name, _predefined=None):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        if _predefined:
            message = 'Predefined function \'%s\' redeclared!' % _name
        else:
            message = 'Function \'%s\' redeclared!' % _name
        return MessageCode.FUNCTION_REDECLARED, message

    @classmethod
    def getNoOde(cls, _name=None):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Variable \'%s\' not provided with an ODE!' % _name
        return MessageCode.NO_ODE, message

    @classmethod
    def getNoInitValue(cls, _name=None):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Initial value of ode variable \'%s\' not provided!'
        return MessageCode.NO_INIT_VALUE, message

    @classmethod
    def getNeuronRedeclared(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Neuron \'%s\' redeclared!' % _name
        return MessageCode.NEURON_REDECLARED, message

    @classmethod
    def getNestCollision(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Function \'%s\' collides with NEST namespace!' % _name
        return MessageCode.NEST_COLLISION, message

    @classmethod
    def getShapeOutsideConvolve(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Shape \'%s\' used outside convolve!' % _name
        return MessageCode.SHAPE_OUTSIDE_CONVOLVE, message

    @classmethod
    def getCompilationUnitNameCollision(cls, _name, _art1, _art2):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        assert (_art1 is not None and isinstance(_art1, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _art1
        assert (_art2 is not None and isinstance(_art2, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _art2
        message = 'Name collision of \'%s\' in \'%s\' and \'%s\'!' % (_name, _art1, _art2)
        return MessageCode.NAME_COLLISION, message

    @classmethod
    def getDataTypeNotSpecified(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Data type of \'%s\' at not specified!' % _name
        return MessageCode.TYPE_NOT_SPECIFIED, message

    @classmethod
    def getNotTypeAllowed(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'No data type allowed for \'%s\'!' % _name
        return MessageCode.NO_TYPE_ALLOWED, message

    @classmethod
    def getAssignmentNotAllowed(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Assignment to \'%s\' not allowed!' % _name
        return MessageCode.NO_ASSIGNMENT_ALLOWED, message

    @classmethod
    def getNotAVariable(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = '\'%s\' not a variable!' % _name
        return MessageCode.NOT_A_VARIABLE, message

    @classmethod
    def getMultipleKeywords(cls, _keyword):
        message = 'Buffer specified with multiple \'%s\' keywords!' % _keyword
        return MessageCode.MULTIPLE_KEYWORDS, message

    @classmethod
    def getVectorInNonVector(cls, _vector, _nonVector):
        message = 'Vector value \'%s\' used in a non-vector declaration of variables \'%s\'!' % (_vector, _nonVector)
        return MessageCode.VECTOR_IN_NON_VECTOR, message

    @classmethod
    def getVariableRedeclared(cls, _name, _predefined=False):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        assert (_predefined is not None and isinstance(_predefined, bool)), \
            '(PyNestML.Utils.Message) Not a bool provided (%s)!' % _predefined
        if _predefined:
            message = 'Predefined variable \'%s\' redeclared!' % _name
        else:
            message = 'Variable \'%s\' redeclared !' % _name
        return MessageCode.VARIABLE_REDECLARED, message

    @classmethod
    def getNoReturn(cls):
        message = 'Return statement expected!'
        return MessageCode.NO_RETURN, message

    @classmethod
    def getNotLastStatement(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = '\'%s\' not the last statement!' % _name
        return MessageCode.NOT_LAST_STATEMENT, message

    @classmethod
    def getFunctionNotDeclared(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Function \'%s\' is not declared!' % _name
        return MessageCode.FUNCTION_NOT_DECLARED, message

    @classmethod
    def getCouldNotResolve(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'Could not resolve symbol \'%s\'!' % _name
        return MessageCode.SYMBOL_NOT_RESOLVED, message

    @classmethod
    def getNeuronSolvedBySolve(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'The neuron \'%s\' will be solved numerically with GSL solver without modification!' % _name
        return MessageCode.NEURON_SOLVED_BY_GSL, message

    @classmethod
    def getNeuronAnalyzed(cls, _name):
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.Utils.Message) Not a string provided (%s)!' % _name
        message = 'The neuron \'%s\' will be analysed!' % _name
        return MessageCode.NEURON_ANALYZED, message


class MessageCode(Enum):
    """
    A mapping between codes and the corresponding messages.
    """
    START_PROCESSING_FILE = 0
    TYPE_REGISTERED = 1
    START_SYMBOL_TABLE_BUILDING = 2
    FUNCTION_CALL_TYPE_ERROR = 3
    TYPE_NOT_DERIVABLE = 4
    IMPLICIT_CAST = 5
    CAST_NOT_POSSIBLE = 6
    TYPE_DIFFERENT_FROM_EXPECTED = 7
    ADD_SUB_TYPE_MISMATCH = 8
    BUFFER_SET_TO_CONDUCTANCE_BASED = 9
    ODE_UPDATED = 10
    NO_VARIABLE_FOUND = 11
    SPIKE_BUFFER_TYPE_NOT_DEFINED = 12
    NEURON_CONTAINS_ERRORS = 13
    START_PROCESSING_NEURON = 14
    CODE_SUCCESSFULLY_GENERATED = 15
    MODULE_SUCCESSFULLY_GENERATED = 16
    DRY_RUN = 17
    VARIABLE_USED_BEFORE_DECLARATION = 18
    VARIABLE_DEFINED_RECURSIVELY = 19
    VALUE_ASSIGNED_TO_BUFFER = 20
    ARG_NOT_SHAPE_OR_EQUATION = 21
    ARG_NOT_BUFFER = 22
    NUMERATOR_NOT_ONE = 23
    ORDER_NOT_DECLARED = 24
    CURRENT_BUFFER_SPECIFIED = 25
    BLOCK_NOT_CORRECT = 26
    VARIABLE_NOT_IN_INIT = 27
    WRONG_NUMBER_OF_ARGS = 28
    NO_RHS = 29
    SEVERAL_LHS = 30
    FUNCTION_REDECLARED = 31
    FUNCTION_NOT_DECLARED = 52
    NO_ODE = 32
    NO_INIT_VALUE = 33
    NEURON_REDECLARED = 34
    NEST_COLLISION = 35
    SHAPE_OUTSIDE_CONVOLVE = 36
    NAME_COLLISION = 37
    TYPE_NOT_SPECIFIED = 38
    NO_TYPE_ALLOWED = 39
    NO_ASSIGNMENT_ALLOWED = 40
    NOT_A_VARIABLE = 41
    MULTIPLE_KEYWORDS = 42
    VECTOR_IN_NON_VECTOR = 43
    VARIABLE_REDECLARED = 44
    SOFT_INCOMPATIBILITY = 45
    HARD_INCOMPATIBILITY = 46
    NO_RETURN = 47
    NOT_LAST_STATEMENT = 48
    SYMBOL_NOT_RESOLVED = 49
    TYPE_MISMATCH = 50
    NO_SEMANTICS = 51
    NEURON_SOLVED_BY_GSL = 52
    NEURON_ANALYZED = 53
