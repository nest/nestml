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

from typing import Optional, Union

from pynestml.codegeneration.printers import nest_variable_printer
from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.model_printer import ModelPrinter
from pynestml.codegeneration.printers.nest_variable_printer import NESTVariablePrinter
from pynestml.codegeneration.printers.nestml_expression_printer import NESTMLExpressionPrinter
from pynestml.codegeneration.printers.nestml_function_call_printer import NESTMLFunctionCallPrinter
from pynestml.codegeneration.printers.nestml_simple_expression_printer import NESTMLSimpleExpressionPrinter
from pynestml.codegeneration.printers.nestml_variable_printer import NESTMLVariablePrinter
from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
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
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_input_qualifier import ASTInputQualifier
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_model_body import ASTModelBody
from pynestml.meta_model.ast_namespace_decorator import ASTNamespaceDecorator
from pynestml.meta_model.ast_nestml_compilation_unit import ASTNestMLCompilationUnit
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_on_condition_block import ASTOnConditionBlock
from pynestml.meta_model.ast_output_block import ASTOutputBlock
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock
from pynestml.meta_model.ast_parameter import ASTParameter
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_stmts_body import ASTStmtsBody
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

        self._expression_printer = NESTMLExpressionPrinter(simple_expression_printer=None)
        self._constant_printer = ConstantPrinter()
        self._function_call_printer = NESTMLFunctionCallPrinter(expression_printer=self._expression_printer)
        self._variable_printer = NESTMLVariablePrinter(expression_printer=self._expression_printer)
        self._simple_expression_printer = NESTMLSimpleExpressionPrinter(variable_printer=self._variable_printer, function_call_printer=self._function_call_printer, constant_printer=self._constant_printer)
        self._expression_printer._simple_expression_printer = self._simple_expression_printer

    def print_model(self, node: ASTModel) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += "model " + node.get_name() + ":" + print_sl_comment(node.in_comment)
        ret += "\n" + self.print(node.get_body())
        return ret

    def print_constant(self, const: Union[str, float, int]) -> str:
        return self._constant_printer.print_constant(const)

    def print_function_call(self, node: ASTFunctionCall) -> str:
        return self._function_call_printer.print_function_call(node)

    def print_variable(self, node: ASTVariable) -> str:
        return self._variable_printer.print_variable(node)

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        return self._simple_expression_printer.print_simple_expression(node)

    def print_expression(self, node: ASTExpression) -> str:
        return self._expression_printer.print_expression(node)

    def print_arithmetic_operator(self, node: ASTArithmeticOperator) -> str:
        return self._expression_printer.print_arithmetic_operator(node)

    def print_unary_operator(self, node: ASTUnaryOperator) -> str:
        return self._expression_printer.print_unary_operator(node)

    def print_comparison_operator(self, node: ASTComparisonOperator) -> str:
        return self._expression_printer.print_comparison_operator(node)

    def print_logical_operator(self, node: ASTLogicalOperator) -> str:
        return self._expression_printer.print_logical_operator(node)

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

    def print_stmts_body(self, node: ASTStmtsBody) -> str:
        ret = ""
        for stmt in node.stmts:
            ret += self.print(stmt)

        return ret

    def print_block_with_variables(self, node: ASTBlockWithVariables) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent)
        if node.is_state:
            ret += "state"
        elif node.is_parameters:
            ret += "parameters"
        else:
            assert node.is_internals
            ret += "internals"
        ret += ":" + print_sl_comment(node.in_comment) + "\n"
        if node.get_declarations() is not None:
            self.inc_indent()
            for decl in node.get_declarations():
                ret += self.print(decl)
            self.dec_indent()

        return ret

    def print_model_body(self, node: ASTModelBody) -> str:
        self.inc_indent()
        ret = ""
        for elem in node.body_elements:
            ret += self.print(elem)
        self.dec_indent()
        return ret

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
        ret = print_n_spaces(self.indent) + "elif " + self.print(node.get_condition()) + ":\n"
        self.inc_indent()
        ret += self.print(node.get_stmts_body())
        self.dec_indent()

        return ret

    def print_else_clause(self, node: ASTElseClause) -> str:
        ret = print_n_spaces(self.indent) + "else:\n"
        self.inc_indent()
        ret += self.print(node.get_stmts_body())
        self.dec_indent()

        return ret

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

    def print_for_stmt(self, node: ASTForStmt) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent)
        ret += ("for " + node.get_variable() + " in " + self.print(node.get_start_from()) + "..."
                + self.print(node.get_end_at()) + " step "
                + str(node.get_step()) + ":" + print_sl_comment(node.in_comment) + "\n")
        self.inc_indent()
        ret += self.print(node.get_stmts_body())
        self.dec_indent()
        return ret

    def print_function_call(self, node: ASTFunctionCall) -> str:
        return self._function_call_printer.print_function_call(node)

    def print_function(self, node: ASTFunction) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent)
        ret += print_n_spaces(self.indent) + "function " + node.get_name() + "("
        if node.has_parameters():
            for par in node.get_parameters():
                ret += self.print(par)
        ret += ")"
        if node.has_return_type():
            ret += " " + self.print(node.get_return_type())
        ret += ":" + print_sl_comment(node.in_comment) + "\n"
        self.inc_indent()
        ret += self.print(node.get_stmts_body()) + "\n"
        self.dec_indent()
        return ret

    def print_if_clause(self, node: ASTIfClause) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent)
        ret += print_n_spaces(self.indent) + "if " + self.print(node.get_condition()) + ":"
        ret += print_sl_comment(node.in_comment) + "\n"
        self.inc_indent()
        ret += self.print(node.get_stmts_body())
        self.dec_indent()

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
        ret += " <- "
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

    def print_compilation_unit(self, node: ASTNestMLCompilationUnit) -> str:
        ret = ""
        if node.get_model_list() is not None:
            for model in node.get_model_list():
                ret += self.print(model)

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
        if node.get_attributes():
            ret += "("
            for i, attr in enumerate(node.get_attributes()):
                ret += self.print(attr)
                if i < len(node.get_attributes()) - 1:
                    ret += ", "

            ret += ")"
        ret += print_sl_comment(node.in_comment)
        ret += "\n"
        return ret

    def print_parameter(self, node: ASTParameter) -> str:
        return node.get_name() + " " + self.print(node.get_data_type())

    def print_return_stmt(self, node: ASTReturnStmt):
        ret = print_n_spaces(self.indent)
        ret += "return " + (self.print(node.get_expression()) if node.has_expression() else "")
        return ret

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

    def print_unit_type(self, node: ASTUnitType) -> str:
        if node.is_encapsulated:
            return "(" + self.print(node.compound_unit) + ")"

        if node.is_pow:
            return self.print(node.base) + "**" + str(node.exponent)

        if node.is_arithmetic_expression():
            t_lhs = self.print(node.get_lhs()) if isinstance(node.get_lhs(), ASTUnitType) else str(node.get_lhs())
            if node.is_times:
                return t_lhs + "*" + self.print(node.get_rhs())

            return t_lhs + "/" + self.print(node.get_rhs())

        return node.unit

    def print_on_receive_block(self, node: ASTOnReceiveBlock) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + "onReceive(" + node.port_name + "):" + print_sl_comment(node.in_comment) + "\n"
        self.inc_indent()
        ret += self.print(node.get_stmts_body())
        self.dec_indent()

        return ret

    def print_on_condition_block(self, node: ASTOnConditionBlock) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + "onCondition(" + self.print(node.get_cond_expr()) + "):" + print_sl_comment(node.in_comment) + "\n"
        self.inc_indent()
        ret += self.print(node.get_stmts_body())
        self.dec_indent()

        return ret

    def print_update_block(self, node: ASTUpdateBlock):
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += print_n_spaces(self.indent) + "update:" + print_sl_comment(node.in_comment) + "\n"
        self.inc_indent()
        ret += self.print(node.get_stmts_body())
        self.dec_indent()
        return ret

    def print_while_stmt(self, node: ASTWhileStmt) -> str:
        ret = print_ml_comments(node.pre_comments, self.indent, False)
        ret += (print_n_spaces(self.indent) + "while " + self.print(node.get_condition())
                + ":" + print_sl_comment(node.in_comment) + "\n")
        self.inc_indent()
        ret += self.print(node.get_stmts_body())
        self.dec_indent()

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
        if comment.lstrip() == "":
            ret += "# \n"

        for c_line in comment.splitlines(True):
            if c_line == "\n":
                ret += print_n_spaces(indent) + "#" + "\n"
                continue

            ret += print_n_spaces(indent)
            if c_line[len(c_line) - len(c_line.lstrip())] != "#":
                ret += "# "

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
