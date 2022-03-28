# -*- coding: utf-8 -*-
#
# nestml_printer.py
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

from pynestml.codegeneration.printers.printer import Printer
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
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock
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


class NESTMLPrinter(Printer):
    r"""
    This class can be used to print any ASTNode to NESTML syntax.
    """

    tab_size = 2  # type: int # the indentation level, change if required

    def __init__(self):
        self.indent = 0

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

        if isinstance(node, ASTSynapse):
            ret = self.print_synapse(node)

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

        if isinstance(node, ASTOnReceiveBlock):
            ret = self.print_on_receive_block(node)

        if isinstance(node, ASTVariable):
            ret = self.print_variable(node)

        if isinstance(node, ASTWhileStmt):
            ret = self.print_while_stmt(node)

        if isinstance(node, ASTStmt):
            ret = self.print_stmt(node)

        ret = filter_subsequent_whitespaces(ret)

        return ret

    def print_neuron(self, node: ASTNeuron) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        self.inc_indent()
        ret += 'neuron ' + node.get_name() + ':' + print_sl_comment(node.in_comment)
        ret += '\n' + self.print_node(node.get_body()) + 'end' + '\n'
        self.dec_indent()
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_synapse(self, node: ASTNeuron) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        self.inc_indent()
        ret += 'synapse ' + node.get_name() + ':' + print_sl_comment(node.in_comment)
        ret += '\n' + self.print_node(node.get_body()) + 'end' + '\n'
        self.dec_indent()
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_arithmetic_operator(celf, node: ASTArithmeticOperator) -> str:
        if node.is_times_op:
            return ' * '

        if node.is_div_op:
            return ' / '

        if node.is_modulo_op:
            return ' % '

        if node.is_plus_op:
            return ' + '

        if node.is_minus_op:
            return ' - '

        if node.is_pow_op:
            return ' ** '

        raise RuntimeError('(PyNestML.ArithmeticOperator.Print) Arithmetic operator not specified.')

    def print_assignment(self, node: ASTAssignment) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + self.print_node(node.lhs) + ' '
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
        ret += ' ' + self.print_node(node.rhs) + print_sl_comment(node.in_comment) + '\n'
        ret += print_ml_comments(node.post_comments, self.indent, True)

        return ret

    def print_bit_operator(self, node: ASTBitOperator) -> str:
        if node.is_bit_and:
            return ' & '

        if node.is_bit_or:
            return ' ^ '

        if node.is_bit_or:
            return ' | '

        if node.is_bit_shift_left:
            return ' << '

        if node.is_bit_shift_right:
            return ' >> '

        raise RuntimeError('(PyNestML.BitOperator.Print) Type of bit operator not specified!')

    def print_block(self, node: ASTBlock) -> str:
        ret = ''  # print_ml_comments(node.pre_comments, self.indent, False)
        self.inc_indent()
        for stmt in node.stmts:
            ret += self.print_node(stmt)

        self.dec_indent()
        # ret += print_ml_comments(node.post_comments, self.indent, True)

        return ret

    def print_block_with_variables(self, node: ASTBlockWithVariables) -> str:
        temp_indent = self.indent
        self.inc_indent()
        ret = print_ml_comments(node.pre_comments, temp_indent, False)
        ret += print_n_spaces(temp_indent)
        if node.is_state:
            ret += 'state'
        elif node.is_parameters:
            ret += 'parameters'
        else:
            assert node.is_internals
            ret += 'internals'
        ret += ':' + print_sl_comment(node.in_comment) + '\n'
        if node.get_declarations() is not None:
            for decl in node.get_declarations():
                ret += self.print_node(decl)
        ret += print_n_spaces(temp_indent) + 'end' + ('\n' if len(node.post_comments) else '')
        ret += print_ml_comments(node.post_comments, temp_indent, True)
        self.dec_indent()
        return ret

    def print_neuron_or_synapse_body(self, node: ASTNeuronOrSynapseBody) -> str:
        ret = ''
        for elem in node.body_elements:
            ret += self.print_node(elem)
            ret += '\n'
        return ret

    def print_comparison_operator(self, node: ASTComparisonOperator) -> str:
        if node.is_lt:
            return ' < '

        if node.is_le:
            return ' <= '

        if node.is_eq:
            return ' == '

        if node.is_ne:
            return ' != '

        if node.is_ne2:
            return ' <> '

        if node.is_ge:
            return ' >= '

        if node.is_gt:
            return ' > '

        raise RuntimeError('(PyNestML.ComparisonOperator.Print) Type of comparison operator not specified!')

    def print_compound_stmt(self, node: ASTCompoundStmt) -> str:
        if node.is_if_stmt():
            return self.print_node(node.get_if_stmt())

        if node.is_for_stmt():
            return self.print_node(node.get_for_stmt())

        if node.is_while_stmt():
            return self.print_node(node.get_while_stmt())

        raise RuntimeError('(PyNestML.CompoundStmt.Print) Type of compound statement not specified!')

    def print_data_type(self, node: ASTDataType) -> str:
        if node.is_void:
            return 'void'

        if node.is_string:
            return 'string'

        if node.is_boolean:
            return 'boolean'

        if node.is_integer:
            return 'integer'

        if node.is_real:
            return 'real'

        if node.is_unit_type():
            return self.print_node(node.get_unit_type())

        raise RuntimeError('Type of datatype not specified!')

    def print_declaration(self, node: ASTDeclaration) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent)
        if node.is_recordable:
            ret += 'recordable '
        if node.is_inline_expression:
            ret += 'inline '
        for var in node.get_variables():
            ret += self.print_node(var)
            if node.get_variables().index(var) < len(node.get_variables()) - 1:
                ret += ','
        ret += ' ' + self.print_node(node.get_data_type()) + ' '
        if node.has_size_parameter():
            ret += '[' + node.get_size_parameter() + '] '
        if node.has_expression():
            ret += '= ' + self.print_node(node.get_expression())
        if node.has_invariant():
            ret += ' [[' + self.print_node(node.get_invariant()) + ']]'
        ret += print_sl_comment(node.in_comment) + '\n'
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_elif_clause(self, node: ASTElifClause) -> str:
        return (print_n_spaces(self.indent) + 'elif ' + self.print_node(node.get_condition())
                + ':\n' + self.print_node(node.get_block()))

    def print_else_clause(self, node: ASTElseClause) -> str:
        return print_n_spaces(self.indent) + 'else:\n' + self.print_node(node.get_block())

    def print_equations_block(self, node: ASTEquationsBlock) -> str:
        temp_indent = self.indent
        self.inc_indent()
        ret = print_ml_comments(node.pre_comments, temp_indent, False)
        ret += print_n_spaces(temp_indent)
        ret += 'equations:' + print_sl_comment(node.in_comment) + '\n'
        for decl in node.get_declarations():
            ret += self.print_node(decl)
        self.dec_indent()
        ret += print_n_spaces(temp_indent) + 'end' + '\n'
        ret += print_ml_comments(node.post_comments, temp_indent, True)
        return ret

    def print_expression(self, node: ASTExpression) -> str:
        ret = ''
        if node.is_expression():
            if node.is_encapsulated:
                ret += '('
            if node.is_logical_not:
                ret += 'not '
            if node.is_unary_operator():
                ret += self.print_node(node.get_unary_operator())
            ret += self.print_node(node.get_expression())
            if node.is_encapsulated:
                ret += ')'
        elif node.is_compound_expression():
            ret += self.print_node(node.get_lhs())
            ret += self.print_node(node.get_binary_operator())
            ret += self.print_node(node.get_rhs())
        elif node.is_ternary_operator():
            ret += self.print_node(node.get_condition()) + '?' + self.print_node(
                node.get_if_true()) + ':' + self.print_node(node.get_if_not())
        return ret

    def print_for_stmt(self, node: ASTForStmt) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent)
        ret += ('for ' + node.get_variable() + ' in ' + self.print_node(node.get_start_from()) + '...'
                + self.print_node(node.get_end_at()) + ' step '
                + str(node.get_step()) + ':' + print_sl_comment(node.in_comment) + '\n')
        ret += self.print_node(node.get_block()) + print_n_spaces(self.indent) + 'end\n'
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_function(self, node: ASTFunction) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent)
        ret += 'function ' + node.get_name() + '('
        if node.has_parameters():
            for par in node.get_parameters():
                ret += self.print_node(par)
        ret += ')'
        if node.has_return_type():
            ret += ' ' + self.print_node(node.get_return_type())
        ret += ':' + print_sl_comment(node.in_comment) + '\n'
        ret += self.print_node(node.get_block()) + '\nend\n'
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_function_call(self, node: ASTFunctionCall) -> str:
        ret = str(node.get_name()) + '('
        for i in range(0, len(node.get_args())):
            ret += self.print_node(node.get_args()[i])
            if i < len(node.get_args()) - 1:  # in the case that it is not the last arg, print also a comma
                ret += ','
        ret += ')'
        return ret

    def print_if_clause(self, node: ASTIfClause) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent)
        ret += print_n_spaces(self.indent) + 'if ' + self.print_node(node.get_condition()) + ':'
        ret += print_sl_comment(node.in_comment) + '\n'
        ret += self.print_node(node.get_block())
        ret += print_ml_comments(node.post_comments, self.indent)
        return ret

    def print_if_stmt(self, node: ASTIfStmt) -> str:
        ret = self.print_node(node.get_if_clause())
        if node.get_elif_clauses() is not None:
            for clause in node.get_elif_clauses():
                ret += self.print_node(clause)
        if node.get_else_clause() is not None:
            ret += self.print_node(node.get_else_clause())
        ret += print_n_spaces(self.indent) + 'end\n'
        return ret

    def print_input_block(self, node: ASTInputBlock) -> str:
        temp_indent = self.indent
        self.inc_indent()
        ret = print_ml_comments(node.pre_comments, temp_indent, False)
        ret += print_n_spaces(temp_indent) + 'input:\n'
        if node.get_input_ports() is not None:
            for inputDef in node.get_input_ports():
                ret += self.print_node(inputDef)
        ret += print_n_spaces(temp_indent) + 'end\n'
        ret += print_ml_comments(node.post_comments, temp_indent, True)
        self.dec_indent()
        return ret

    def print_input_port(self, node: ASTInputPort) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + node.get_name()
        if node.has_datatype():
            ret += ' ' + self.print_node(node.get_datatype()) + ' '
        if node.has_index_parameter():
            ret += '[' + node.get_index_parameter() + ']'
        ret += '<-'
        if node.has_input_qualifiers():
            for qual in node.get_input_qualifiers():
                ret += self.print_node(qual) + ' '
        if node.is_spike():
            ret += 'spike'
        else:
            ret += 'current'
        ret += print_sl_comment(node.in_comment) + '\n'
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_input_qualifier(self, node: ASTInputQualifier) -> str:
        if node.is_inhibitory:
            return 'inhibitory'
        if node.is_excitatory:
            return 'excitatory'
        return ''

    def print_logical_operator(self, node: ASTLogicalOperator) -> str:
        if node.is_logical_and:
            return ' and '

        if node.is_logical_or:
            return ' or '

        raise Exception("Unknown logical operator")

    def print_compilation_unit(self, node: ASTNestMLCompilationUnit) -> str:
        ret = ''
        if node.get_neuron_list() is not None:
            for neuron in node.get_neuron_list():
                ret += self.print_node(neuron) + '\n'
        return ret

    def print_ode_equation(self, node: ASTOdeEquation) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += (print_n_spaces(self.indent) + self.print_node(node.get_lhs())
                + '=' + self.print_node(node.get_rhs())
                + print_sl_comment(node.in_comment) + '\n')
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_inline_expression(self, node: ASTInlineExpression) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        if node.is_recordable:
            ret += 'recordable'
        ret += (print_n_spaces(self.indent) + 'inline '
                + str(node.get_variable_name()) + ' ' + self.print_node(node.get_data_type())
                + ' = ' + self.print_node(node.get_expression()) + print_sl_comment(node.in_comment) + '\n')
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_kernel(self, node: ASTKernel) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent)
        ret += 'kernel '
        for var, expr in zip(node.get_variables(), node.get_expressions()):
            ret += self.print_node(var)
            ret += ' = '
            ret += self.print_node(expr)
            ret += ', '
        ret = ret[:-2]
        ret += print_sl_comment(node.in_comment) + '\n'
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_output_block(self, node: ASTOutputBlock) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + 'output: ' + ('spike' if node.is_spike() else 'current')
        ret += print_sl_comment(node.in_comment)
        ret += '\n'
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_parameter(self, node: ASTParameter) -> str:
        return node.get_name() + ' ' + self.print_node(node.get_data_type())

    def print_return_stmt(self, node: ASTReturnStmt):
        ret = print_n_spaces(self.indent)
        ret += 'return ' + (self.print_node(node.get_expression()) if node.has_expression() else '')
        return ret

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        if node.is_function_call():
            return self.print_node(node.function_call)

        if node.is_boolean_true:
            return 'true'

        if node.is_boolean_false:
            return 'false'

        if node.is_inf_literal:
            return 'inf'

        if node.is_numeric_literal():
            if node.variable is not None:
                return str(node.numeric_literal) + self.print_node(node.variable)

            return str(node.numeric_literal)

        if node.is_variable():
            return self.print_node(node.variable)

        if node.is_string():
            return node.get_string()

        raise RuntimeError('Simple rhs at %s not specified!' % str(node.get_source_position()))

    def print_small_stmt(self, node: ASTSmallStmt) -> str:
        if node.is_assignment():
            ret = self.print_node(node.get_assignment())
        elif node.is_function_call():
            # the problem with the function is that it is used inside an expression or as a simple statement
            # we therefore have to include the right printing here
            ret = print_ml_comments(node.pre_comments, self.indent, False)
            ret += print_n_spaces(self.indent) + self.print_node(node.get_function_call())
            ret += print_sl_comment(node.in_comment) + '\n'
            ret += print_ml_comments(node.post_comments, self.indent, True)
        elif node.is_declaration():
            ret = self.print_node(node.get_declaration())
        else:
            ret = self.print_node(node.get_return_stmt())
        return ret

    def print_stmt(self, node: ASTStmt):
        if node.is_small_stmt():
            return self.print_node(node.small_stmt)

        return self.print_node(node.compound_stmt)

    def print_unary_operator(self, node: ASTUnaryOperator) -> str:
        if node.is_unary_plus:
            return '+'

        if node.is_unary_minus:
            return '-'

        if node.is_unary_tilde:
            return '~'

        raise RuntimeError('Type of unary operator not specified!')

    def print_unit_type(self, node: ASTUnitType) -> str:
        if node.is_encapsulated:
            return '(' + self.print_node(node.compound_unit) + ')'

        if node.is_pow:
            return self.print_node(node.base) + '**' + str(node.exponent)

        if node.is_arithmetic_expression():
            t_lhs = (
                self.print_node(node.get_lhs()) if isinstance(node.get_lhs(), ASTUnitType) else str(node.get_lhs()))
            if node.is_times:
                return t_lhs + '*' + self.print_node(node.get_rhs())
            else:
                return t_lhs + '/' + self.print_node(node.get_rhs())

        return node.unit

    def print_on_receive_block(self, node: ASTOnReceiveBlock) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + 'onReceive(' + node.port_name + '):' + print_sl_comment(node.in_comment) + '\n'
        ret += (self.print_node(node.get_block()) + print_n_spaces(self.indent) + 'end\n')
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_update_block(self, node: ASTUpdateBlock):
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + 'update:' + print_sl_comment(node.in_comment) + '\n'
        ret += (self.print_node(node.get_block()) + print_n_spaces(self.indent) + 'end\n')
        ret += print_ml_comments(node.post_comments, self.indent, True)
        return ret

    def print_variable(self, node: ASTVariable):
        ret = node.name
        for i in range(1, node.differential_order + 1):
            ret += "'"
        return ret

    def print_while_stmt(self, node: ASTWhileStmt) -> str:
        temp_indent = self.indent
        self.inc_indent()
        ret = print_ml_comments(node.pre_comments, temp_indent, False)
        ret += (print_n_spaces(temp_indent) + 'while ' + self.print_node(node.get_condition())
                + ':' + print_sl_comment(node.in_comment) + '\n')
        ret += self.print_node(node.get_block()) + print_n_spaces(temp_indent) + 'end\n'
        self.dec_indent()
        ret += print_ml_comments(node.post_comments, temp_indent, True)
        return ret

    def inc_indent(self):
        self.indent += self.tab_size

    def dec_indent(self):
        self.indent -= self.tab_size


