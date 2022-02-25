# -*- coding: utf-8 -*-
#
# python_standalone_printer.py
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

from pynestml.codegeneration.reference_converter import ReferenceConverter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_elif_clause import ASTElifClause
from pynestml.meta_model.ast_else_clause import ASTElseClause
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
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
from pynestml.meta_model.ast_neuron_or_synapse_body import ASTNeuronOrSynapseBody
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_output_block import ASTOutputBlock
from pynestml.meta_model.ast_parameter import ASTParameter
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_while_stmt import ASTWhileStmt
from pynestml.symbols.symbol import SymbolKind
from pynestml.codegeneration.printer import Printer
from pynestml.codegeneration.types_printer import TypesPrinter
from pynestml.codegeneration.expressions_printer import ExpressionsPrinter
from pynestml.symbols.variable_symbol import VariableSymbol, BlockType


class PythonStandalonePrinter(Printer):
    r"""
    This class contains all methods as required to transform

    Uses the composability-over-inheritance pattern to have the ability to swap out ExpressionPrinters.
    """

    def __init__(self,
                 reference_converter: ReferenceConverter,
                 types_printer: TypesPrinter,
                 expressions_printer: Printer):
        super().__init__(reference_converter=reference_converter,
                         types_printer=types_printer)
        self._expressions_printer = expressions_printer
        assert not isinstance(self._expressions_printer, PythonStandalonePrinter)

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
        if isinstance(node, ASTNeuronOrSynapseBody):
            ret = self.print_neuron_or_synapse_body(node)
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

    def print_simple_expression(self, node, prefix=""):
        return self.print_expression(node, prefix=prefix)

    def print_small_stmt(self, node, prefix=""):
        if node.is_assignment():
            return self.print_assignment(node.assignment, prefix=prefix)

    def print_stmt(self, node, prefix=""):
        if node.is_small_stmt:
            return self.print_small_stmt(node.small_stmt, prefix=prefix)

    def print_assignment(self, node, prefix=""):
        # type: (ASTAssignment) -> str
        symbol = node.get_scope().resolve_to_symbol(node.lhs.get_complete_name(), SymbolKind.VARIABLE)
        ret = self.print_origin(symbol) + self.reference_converter.name(symbol) + ' '
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

    def print_variable(self, node: ASTVariable) -> str:
        symbol = node.get_scope().resolve_to_symbol(node.lhs.get_complete_name(), SymbolKind.VARIABLE)
        ret = self.print_origin(symbol) + node.name
        for i in range(1, node.differential_order + 1):
            ret += "__d"
        return ret

    def print_comparison_operator(self, for_stmt):
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

    def print_step(self, for_stmt):
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

    def print_output_event(self, ast_body: ASTNeuronOrSynapseBody) -> str:
        """
        For the handed over neuron, print its defined output type.
        :param ast_body: a single neuron body
        :return: the corresponding representation of the event
        """
        assert (ast_body is not None and isinstance(ast_body, ASTNeuronOrSynapseBody)), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of body provided (%s)!' % type(ast_body)
        outputs = ast_body.get_output_blocks()
        if len(outputs) == 0:
            # no output port defined in the model: pretend dummy spike output port to obtain usable model
            return 'nest::SpikeEvent'

        output = outputs[0]
        if output.is_spike():
            return 'nest::SpikeEvent'

        if output.is_continuous():
            return 'nest::CurrentEvent'

        raise RuntimeError('Unexpected output type. Must be continuous or spike, is %s.' % str(output))

    def print_buffer_initialization(self, variable_symbol):
        """
        Prints the buffer initialization.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: a buffer initialization
        :rtype: str
        """
        return 'get_' + variable_symbol.get_symbol_name() + '().clear(); //includes resize'


    def print_function_declaration(self, ast_function):
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
        declaration += self.types_printer.convert(function_symbol.get_return_type()).replace('.', '::')
        declaration += ' '
        declaration += ast_function.get_name() + '('
        for typeSym in function_symbol.get_parameter_types():
            declaration += self.types_printer.convert(typeSym)
            if function_symbol.get_parameter_types().index(typeSym) < len(
                    function_symbol.get_parameter_types()) - 1:
                declaration += ', '
        declaration += ') const\n'
        return declaration

    def print_function_definition(self, ast_function, namespace):
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
        declaration += self.types_printer.convert(function_symbol.get_return_type()).replace('.', '::')
        declaration += ' '
        if namespace is not None:
            declaration += namespace + '::'
        declaration += ast_function.get_name() + '('
        for typeSym in function_symbol.get_parameter_types():
            # create the type name combination, e.g. double Tau
            declaration += self.types_printer.convert(typeSym) + ' ' + \
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
        if ast_buffer.is_spike_input_port() and ast_buffer.is_inhibitory() and ast_buffer.is_excitatory():
            return 'inline ' + self.types_printer.convert(ast_buffer.get_type_symbol()) + '&' + ' get_' \
                   + ast_buffer.get_symbol_name() + '() {' + \
                   '  return spike_inputs_[' + ast_buffer.get_symbol_name().upper() + ' - 1]; }'
        else:
            return self.print_buffer_getter(ast_buffer, True)

    def print_buffer_getter(self, ast_buffer, is_in_struct=False):
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
            declaration += self.types_printer.convert(ast_buffer.get_type_symbol())
            declaration += '> &'
        else:
            declaration += self.types_printer.convert(ast_buffer.get_type_symbol()) + '&'
        declaration += ' get_' + ast_buffer.get_symbol_name() + '() {'
        if is_in_struct:
            declaration += 'return ' + ast_buffer.get_symbol_name() + ';'
        else:
            declaration += 'return B_.get_' + ast_buffer.get_symbol_name() + '();'
        declaration += '}'
        return declaration

    def print_buffer_declaration_value(self, ast_buffer):
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
            return 'std::vector<double> ' + self.self.reference_converter.buffer_value(ast_buffer)
        else:
            return 'double ' + self.self.reference_converter.buffer_value(ast_buffer)

    def print_buffer_declaration(self, ast_buffer):
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
            buffer_type = 'std::vector< ' + self.types_printer.convert(ast_buffer.get_type_symbol()) + ' >'
        else:
            buffer_type = self.types_printer.convert(ast_buffer.get_type_symbol())
        buffer_type.replace(".", "::")
        return buffer_type + " " + ast_buffer.get_symbol_name()

    def print_buffer_declaration_header(self, ast_buffer):
        """
        Prints the comment as stated over the buffer declaration.
        :param ast_buffer: a single buffer variable symbol.
        :type ast_buffer: VariableSymbol
        :return: the corresponding string representation
        :rtype: str
        """
        assert isinstance(ast_buffer, VariableSymbol), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of ast_buffer symbol provided (%s)!' % type(ast_buffer)
        return '//!< Buffer for input (type: ' + ast_buffer.get_type_symbol().get_symbol_name() + ')'

    def print_vector_size_parameter(self, variable: VariableSymbol) -> str:
        """
        Prints NEST compatible vector size parameter
        :param variable: Vector variable
        :return: vector size parameter
        """
        vector_parameter = variable.get_vector_parameter()
        vector_parameter_var = ASTVariable(vector_parameter, scope=variable.get_corresponding_scope())
        symbol = vector_parameter_var.get_scope().resolve_to_symbol(vector_parameter_var.get_complete_name(),
                                                                    SymbolKind.VARIABLE)
        vector_param = ""
        if symbol is not None:
            # size parameter is a variable
            vector_param += self.print_origin(symbol) + vector_parameter
        else:
            # size parameter is an integer
            vector_param += vector_parameter

        return vector_param

    def print_vector_declaration(self, variable: VariableSymbol) -> str:
        """
        Prints the vector declaration
        :param variable: Vector variable
        :return: the corresponding vector declaration statement
        """
        assert isinstance(variable, VariableSymbol), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of variable symbol provided (%s)!' % type(variable)

        decl_str = self.print_origin(variable) + variable.get_symbol_name() + \
            ".resize(" + self.print_vector_size_parameter(variable) + ", " + \
            self.print_expression(variable.get_declaring_expression()) + \
            ");"
        return decl_str

    def print_expression(self, node: ASTExpressionNode, prefix: str = "") -> str:
        """
        Prints the handed over rhs to a nest readable format.
        :param node: a single meta_model node.
        :type node: ASTExpressionNode
        :return: the corresponding string representation
        """
        return self._expressions_printer.print_expression(node, prefix=prefix)

    def print_function_call(self, node: ASTFunctionCall) -> str:
        """
        Prints a single handed over function call.
        :param node: a single function call.
        :type node: ASTFunctionCall
        :return: the corresponding string representation.
        """
        return self._expressions_printer.print_function_call(node)

    def print_origin(self, variable_symbol, prefix='') -> str:
        return self.reference_converter.print_origin(variable_symbol)
