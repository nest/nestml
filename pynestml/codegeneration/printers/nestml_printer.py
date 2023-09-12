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

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.codegeneration.printers.model_printer import ModelPrinter
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
from pynestml.meta_model.ast_namespace_decorator import ASTNamespaceDecorator
from pynestml.meta_model.ast_nestml_compilation_unit import ASTNestMLCompilationUnit
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_node import ASTNode
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


class NESTMLPrinter(ModelPrinter):
    r"""
    This class can be used to print any ASTNode to NESTML syntax.
    """

    tab_size: int = 4    # the indentation level, change if required

    def __init__(self):
        self.indent = 0

    def print_neuron(self, node: ASTNeuron) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        self.inc_indent()
        ret += "neuron " + node.get_name() + ":" + print_sl_comment(node.in_comment)
        ret += "\n" + self.print(node.get_body())
        self.dec_indent()
        return ret

    def print_synapse(self, node: ASTSynapse) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        self.inc_indent()
        ret += "synapse " + node.get_name() + ":" + print_sl_comment(node.in_comment)
        ret += "\n" + self.print(node.get_body()) + "\n"
        self.dec_indent()
        return ret

    def print_arithmetic_operator(celf, node: ASTArithmeticOperator) -> str:
        if node.is_times_op:
            return " * "

        if node.is_div_op:
            return " / "

        if node.is_modulo_op:
            return " % "

        if node.is_plus_op:
            return " + "

        if node.is_minus_op:
            return " - "

        if node.is_pow_op:
            return " ** "

        raise RuntimeError("(PyNestML.ArithmeticOperator.Print) Arithmetic operator not specified.")

    def print_assignment(self, node: ASTAssignment) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + self.print(node.lhs) + " "
        if node.is_compound_quotient:
            ret += "/="
        elif node.is_compound_product:
            ret += "*="
        elif node.is_compound_minus:
            ret += "-="
        elif node.is_compound_sum:
            ret += "+="
        else:
            ret += "="
        ret += " " + self.print(node.rhs) + print_sl_comment(node.in_comment) + "\n"

        return ret

    def print_bit_operator(self, node: ASTBitOperator) -> str:
        if node.is_bit_and:
            return " & "

        if node.is_bit_or:
            return " ^ "

        if node.is_bit_or:
            return " | "

        if node.is_bit_shift_left:
            return " << "

        if node.is_bit_shift_right:
            return " >> "

        raise RuntimeError("Unknown bit operator")

    def print_block(self, node: ASTBlock) -> str:
        ret = ""
        self.inc_indent()
        for stmt in node.stmts:
            ret += self.print(stmt)

        self.dec_indent()

        return ret

    def print_block_with_variables(self, node: ASTBlockWithVariables) -> str:
        temp_indent = self.indent
        self.inc_indent()
        ret = print_ml_comments(node.pre_comments, temp_indent, False)
        ret += print_n_spaces(temp_indent)
        if node.is_state:
            ret += "state"
        elif node.is_parameters:
            ret += "parameters"
        else:
            assert node.is_internals
            ret += "internals"
        ret += ":" + print_sl_comment(node.in_comment) + "\n"
        if node.get_declarations() is not None:
            for decl in node.get_declarations():
                ret += self.print(decl)
        self.dec_indent()
        return ret

    def print_neuron_or_synapse_body(self, node: ASTNeuronOrSynapseBody) -> str:
        ret = ""
        for elem in node.body_elements:
            ret += self.print(elem)
        return ret

    def print_comparison_operator(self, node: ASTComparisonOperator) -> str:
        if node.is_lt:
            return " < "

        if node.is_le:
            return " <= "

        if node.is_eq:
            return " == "

        if node.is_ne:
            return " != "

        if node.is_ne2:
            return " <> "

        if node.is_ge:
            return " >= "

        if node.is_gt:
            return " > "

        raise RuntimeError("(PyNestML.ComparisonOperator.Print) Type of comparison operator not specified!")

    def print_compound_stmt(self, node: ASTCompoundStmt) -> str:
        if node.is_if_stmt():
            return self.print(node.get_if_stmt())

        if node.is_for_stmt():
            return self.print(node.get_for_stmt())

        if node.is_while_stmt():
            return self.print(node.get_while_stmt())

        raise RuntimeError("(PyNestML.CompoundStmt.Print) Type of compound statement not specified!")

    def print_data_type(self, node: ASTDataType) -> str:
        if node.is_void:
            return "void"

        if node.is_string:
            return "string"

        if node.is_boolean:
            return "boolean"

        if node.is_integer:
            return "integer"

        if node.is_real:
            return "real"

        if node.is_unit_type():
            return self.print(node.get_unit_type())

        raise RuntimeError("Type of datatype not specified!")

    def print_declaration(self, node: ASTDeclaration) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent)
        if node.is_recordable:
            ret += "recordable "
        if node.is_inline_expression:
            ret += "inline "
        for var in node.get_variables():
            ret += self.print(var)
            if node.get_variables().index(var) < len(node.get_variables()) - 1:
                ret += ","
        ret += " " + self.print(node.get_data_type()) + " "
        if node.has_size_parameter():
            ret += "[" + self.print(node.get_size_parameter()) + "] "
        if node.has_expression():
            ret += "= " + self.print(node.get_expression())
        if node.has_invariant():
            ret += " [[" + self.print(node.get_invariant()) + "]]"
        for decorator in node.get_decorators():
            if isinstance(decorator, ASTNamespaceDecorator):
                ret += " @" + str(decorator.namespace) + "::" + str(decorator.name)
            else:
                ret += " @" + str(decorator)
        ret += print_sl_comment(node.in_comment) + "\n"
        return ret

    def print_elif_clause(self, node: ASTElifClause) -> str:
        return (print_n_spaces(self.indent) + "elif " + self.print(node.get_condition())
                + ":\n" + self.print(node.get_block()))

    def print_else_clause(self, node: ASTElseClause) -> str:
        return print_n_spaces(self.indent) + "else:\n" + self.print(node.get_block())

    def print_equations_block(self, node: ASTEquationsBlock) -> str:
        temp_indent = self.indent
        self.inc_indent()
        ret = print_ml_comments(node.pre_comments, temp_indent, False)
        ret += print_n_spaces(temp_indent)
        ret += "equations:" + print_sl_comment(node.in_comment) + "\n"
        for decl in node.get_declarations():
            ret += self.print(decl)
        self.dec_indent()
        return ret

    def print_expression(self, node: ASTExpression) -> str:
        ret = ""
        if node.is_expression():
            if node.is_encapsulated:
                ret += "("
            if node.is_logical_not:
                ret += "not "
            if node.is_unary_operator():
                ret += self.print(node.get_unary_operator())
            ret += self.print(node.get_expression())
            if node.is_encapsulated:
                ret += ")"
        elif node.is_compound_expression():
            ret += self.print(node.get_lhs())
            ret += self.print(node.get_binary_operator())
            ret += self.print(node.get_rhs())
        elif node.is_ternary_operator():
            ret += self.print(node.get_condition()) + "?" + self.print(
                node.get_if_true()) + ":" + self.print(node.get_if_not())
        return ret

    def print_for_stmt(self, node: ASTForStmt) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent)
        ret += ("for " + node.get_variable() + " in " + self.print(node.get_start_from()) + "..."
                + self.print(node.get_end_at()) + " step "
                + str(node.get_step()) + ":" + print_sl_comment(node.in_comment) + "\n")
        ret += self.print(node.get_block())
        return ret

    def print_function(self, node: ASTFunction) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent)
        ret += "function " + node.get_name() + "("
        if node.has_parameters():
            for par in node.get_parameters():
                ret += self.print(par)
        ret += ")"
        if node.has_return_type():
            ret += " " + self.print(node.get_return_type())
        ret += ":" + print_sl_comment(node.in_comment) + "\n"
        ret += self.print(node.get_block()) + "\n"
        return ret

    def print_function_call(self, node: ASTFunctionCall) -> str:
        ret = str(node.get_name()) + "("
        for i in range(0, len(node.get_args())):
            ret += self.print(node.get_args()[i])
            if i < len(node.get_args()) - 1:  # in the case that it is not the last arg, print also a comma
                ret += ","
        ret += ")"
        return ret

    def print_if_clause(self, node: ASTIfClause) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent)
        ret += print_n_spaces(self.indent) + "if " + self.print(node.get_condition()) + ":"
        ret += print_sl_comment(node.in_comment) + "\n"
        ret += self.print(node.get_block())
        return ret

    def print_if_stmt(self, node: ASTIfStmt) -> str:
        ret = self.print(node.get_if_clause())
        if node.get_elif_clauses() is not None:
            for clause in node.get_elif_clauses():
                ret += self.print(clause)
        if node.get_else_clause() is not None:
            ret += self.print(node.get_else_clause())
        ret += print_n_spaces(self.indent) + "\n"
        return ret

    def print_input_block(self, node: ASTInputBlock) -> str:
        temp_indent = self.indent
        self.inc_indent()
        ret = print_ml_comments(node.pre_comments, temp_indent, False)
        ret += print_n_spaces(temp_indent) + "input:\n"
        if node.get_input_ports() is not None:
            for inputDef in node.get_input_ports():
                ret += self.print(inputDef)
        self.dec_indent()
        return ret

    def print_input_port(self, node: ASTInputPort) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + node.get_name()
        if node.has_datatype():
            ret += " " + self.print(node.get_datatype()) + " "
        if node.has_size_parameter():
            ret += "[" + self.print(node.get_size_parameter()) + "]"
        ret += "<- "
        if node.has_input_qualifiers():
            for qual in node.get_input_qualifiers():
                ret += self.print(qual) + " "
        if node.is_spike():
            ret += "spike"
        else:
            ret += "continuous"
        ret += print_sl_comment(node.in_comment) + "\n"
        return ret

    def print_input_qualifier(self, node: ASTInputQualifier) -> str:
        if node.is_inhibitory:
            return "inhibitory"
        if node.is_excitatory:
            return "excitatory"
        return ""

    def print_logical_operator(self, node: ASTLogicalOperator) -> str:
        if node.is_logical_and:
            return " and "

        if node.is_logical_or:
            return " or "

        raise Exception("Unknown logical operator")

    def print_compilation_unit(self, node: ASTNestMLCompilationUnit) -> str:
        ret = ""
        if node.get_neuron_list() is not None:
            for neuron in node.get_neuron_list():
                ret += self.print(neuron)

        if node.get_synapse_list() is not None:
            for synapse in node.get_synapse_list():
                ret += self.print(synapse)

        return ret

    def print_ode_equation(self, node: ASTOdeEquation) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += (print_n_spaces(self.indent) + self.print(node.get_lhs())
                + " = " + self.print(node.get_rhs())
                + print_sl_comment(node.in_comment) + "\n")
        return ret

    def print_inline_expression(self, node: ASTInlineExpression) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent)
        if node.is_recordable:
            ret += "recordable "
        ret += ("inline "
                + str(node.get_variable_name()) + " " + self.print(node.get_data_type())
                + " = " + self.print(node.get_expression()) + print_sl_comment(node.in_comment) + "\n")
        return ret

    def print_kernel(self, node: ASTKernel) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent)
        ret += "kernel "
        for var, expr in zip(node.get_variables(), node.get_expressions()):
            ret += self.print(var)
            ret += " = "
            ret += self.print(expr)
            ret += ", "
        ret = ret[:-2]
        ret += print_sl_comment(node.in_comment) + "\n"
        return ret

    def print_output_block(self, node: ASTOutputBlock) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + "output:\n"
        ret += print_n_spaces(self.indent + 4)
        ret += "spike" if node.is_spike() else "continuous"
        ret += print_sl_comment(node.in_comment)
        ret += "\n"
        return ret

    def print_parameter(self, node: ASTParameter) -> str:
        return node.get_name() + " " + self.print(node.get_data_type())

    def print_return_stmt(self, node: ASTReturnStmt):
        ret = print_n_spaces(self.indent)
        ret += "return " + (self.print(node.get_expression()) if node.has_expression() else "")
        return ret

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        if node.is_function_call():
            return self.print(node.function_call)

        if node.is_boolean_true:
            return "true"

        if node.is_boolean_false:
            return "false"

        if node.is_inf_literal:
            return "inf"

        if node.is_numeric_literal():
            if node.variable is not None:
                return str(node.numeric_literal) + self.print(node.variable)

            return str(node.numeric_literal)

        if node.is_variable():
            return self.print_variable(node.get_variable())

        if node.is_string():
            return node.get_string()

        raise RuntimeError("Simple rhs at %s not specified!" % str(node.get_source_position()))

    def print_small_stmt(self, node: ASTSmallStmt) -> str:
        if node.is_assignment():
            ret = self.print(node.get_assignment())
        elif node.is_function_call():
            # the problem with the function is that it is used inside an expression or as a simple statement
            # we therefore have to include the right printing here
            ret = print_ml_comments(node.pre_comments, self.indent, False)
            ret += print_n_spaces(self.indent) + self.print(node.get_function_call())
            ret += print_sl_comment(node.in_comment) + "\n"
        elif node.is_declaration():
            ret = self.print(node.get_declaration())
        else:
            ret = self.print(node.get_return_stmt())
        return ret

    def print_stmt(self, node: ASTStmt):
        if node.is_small_stmt():
            return self.print(node.small_stmt)

        return self.print(node.compound_stmt)

    def print_unary_operator(self, node: ASTUnaryOperator) -> str:
        if node.is_unary_plus:
            return "+"

        if node.is_unary_minus:
            return "-"

        if node.is_unary_tilde:
            return "~"

        raise RuntimeError("Type of unary operator not specified!")

    def print_unit_type(self, node: ASTUnitType) -> str:
        if node.is_encapsulated:
            return "(" + self.print(node.compound_unit) + ")"

        if node.is_pow:
            return self.print(node.base) + "**" + str(node.exponent)

        if node.is_arithmetic_expression():
            t_lhs = (
                self.print(node.get_lhs()) if isinstance(node.get_lhs(), ASTUnitType) else str(node.get_lhs()))
            if node.is_times:
                return t_lhs + "*" + self.print(node.get_rhs())
            else:
                return t_lhs + "/" + self.print(node.get_rhs())

        return node.unit

    def print_on_receive_block(self, node: ASTOnReceiveBlock) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + "onReceive(" + node.port_name + "):" + print_sl_comment(node.in_comment) + "\n"
        ret += (self.print(node.get_block()) + print_n_spaces(self.indent) + "\n")
        return ret

    def print_update_block(self, node: ASTUpdateBlock):
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + "update:" + print_sl_comment(node.in_comment) + "\n"
        ret += self.print(node.get_block())
        return ret

    def print_variable(self, node: ASTVariable):
        ret = node.name

        if node.get_vector_parameter():
            ret += "[" + self.print(node.get_vector_parameter()) + "]"

        for i in range(1, node.differential_order + 1):
            ret += "'"

        return ret

    def print_while_stmt(self, node: ASTWhileStmt) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += (print_n_spaces(self.indent) + "while " + self.print(node.get_condition())
                + ":" + print_sl_comment(node.in_comment) + "\n")
        ret += self.print(node.get_block())
        return ret

    def inc_indent(self):
        self.indent += self.tab_size

    def dec_indent(self):
        self.indent -= self.tab_size


def print_n_spaces(n) -> str:
    return " " * n


def print_ml_comments(comments, indent=0, newline=False) -> str:
    if comments is None or len(list(comments)) == 0:
        return ""
    ret = ""
    for comment in comments:
        if "\"\"\"" in comment:
            return comment + "\n"
        for c_line in comment.splitlines(True):
            if c_line == "\n":
                ret += print_n_spaces(indent) + "#" + "\n"
                continue
            elif c_line.lstrip() == "":
                continue
            ret += print_n_spaces(indent)
            if c_line[len(c_line) - len(c_line.lstrip())] != "#":
                ret += "#"
            ret += c_line + "\n"
        if len(comment.splitlines(True)) > 1:
            ret += print_n_spaces(indent)
    if len(comments) > 0 and newline:
        ret += "\n"

    return ret


def print_sl_comment(comment) -> str:
    if comment is not None:
        return " # " + comment.lstrip()

    return ""