def print_n_spaces(n) -> str:
    return ' ' * n


def print_ml_comments(comments, indent=0, newline=False) -> str:
    if comments is None or len(list(comments)) == 0:
        return ''
    ret = ''
    for comment in comments:
        if "\"\"\"" in comment:
            return comment + '\n'
        for c_line in comment.splitlines(True):
            if c_line == '\n':
                ret += print_n_spaces(indent) + '#' + '\n'
                continue
            elif c_line.lstrip() == '':
                continue
            ret += print_n_spaces(indent)
            if c_line[len(c_line) - len(c_line.lstrip())] != '#':
                ret += '#'
            ret += c_line + '\n'
        if len(comment.splitlines(True)) > 1:
            ret += print_n_spaces(indent)
    if len(comments) > 0 and newline:
        ret += '\n'

    return ret


def print_sl_comment(comment) -> str:
    if comment is not None:
        return ' # ' + comment.lstrip()

    return ''


def filter_subsequent_whitespaces(string: str) -> str:
    """
    This filter reduces more than one newline to exactly one, e.g.:
        l1
        \n
        \n
        \n
        l2
    is filtered to
        l1
        \n
        l2
    """
    s_lines = string.splitlines(True)
    for index, item in enumerate(s_lines, start=0):
        if index < len(s_lines) - 1 and item == '\n' and s_lines[index + 1] == '\n':
            del s_lines[index + 1]
    ret = ''.join(s_lines)
    return ret
