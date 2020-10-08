# -*- coding: utf-8 -*-
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
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_body import ASTBody
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_elif_clause import ASTElifClause
from pynestml.meta_model.ast_else_clause import ASTElseClause
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_for_stmt import ASTForStmt
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_if_clause import ASTIfClause
from pynestml.meta_model.ast_if_stmt import ASTIfStmt
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_input_qualifier import ASTInputQualifier
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_nestml_compilation_unit import ASTNestMLCompilationUnit
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_output_block import ASTOutputBlock
from pynestml.meta_model.ast_parameter import ASTParameter
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_while_stmt import ASTWhileStmt


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

    def print_node(self, node):
        ret = ''
        if isinstance(node, ASTArithmeticOperator):
            ret = self.print_arithmetic_operator(node)
        if isinstance(node, ASTAssignment):
            ret = self.print_assignment(node)
        if isinstance(node, ASTBitOperator):
            ret = self.print_bit_operator(node)
        if isinstance(node, ASTBlock):
            ret = self.print_block(node)
        if isinstance(node, ASTBlockWithVariables):
            ret = self.print_block_with_variables(node)
        if isinstance(node, ASTBody):
            ret = self.print_body(node)
        if isinstance(node, ASTComparisonOperator):
            ret = self.print_comparison_operator(node)
        if isinstance(node, ASTCompoundStmt):
            ret = self.print_compound_stmt(node)
        if isinstance(node, ASTDataType):
            ret = self.print_data_type(node)
        if isinstance(node, ASTDeclaration):
            ret = self.print_declaration(node)
        if isinstance(node, ASTElifClause):
            ret = self.print_elif_clause(node)
        if isinstance(node, ASTElseClause):
            ret = self.print_else_clause(node)
        if isinstance(node, ASTEquationsBlock):
            ret = self.print_equations_block(node)
        if isinstance(node, ASTExpression):
            ret = self.print_expression(node)
        if isinstance(node, ASTForStmt):
            ret = self.print_for_stmt(node)
        if isinstance(node, ASTFunction):
            ret = self.print_function(node)
        if isinstance(node, ASTFunctionCall):
            ret = self.print_function_call(node)
        if isinstance(node, ASTIfClause):
            ret = self.print_if_clause(node)
        if isinstance(node, ASTIfStmt):
            ret = self.print_if_stmt(node)
        if isinstance(node, ASTInputBlock):
            ret = self.print_input_block(node)
        if isinstance(node, ASTInputPort):
            ret = self.print_input_port(node)
        if isinstance(node, ASTInputQualifier):
            ret = self.print_input_qualifier(node)
        if isinstance(node, ASTLogicalOperator):
            ret = self.print_logical_operator(node)
        if isinstance(node, ASTNestMLCompilationUnit):
            ret = self.print_compilation_unit(node)
        if isinstance(node, ASTNeuron):
            ret = self.print_neuron(node)
        if isinstance(node, ASTOdeEquation):
            ret = self.print_ode_equation(node)
        if isinstance(node, ASTInlineExpression):
            ret = self.print_inline_expression(node)
        if isinstance(node, ASTKernel):
            ret = self.print_kernel(node)
        if isinstance(node, ASTOutputBlock):
            ret = self.print_output_block(node)
        if isinstance(node, ASTParameter):
            ret = self.print_parameter(node)
        if isinstance(node, ASTReturnStmt):
            ret = self.print_return_stmt(node)
        if isinstance(node, ASTSimpleExpression):
            ret = self.print_simple_expression(node)
        if isinstance(node, ASTSmallStmt):
            ret = self.print_small_stmt(node)
        if isinstance(node, ASTUnaryOperator):
            ret = self.print_unary_operator(node)
        if isinstance(node, ASTUnitType):
            ret = self.print_unit_type(node)
        if isinstance(node, ASTUpdateBlock):
            ret = self.print_update_block(node)
        if isinstance(node, ASTVariable):
            ret = self.print_variable(node)
        if isinstance(node, ASTWhileStmt):
            ret = self.print_while_stmt(node)
        if isinstance(node, ASTStmt):
            ret = self.print_stmt(node)
        return ret

    def print_assignment(self, node, prefix=""):
        # type: (ASTAssignment) -> str
        ret = self.print_node(node.lhs) + ' '
        if node.is_compound_quotient:
            ret += '/='
        elif node.is_compound_product:
            ret += '*='
        elif node.is_compound_minus:
            ret += '-='
        elif node.is_compound_sum:
            ret += '+='
        else:
            ret += '='
        ret += ' ' + self.print_node(node.rhs)
        return ret

    def print_variable(self, node):
        # type: (ASTVariable) -> str
        ret = node.name
        for i in range(1, node.differential_order + 1):
            ret += "__d"
        return ret

    def print_expression(self, node, prefix=""):
        # type: (ASTExpressionNode) -> str
        """
        Pretty Prints the handed over rhs to a nest readable format.
        :param node: a single meta_model node.
        :type node: ASTExpressionNode
        :return: the corresponding string representation
        :rtype: str
        """
        return self.expression_pretty_printer.print_expression(node, prefix=prefix)

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
    def print_origin(cls, variable_symbol, prefix=''):
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
            return prefix + 'S_.'

        if variable_symbol.block_type == BlockType.INITIAL_VALUES:
            return prefix + 'S_.'

        if variable_symbol.block_type == BlockType.EQUATION:
            return prefix + 'S_.'

        if variable_symbol.block_type == BlockType.PARAMETERS:
            return prefix + 'P_.'

        if variable_symbol.block_type == BlockType.INTERNALS:
            return prefix + 'V_.'

        if variable_symbol.block_type == BlockType.INPUT_BUFFER_CURRENT:
            return prefix + 'B_.'

        if variable_symbol.block_type == BlockType.INPUT_BUFFER_SPIKE:
            return prefix + 'B_.'

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
            # no output port defined in the model: pretend dummy spike output port to obtain usable model
            return 'nest::SpikeEvent'

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
