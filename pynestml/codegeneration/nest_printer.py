#
# nest_printer.py
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
from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.pynestml_2_nest_type_converter import PyNestml2NestTypeConverter
from pynestml.codegeneration.i_reference_converter import IReferenceConverter
from pynestml.meta_model.ast_body import ASTBody
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_for_stmt import ASTForStmt
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import VariableSymbol, BlockType


class NestPrinter(object):
    """
    This class contains all methods as required to transform
    """
    
    def __init__(self, expression_pretty_printer, reference_convert=None):
        """
        The standard constructor.
        :param reference_convert: a single reference converter
        :type reference_convert: IReferenceConverter
        """
        if expression_pretty_printer is not None:
            self.expression_pretty_printer = expression_pretty_printer
        else:
            self.expression_pretty_printer = ExpressionsPrettyPrinter(reference_convert)
        return

    def print_expression(self, node):
        # type: (ASTExpressionNode) -> str
        """
        Pretty Prints the handed over rhs to a nest readable format.
        :param node: a single meta_model node.
        :type node: ASTExpressionNode
        :return: the corresponding string representation
        :rtype: str
        """
        return self.expression_pretty_printer.print_expression(node)

    def print_method_call(self, node):
        # type: (ASTFunctionCall) -> str
        """
        Prints a single handed over function call.
        :param node: a single function call.
        :type node: ASTFunctionCall
        :return: the corresponding string representation.
        :rtype: str
        """
        return self.expression_pretty_printer.print_function_call(node)

    @classmethod
    def print_comparison_operator(cls, for_stmt):
        """
        Prints a single handed over comparison operator for a for stmt to a Nest processable format.
        :param for_stmt: a single for stmt
        :type for_stmt: ASTForStmt
        :return: a string representation
        :rtype: str
        """
        step = for_stmt.get_step()
        if step < 0:
            return '>'
        elif step > 0:
            return '<'
        else:
            return '!='

    @classmethod
    def print_step(cls, for_stmt):
        """
        Prints the step length to a nest processable format.
        :param for_stmt: a single for stmt
        :type for_stmt: ASTForStmt
        :return: a string representation
        :rtype: str
        """
        assert isinstance(for_stmt, ASTForStmt), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of for-stmt provided (%s)!' % type(for_stmt)
        return for_stmt.get_step()

    @classmethod
    def print_origin(cls, variable_symbol):
        """
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: the corresponding prefix
        :rtype: str
        """
        assert isinstance(variable_symbol, VariableSymbol), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of variable symbol provided (%s)!' % type(
                variable_symbol)
        if variable_symbol.block_type == BlockType.STATE:
            return 'S_.'
        elif variable_symbol.block_type == BlockType.INITIAL_VALUES:
            return 'S_.'
        elif variable_symbol.block_type == BlockType.EQUATION:
            return 'S_.'
        elif variable_symbol.block_type == BlockType.PARAMETERS:
            return 'P_.'
        elif variable_symbol.block_type == BlockType.INTERNALS:
            return 'V_.'
        elif variable_symbol.block_type == BlockType.INPUT_BUFFER_CURRENT:
            return 'B_.'
        elif variable_symbol.block_type == BlockType.INPUT_BUFFER_SPIKE:
            return 'B_.'
        else:
            return ''

    @classmethod
    def print_output_event(cls, ast_body):
        """
        For the handed over neuron, this operations checks of output event shall be preformed.
        :param ast_body: a single neuron body
        :type ast_body: ASTBody
        :return: the corresponding representation of the event
        :rtype: str
        """
        assert (ast_body is not None and isinstance(ast_body, ASTBody)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of body provided (%s)!' % type(ast_body)
        outputs = ast_body.get_output_blocks()
        if len(outputs) > 0:
            output = outputs[0]
            if output.is_spike():
                return 'nest::SpikeEvent'
            elif output.is_current():
                return 'nest::CurrentEvent'
            else:
                raise RuntimeError('Unexpected output type. Must be current or spike, is %s.' % str(output))
        else:
            return 'none'

    @classmethod
    def print_buffer_initialization(cls, variable_symbol):
        """
        Prints the buffer initialization.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: a buffer initialization
        :rtype: str
        """
        return 'get_' + variable_symbol.get_symbol_name() + '().clear(); //includes resize'

    @classmethod
    def print_function_declaration(cls, ast_function):
        """
        Returns a nest processable function declaration head, i.e. the part which appears in the .h file.
        :param ast_function: a single function.
        :type ast_function: ASTFunction
        :return: the corresponding string representation.
        :rtype: str
        """
        from pynestml.meta_model.ast_function import ASTFunction
        from pynestml.symbols.symbol import SymbolKind
        assert (ast_function is not None and isinstance(ast_function, ASTFunction)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of ast_function provided (%s)!' % type(ast_function)
        function_symbol = ast_function.get_scope().resolve_to_symbol(ast_function.get_name(), SymbolKind.FUNCTION)
        if function_symbol is None:
            raise RuntimeError('Cannot resolve the method ' + ast_function.get_name())
        declaration = ast_function.print_comment('//') + '\n'
        declaration += PyNestml2NestTypeConverter.convert(function_symbol.get_return_type()).replace('.', '::')
        declaration += ' '
        declaration += ast_function.get_name() + '('
        for typeSym in function_symbol.get_parameter_types():
            declaration += PyNestml2NestTypeConverter.convert(typeSym)
            if function_symbol.get_parameter_types().index(typeSym) < len(
                    function_symbol.get_parameter_types()) - 1:
                declaration += ', '
        declaration += ') const\n'
        return declaration

    @classmethod
    def print_function_definition(cls, ast_function, namespace):
        """
        Returns a nest processable function definition, i.e. the part which appears in the .cpp file.
        :param ast_function: a single function.
        :type ast_function: ASTFunction
        :param namespace: the namespace in which this function is defined in
        :type namespace: str
        :return: the corresponding string representation.
        :rtype: str
        """
        assert isinstance(ast_function, ASTFunction), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of ast_function provided (%s)!' % type(ast_function)
        assert isinstance(namespace, str), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of namespace provided (%s)!' % type(namespace)
        function_symbol = ast_function.get_scope().resolve_to_symbol(ast_function.get_name(), SymbolKind.FUNCTION)
        if function_symbol is None:
            raise RuntimeError('Cannot resolve the method ' + ast_function.get_name())
        # first collect all parameters
        params = list()
        for param in ast_function.get_parameters():
            params.append(param.get_name())
        declaration = ast_function.print_comment('//') + '\n'
        declaration += PyNestml2NestTypeConverter.convert(function_symbol.get_return_type()).replace('.', '::')
        declaration += ' '
        if namespace is not None:
            declaration += namespace + '::'
        declaration += ast_function.get_name() + '('
        for typeSym in function_symbol.get_parameter_types():
            # create the type name combination, e.g. double Tau
            declaration += PyNestml2NestTypeConverter.convert(typeSym) + ' ' + \
                            params[function_symbol.get_parameter_types().index(typeSym)]
            # if not the last component, separate by ','
            if function_symbol.get_parameter_types().index(typeSym) < \
                    len(function_symbol.get_parameter_types()) - 1:
                declaration += ', '
        declaration += ') const\n'
        return declaration

    def print_buffer_array_getter(self, ast_buffer):
        """
        Returns a string containing the nest declaration for a multi-receptor spike buffer.
        :param ast_buffer: a single buffer Variable Symbol
        :type ast_buffer: VariableSymbol
        :return: a string representation of the getter
        :rtype: str
        """
        assert (ast_buffer is not None and isinstance(ast_buffer, VariableSymbol)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of ast_buffer symbol provided (%s)!' % type(ast_buffer)
        if ast_buffer.is_spike_buffer() and ast_buffer.is_inhibitory() and ast_buffer.is_excitatory():
            return 'inline ' + PyNestml2NestTypeConverter.convert(ast_buffer.get_type_symbol()) + '&' + ' get_' \
                   + ast_buffer.get_symbol_name() + '() {' + \
                   '  return spike_inputs_[' + ast_buffer.get_symbol_name().upper() + ' - 1]; }'
        else:
            return self.print_buffer_getter(ast_buffer, True)

    @classmethod
    def print_buffer_getter(cls, ast_buffer, is_in_struct=False):
        """
        Returns a string representation declaring a buffer getter as required in nest.
        :param ast_buffer: a single variable symbol representing a buffer.
        :type ast_buffer: VariableSymbol
        :param is_in_struct: indicates whether this getter is used in a struct or not
        :type is_in_struct: bool
        :return: a string representation of the getter.
        :rtype: str
        """
        assert (ast_buffer is not None and isinstance(ast_buffer, VariableSymbol)), \
            '(PyNestMl.CodeGeneration.Printer) No or wrong type of ast_buffer symbol provided (%s)!' % type(ast_buffer)
        assert (is_in_struct is not None and isinstance(is_in_struct, bool)), \
            '(PyNestMl.CodeGeneration.Printer) No or wrong type of is-in-struct provided (%s)!' % type(is_in_struct)
        declaration = 'inline '
        if ast_buffer.has_vector_parameter():
            declaration += 'std::vector<'
            declaration += PyNestml2NestTypeConverter.convert(ast_buffer.get_type_symbol())
            declaration += '> &'
        else:
            declaration += PyNestml2NestTypeConverter.convert(ast_buffer.get_type_symbol()) + '&'
        declaration += ' get_' + ast_buffer.get_symbol_name() + '() {'
        if is_in_struct:
            declaration += 'return ' + ast_buffer.get_symbol_name() + ';'
        else:
            declaration += 'return B_.get_' + ast_buffer.get_symbol_name() + '();'
        declaration += '}'
        return declaration

    @classmethod
    def print_buffer_declaration_value(cls, ast_buffer):
        """
        Returns a string representation for the declaration of a buffer's value.
        :param ast_buffer: a single buffer variable symbol
        :type ast_buffer: VariableSymbol
        :return: the corresponding string representation
        :rtype: str
        """
        assert isinstance(ast_buffer, VariableSymbol), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of ast_buffer symbol provided (%s)!' % type(ast_buffer)
        if ast_buffer.has_vector_parameter():
            return 'std::vector<double> ' + NestNamesConverter.buffer_value(ast_buffer)
        else:
            return 'double ' + NestNamesConverter.buffer_value(ast_buffer)

    @classmethod
    def print_buffer_declaration(cls, ast_buffer):
        """
        Returns a string representation for the declaration of a buffer.
        :param ast_buffer: a single buffer variable symbol
        :type ast_buffer: VariableSymbol
        :return: the corresponding string representation
        :rtype: str
        """
        assert isinstance(ast_buffer, VariableSymbol), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of ast_buffer symbol provided (%s)!' % type(ast_buffer)
        if ast_buffer.has_vector_parameter():
            buffer_type = 'std::vector< ' + PyNestml2NestTypeConverter.convert(ast_buffer.get_type_symbol()) + ' >'
        else:
            buffer_type = PyNestml2NestTypeConverter.convert(ast_buffer.get_type_symbol())
        buffer_type.replace(".", "::")
        return buffer_type + " " + ast_buffer.get_symbol_name()

    @classmethod
    def print_buffer_declaration_header(cls, ast_buffer):
        """
        Prints the comment as stated over the buffer declaration.
        :param ast_buffer: a single buffer variable symbol.
        :type ast_buffer: VariableSymbol
        :return: the corresponding string representation
        :rtype: str
        """
        assert isinstance(ast_buffer, VariableSymbol), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of ast_buffer symbol provided (%s)!' % type(ast_buffer)
        return '//!< Buffer incoming ' + ast_buffer.get_type_symbol().get_symbol_name() + 's through delay, as sum'
