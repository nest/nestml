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
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.codegeneration.PyNestMl2NESTTypeConverter import NESTML2NESTTypeConverter
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from pynestml.modelprocessor.ASTFunction import ASTFunction
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTForStmt import ASTForStmt
from pynestml.modelprocessor.VariableSymbol import VariableSymbol, BlockType
from pynestml.modelprocessor.ASTBody import ASTBody


class NestPrinter(object):
    """
    This class contains all methods as required to transform
    """
    __expressionPrettyPrinter = None

    def __init__(self, _expressionPrettyPrinter, _referenceConvert=None):
        """
        The standard constructor.
        :param _referenceConvert: a single reference converter
        :type _referenceConvert:  IReferenceConverter
        """
        if _expressionPrettyPrinter is not None:
            self.__expressionPrettyPrinter = _expressionPrettyPrinter
        else:
            self.__expressionPrettyPrinter = ExpressionsPrettyPrinter(_referenceConvert)
        return

    def printExpression(self, _ast=None):
        """
        Pretty
        Prints the handed over rhs to a nest readable format.
        :param _ast: a single ast node.
        :type _ast: ASTExpression or ASTSimpleExpression
        :return: the corresponding string representation
        :rtype: str
        """
        assert (_ast is not None and (isinstance(_ast, ASTSimpleExpression) or isinstance(_ast, ASTExpression))), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of rhs provided (%s)!' % type(_ast)
        return self.__expressionPrettyPrinter.printExpression(_ast)

    def printMethodCall(self, _ast=None):
        """
        Prints a single handed over function call.
        :param _ast: a single function call.
        :type _ast: ASTFunctionCall
        :return: the corresponding string representation.
        :rtype: str
        """
        assert (_ast is not None and isinstance(_ast, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of function call provided (%s)!' % type(_ast)
        return self.__expressionPrettyPrinter.printFunctionCall(_ast)

    def printComparisonOperator(self, _forStmt=None):
        """
        Prints a single handed over comparison operator for a for stmt to a Nest processable format.
        :param _forStmt: a single for stmt
        :type _forStmt: ASTForStmt
        :return: a string representation
        :rtype: str
        """
        assert (_forStmt is not None and isinstance(_forStmt, ASTForStmt)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of for-stmt provided (%s)!' % type(_forStmt)
        step = _forStmt.get_step()
        if step < 0:
            return '>'
        elif step > 0:
            return '<'
        else:
            return '!='

    def printStep(self, _forStmt=None):
        """
        Prints the step length to a nest processable format.
        :param _forStmt: a single for stmt
        :type _forStmt: ASTForStmt
        :return: a string representation
        :rtype: str
        """
        assert (_forStmt is not None and isinstance(_forStmt, ASTForStmt)), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of for-stmt provided (%s)!' % type(_forStmt)
        return _forStmt.get_step()

    @classmethod
    def printOrigin(cls, _variableSymbol=None):
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: the corresponding prefix
        :rtype: str
        """
        assert (_variableSymbol is not None and isinstance(_variableSymbol, VariableSymbol)), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of variable symbol provided (%s)!' % type(
                _variableSymbol)
        if _variableSymbol.get_block_type() == BlockType.STATE:
            return 'S_.'
        elif _variableSymbol.get_block_type() == BlockType.INITIAL_VALUES:
            return 'S_.'
        elif _variableSymbol.get_block_type() == BlockType.EQUATION:
            return 'S_.'
        elif _variableSymbol.get_block_type() == BlockType.PARAMETERS:
            return 'P_.'
        elif _variableSymbol.get_block_type() == BlockType.INTERNALS:
            return 'V_.'
        elif _variableSymbol.get_block_type() == BlockType.INPUT_BUFFER_CURRENT:
            return 'B_.'
        elif _variableSymbol.get_block_type() == BlockType.INPUT_BUFFER_SPIKE:
            return 'B_.'
        else:
            return ''

    def printOutputEvent(self, _astBody=None):
        """
        For the handed over neuron, this operations checks of output event shall be preformed.
        :param _astBody: a single neuron body
        :type _astBody: ASTBody
        :return: the corresponding representation of the event
        :rtype: str
        """
        assert (_astBody is not None and isinstance(_astBody, ASTBody)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of body provided (%s)!' % type(_astBody)
        outputs = _astBody.get_output_blocks()
        if len(outputs) > 0:
            output = outputs[0]
            if output.is_spike():
                return 'nest::SpikeEvent'
            elif output.is_current():
                return 'nest::CurrentEvent'
            else:
                Logger.log_message('Unexpected output type. Must be current or spike.', LoggingLevel.ERROR)
                return 'none'
        else:
            return 'none'

    def printBufferInitialization(self, _variableSymbol=None):
        """
        Prints the buffer initialization.
        :param _variableSymbol: a single variable symbol.
        :type _variableSymbol: VariableSymbol
        :return: a buffer initialization
        :rtype: str
        """
        return 'get_' + _variableSymbol.get_symbol_name() + '().clear(); //includes resize'

    def printFunctionDeclaration(self, _function=None):
        """
        Returns a nest processable function declaration head, i.e. the part which appears in the .h file.
        :param _function: a single function.
        :type _function: ASTFunction
        :return: the corresponding string representation.
        :rtype: str
        """
        from pynestml.modelprocessor.ASTFunction import ASTFunction
        from pynestml.modelprocessor.Symbol import SymbolKind
        assert (_function is not None and isinstance(_function, ASTFunction)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of function provided (%s)!' % type(_function)
        functionSymbol = _function.get_scope().resolveToSymbol(_function.get_name(), SymbolKind.FUNCTION)
        if functionSymbol is not None:
            declaration = _function.print_comment('//') + '\n'
            declaration += NESTML2NESTTypeConverter.convert(functionSymbol.get_return_type()).replace('.', '::')
            declaration += ' '
            declaration += _function.get_name() + '('
            for typeSym in functionSymbol.get_parameter_types():
                declaration += NESTML2NESTTypeConverter.convert(typeSym)
                if functionSymbol.get_parameter_types().index(typeSym) < len(functionSymbol.get_parameter_types()) - 1:
                    declaration += ', '
            declaration += ')\n'
            return declaration
        else:
            raise RuntimeException('Cannot resolve the method ' + _function.get_name())

    def printFunctionDefinition(self, _function=None, _namespace=None):
        """
        Returns a nest processable function definition, i.e. the part which appears in the .c file.
        :param _function: a single function.
        :type _function: ASTFunction
        :param _namespace: the namespace in which this function is defined in
        :type _namespace: str
        :return: the corresponding string representation.
        :rtype: str
        """
        assert (_function is not None and isinstance(_function, ASTFunction)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of function provided (%s)!' % type(_function)
        assert (_namespace is not None and isinstance(_namespace, str)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of namespace provided (%s)!' % type(_namespace)
        functionSymbol = _function.get_scope().resolveToSymbol(_function.get_name(), SymbolKind.FUNCTION)
        if functionSymbol is not None:
            # first collect all parameters
            params = list()
            for param in _function.get_parameters():
                params.append(param.get_name())
            declaration = _function.print_comment('//') + '\n'
            declaration += NESTML2NESTTypeConverter.convert(functionSymbol.get_return_type()).replace('.', '::')
            declaration += ' '
            if _namespace is not None:
                declaration += _namespace + '::'
            declaration += _function.get_name() + '('
            for typeSym in functionSymbol.get_parameter_types():
                # create the type name combination, e.g. double Tau
                declaration += NESTML2NESTTypeConverter.convert(typeSym) + ' ' + \
                               params[functionSymbol.get_parameter_types().index(typeSym)]
                # if not the last component, separate by ','
                if functionSymbol.get_parameter_types().index(typeSym) < len(functionSymbol.get_parameter_types()) - 1:
                    declaration += ', '
            declaration += ')\n'
            return declaration
        else:
            raise RuntimeException('Cannot resolve the method ' + _function.get_name())

    def printBufferArrayGetter(self, _buffer=None):
        """
        Returns a string containing the nest declaration for a multi-receptor spike buffer.
        :param _buffer: a single buffer Variable Symbol
        :type _buffer: VariableSymbol
        :return: a string representation of the getter
        :rtype: str
        """
        assert (_buffer is not None and isinstance(_buffer, VariableSymbol)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of buffer symbol provided (%s)!' % type(_buffer)
        if _buffer.is_spike_buffer() and _buffer.is_inhibitory() and _buffer.is_excitatory():
            return 'inline ' + NESTML2NESTTypeConverter.convert(_buffer.get_type_symbol()) + '&' + ' get_' \
                   + _buffer.get_symbol_name() + '() {' + \
                   '  return spike_inputs_[' + _buffer.get_symbol_name().upper() + ' - 1]; }'
        else:
            return self.printBufferGetter(_buffer, True)

    def printBufferGetter(self, _buffer=None, _isInStruct=False):
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
        declaration = 'inline '
        if _buffer.has_vector_parameter():
            declaration += 'std::vector<'
            declaration += NESTML2NESTTypeConverter.convert(_buffer.get_type_symbol())
            declaration += '> &'
        else:
            declaration += NESTML2NESTTypeConverter.convert(_buffer.get_type_symbol()) + '&'
        declaration += ' get_' + _buffer.get_symbol_name() + '() {'
        if _isInStruct:
            declaration += 'return ' + _buffer.get_symbol_name() + ';'
        else:
            declaration += 'return B_.get_' + _buffer.get_symbol_name() + '();'
        declaration += '}'
        return declaration

    def printBufferDeclarationValue(self, _buffer=None):
        """
        Returns a string representation for the declaration of a buffer's value.
        :param _buffer: a single buffer variable symbol
        :type _buffer: VariableSymbol
        :return: the corresponding string representation
        :rtype: str
        """
        assert (_buffer is not None and isinstance(_buffer, VariableSymbol)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of buffer symbol provided (%s)!' % type(_buffer)
        if _buffer.has_vector_parameter():
            return 'std::vector<double> ' + NestNamesConverter.bufferValue(_buffer)
        else:
            return 'double ' + NestNamesConverter.bufferValue(_buffer)

    def printBufferDeclaration(self, _buffer=None):
        """
        Returns a string representation for the declaration of a buffer.
        :param _buffer: a single buffer variable symbol
        :type _buffer: VariableSymbol
        :return: the corresponding string representation
        :rtype: str
        """
        assert (_buffer is not None and isinstance(_buffer, VariableSymbol)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of buffer symbol provided (%s)!' % type(_buffer)
        if _buffer.has_vector_parameter():
            bufferType = 'std::vector< ' + NESTML2NESTTypeConverter.convert(_buffer.get_type_symbol()) + ' >'
        else:
            bufferType = NESTML2NESTTypeConverter.convert(_buffer.get_type_symbol())
        bufferType.replace(".", "::")
        return bufferType + " " + _buffer.get_symbol_name()

    def printBufferDeclarationHeader(self, _buffer=None):
        """
        Prints the comment as stated over the buffer declaration.
        :param _buffer: a single buffer variable symbol.
        :type _buffer: VariableSymbol
        :return: the corresponding string representation
        :rtype: str
        """
        assert (_buffer is not None and isinstance(_buffer, VariableSymbol)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of buffer symbol provided (%s)!' % type(_buffer)
        return '//!< Buffer incoming ' + _buffer.get_type_symbol().get_symbol_name() + 's through delay, as sum'


class RuntimeException(Exception):
    """
    This exception is thrown whenever a problem during runtime occurs.
    """
    pass
