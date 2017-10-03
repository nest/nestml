#
# NestPrinter.py
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
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.codegeneration.NESTML2NESTTypeConverter import NESTML2NESTTypeConverter
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.nestml.VariableSymbol import VariableSymbol


class NestPrinter(object):
    """
    This class contains all methods as required to transform
    """

    @classmethod
    def printExpression(cls, _ast=None):
        """
        Prints the handed over expression to a nest readable format.
        :param _ast: a single ast node.
        :type _ast: ASTExpression or ASTSimpleExpression
        :return: the corresponding string representation
        :rtype: str
        """
        return "TODO expr"

    @classmethod
    def printMethodCall(cls, _ast=None):
        """
        Prints a single handed over function call.
        :param _ast: a single function call.
        :type _ast: ASTFunctionCall
        :return: the corresponding string representation.
        :rtype: str
        """
        return "TODO function"

    @classmethod
    def printComparisonOperator(cls, _forStmt=None):
        """
        Prints a single handed over comparison operator to a Nest processable format.
        :param _ast: a single comparison operator object.
        :type _ast: ASTComparisonOperator
        :return: a string representation
        :rtype: str
        """
        from pynestml.nestml.ASTForStmt import ASTForStmt
        assert (_forStmt is not None and isinstance(_forStmt, ASTForStmt)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of for-stmt provided (%s)!' % type(_forStmt)
        step = _forStmt.getStep()
        if step < 0:
            return '>'
        elif step > 0:
            return '<'
        else:
            return '!='  # todo, this should not happen actually

    @classmethod
    def printVariable(cls, _ast=None):
        """
        Prints a single handed over variable.
        :param _ast: a single variable
        :type _ast: ASTVariable
        :return: a string representation
        :rtype: str
        """
        return "TODO variable"

    @classmethod
    def printStep(cls, _forStmt=None):
        """
        Prints the step length to a nest processable format.
        :param _forStmt: a single for stmt
        :type _forStmt: ASTForStmt
        :return: a string representation
        :rtype: str
        """
        from pynestml.nestml.ASTForStmt import ASTForStmt
        assert (_forStmt is not None and isinstance(_forStmt, ASTForStmt)), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of for-stmt provided (%s)!' % type(_forStmt)
        return _forStmt.getStep()

    @classmethod
    def printOrigin(cls, _variableSymbol=None):
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: the corresponding prefix
        :rtype: str
        """
        from pynestml.nestml.VariableSymbol import VariableSymbol, BlockType
        assert (_variableSymbol is not None and isinstance(_variableSymbol, VariableSymbol)), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of variable symbol provided (%s)!' % type(
                _variableSymbol)
        if _variableSymbol.getBlockType() == BlockType.STATE:
            return 'S_.'
        elif _variableSymbol.getBlockType() == BlockType.INITIAL_VALUES:  # todo
            return 'S_.'
        elif _variableSymbol.getBlockType() == BlockType.EQUATION:
            return 'S_.'
        elif _variableSymbol.getBlockType() == BlockType.PARAMETERS:
            return 'P_.'
        elif _variableSymbol.getBlockType() == BlockType.INTERNALS:
            return 'V_.'
        elif _variableSymbol.getBlockType() == BlockType.INPUT_BUFFER_CURRENT:
            return 'B_.'
        elif _variableSymbol.getBlockType() == BlockType.INPUT_BUFFER_SPIKE:
            return 'B_.'
        else:
            return ''

    @classmethod
    def printOutputEvent(cls, _astBody=None):
        """
        For the handed over neuron, this operations checks of output event shall be preformed.
        :param _astBody: a single neuron body
        :type _astBody: ASTBody
        :return: the corresponding representation of the event
        :rtype: str
        """
        from pynestml.nestml.ASTBody import ASTBody
        assert (_astBody is not None and isinstance(_astBody, ASTBody)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of body provided (%s)!' % type(_astBody)
        outputs = _astBody.getOutputBlocks()
        if len(outputs) > 0:
            output = outputs[0]
            if output.isSpike():
                return 'nest::SpikeEvent'
            elif output.isCurrent():
                return 'nest::CurrentEvent'
            else:
                Logger.logMessage('Unexpected output type. Must be current or spike.', LOGGING_LEVEL.ERROR)
                return 'none'
        else:
            return 'none'

    @classmethod
    def printBufferInitialization(cls, _variableSymbol=None):
        """
        Prints the buffer initialization.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: a buffer initialization
        :rtype: str
        """
        return 'get_' + _variableSymbol.getSymbolName() + '().clear(); //includes resize'

    @classmethod
    def printFunctionDeclaration(cls, _function=None):
        """
        Returns a nest processable function declaration head, i.e. the part which appears in the .h file.
        :param _function: a single function.
        :type _function: ASTFunction
        :return: the corresponding string representation.
        :rtype: str
        """
        from pynestml.nestml.ASTFunction import ASTFunction
        from pynestml.nestml.Symbol import SymbolKind
        assert (_function is not None and isinstance(_function, ASTFunction)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of function provided (%s)!' % type(_function)
        functionSymbol = _function.getScope().resolveToSymbol(_function.getName(), SymbolKind.FUNCTION)
        if functionSymbol is not None:
            # todo printing of function comments
            declaration = NESTML2NESTTypeConverter.convert(functionSymbol.getReturnType()).replace('.', '::')
            declaration += ' '
            declaration += _function.getName() + '('
            for typeSym in functionSymbol.getParameterTypes():
                declaration += NESTML2NESTTypeConverter.convert(typeSym)
                if functionSymbol.getParameterTypes().index(typeSym) < len(functionSymbol.getParameterTypes()) - 1:
                    declaration += ', '
            declaration += ')\n'
            return declaration
        else:
            raise RuntimeException('Cannot resolve the method ' + _function.getName())

    @classmethod
    def printFunctionDefinition(cls, _function=None):
        """
        Returns a nest processable function definition, i.e. the part which appears in the .c file.
        :param _function: a single function.
        :type _function: ASTFunction
        :return: the corresponding string representation.
        :rtype: str
        """
        # todo printing of function comments
        from pynestml.nestml.ASTFunction import ASTFunction
        from pynestml.nestml.Symbol import SymbolKind
        assert (_function is not None and isinstance(_function, ASTFunction)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of function provided (%s)!' % type(_function)
        functionSymbol = _function.getScope().resolveToSymbol(_function.getName(), SymbolKind.FUNCTION)
        parameters = _function.getParameters()
        if functionSymbol is not None:
            # first collect all parameters
            params = list()
            for param in _function.getParameters():
                params.append(param.getName())
            declaration = NESTML2NESTTypeConverter.convert(functionSymbol.getReturnType()).replace('.', '::')
            declaration += ' '
            declaration += _function.getName() + '('
            for typeSym in functionSymbol.getParameterTypes():
                # create the type name combination, e.g. double Tau
                declaration += NESTML2NESTTypeConverter.convert(typeSym) + ' ' + \
                               params[functionSymbol.getParameterTypes().index(typeSym)]
                # if not the last component, separate by ','
                if functionSymbol.getParameterTypes().index(typeSym) < len(functionSymbol.getParameterTypes()) - 1:
                    declaration += ', '
            declaration += ')\n'
            return declaration
        else:
            raise RuntimeException('Cannot resolve the method ' + _function.getName())

    @classmethod
    def printBufferArrayGetter(cls, _buffer=None):
        """
        Returns a string containing the nest declaration for a multi-receptor spike buffer.
        :param _buffer: a single buffer Variable Symbol
        :type _buffer: VariableSymbol
        :return: a string representation of the getter
        :rtype: str
        """
        assert (_buffer is not None and isinstance(_buffer, VariableSymbol)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of buffer symbol provided (%s)!' % type(_buffer)
        if _buffer.isSpikeBuffer() and _buffer.isInhibitory() and _buffer.isExcitatory():
            return 'inline ' + NESTML2NESTTypeConverter.convert(_buffer.getTypeSymbol()) + '&' + ' get_' \
                   + _buffer.getSymbolName() + '() {' + \
                   '  return spike_inputs_[' + _buffer.getSymbolName().upper() + ' - 1]; }'
        else:
            return cls.printBufferGetter(_buffer, True)

    @classmethod
    def printBufferGetter(cls, _buffer=None, _isInStruct=False):
        """
        Returns a string representation declaring a buffer getter as required in nest.
        :param _buffer: a single variable symbol representing a buffer.
        :type _buffer: VariableSymbol
        :param _isInStruct: indicates whether this getter is used in a struct or not
        :type _isInStruct: bool
        :return: a string representation of the getter.
        :rtype: str
        """
        assert (_buffer is not None and isinstance(_buffer, VariableSymbol)), \
            '(PyNestMl.CodeGeneration.Printer) No or wrong type of buffer symbol provided (%s)!' % type(_buffer)
        assert (_isInStruct is not None and isinstance(_isInStruct, bool)), \
            '(PyNestMl.CodeGeneration.Printer) No or wrong type of is-in-struct provided (%s)!' % type(_isInStruct)
        declaration = 'inline'
        if _buffer.hasVectorParameter():
            declaration += 'std::vector< '
            declaration += NESTML2NESTTypeConverter.convert(_buffer.getTypeSymbol())
            declaration += ' > &'
        else:
            declaration += NESTML2NESTTypeConverter.convert(_buffer.getTypeSymbol()) + '&'
        declaration += ' get_' + _buffer.getSymbolName() + '() {'
        if _isInStruct:
            declaration += 'return' + _buffer.getSymbolName() + ';'
        else:
            declaration += 'return B_.get_' + _buffer.getSymbolName() + '();'
        declaration += '}'
        return declaration

    @classmethod
    def printBufferDeclarationValue(cls, _buffer=None):
        """
        Returns a string representation for the declaration of a buffer's value.
        :param _buffer: a single buffer variable symbol
        :type _buffer: VariableSymbol
        :return: the corresponding string representation
        :rtype: str
        """
        assert (_buffer is not None and isinstance(_buffer, VariableSymbol)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of buffer symbol provided (%s)!' % type(_buffer)
        if _buffer.hasVectorParameter():
            return 'std::vector< double > ' + NestNamesConverter.bufferValue(_buffer)
        else:
            return "double " + NestNamesConverter.bufferValue(_buffer)

    @classmethod
    def printBufferDeclaration(cls, _buffer=None):
        """
        Returns a string representation for the declaration of a buffer.
        :param _buffer: a single buffer variable symbol
        :type _buffer: VariableSymbol
        :return: the corresponding string representation
        :rtype: str
        """

        if _buffer.hasVectorParameter():
            bufferType = 'std::vector< ' + NESTML2NESTTypeConverter.convert(_buffer.getTypeSymbol()) + ' >'
        else:
            bufferType = NESTML2NESTTypeConverter.convert(_buffer.getTypeSymbol())
        bufferType.replace(".", "::")

        return "//!< Buffer incoming " + _buffer.getTypeSymbol().getSymbolName() + "s through delay, as sum\n" + \
               bufferType + " " + _buffer.getSymbolName();


class RuntimeException(Exception):
    """
    This exception is thrown whenever a problem during runtime occurs.
    """
    pass
