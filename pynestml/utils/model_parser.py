# -*- coding: utf-8 -*-
#
# model_parser.py
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
import copy

from antlr4 import *
from antlr4.error.ErrorStrategy import BailErrorStrategy, DefaultErrorStrategy
from antlr4.error.ErrorListener import ConsoleErrorListener

from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.generated.PyNestMLParser import PyNestMLParser
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
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
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_while_stmt import ASTWhileStmt
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_builder_visitor import ASTBuilderVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.utils.error_listener import NestMLErrorListener


class ModelParser(object):

    @classmethod
    def parse_model(cls, file_path=None):
        """
        Parses a handed over model and returns the meta_model representation of it.
        :param file_path: the path to the file which shall be parsed.
        :type file_path: str
        :return: a new ASTNESTMLCompilationUnit object.
        :rtype: ASTNestMLCompilationUnit
        """
        try:
            input_file = FileStream(file_path)
        except IOError:
            code, message = Messages.get_input_path_not_found(path=file_path)
            Logger.log_message(node=None, code=None, message=message,
                               error_position=None, log_level=LoggingLevel.ERROR)
            return
        code, message = Messages.get_start_processing_file(file_path)
        Logger.log_message(node=None, code=code, message=message, error_position=None, log_level=LoggingLevel.INFO)

        # create a lexer and hand over the input
        lexer = PyNestMLLexer()
        lexer.removeErrorListeners()
        lexer.addErrorListener(ConsoleErrorListener())
        lexerErrorListener = NestMLErrorListener()
        lexer.addErrorListener(lexerErrorListener)
        # lexer._errHandler = BailErrorStrategy()  # N.B. uncomment this line and the next to halt immediately on lexer errors
        # lexer._errHandler.reset(lexer)
        lexer.inputStream = input_file
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        if lexerErrorListener._error_occurred:
            code, message = Messages.get_lexer_error()
            Logger.log_message(node=None, code=None, message=message,
                               error_position=None, log_level=LoggingLevel.ERROR)
            return
        # parse the file
        parser = PyNestMLParser(None)
        parser.removeErrorListeners()
        parser.addErrorListener(ConsoleErrorListener())
        parserErrorListener = NestMLErrorListener()
        parser.addErrorListener(parserErrorListener)
        # parser._errHandler = BailErrorStrategy()	# N.B. uncomment this line and the next to halt immediately on parse errors
        # parser._errHandler.reset(parser)
        parser.setTokenStream(stream)
        compilation_unit = parser.nestMLCompilationUnit()
        if parserErrorListener._error_occurred:
            code, message = Messages.get_parser_error()
            Logger.log_message(node=None, code=None, message=message,
                               error_position=None, log_level=LoggingLevel.ERROR)
            return

        # create a new visitor and return the new AST
        ast_builder_visitor = ASTBuilderVisitor(stream.tokens)
        ast = ast_builder_visitor.visit(compilation_unit)

        # create and update the corresponding symbol tables
        SymbolTable.initialize_symbol_table(ast.get_source_position())
        log_to_restore = copy.deepcopy(Logger.get_log())
        counter = Logger.curr_message

        Logger.set_log(log_to_restore, counter)
        for neuron in ast.get_neuron_list():
            neuron.accept(ASTSymbolTableVisitor())
            SymbolTable.add_neuron_scope(neuron.get_name(), neuron.get_scope())

        # store source paths
        for neuron in ast.get_neuron_list():
            neuron.file_path = file_path
        ast.file_path = file_path

        return ast

    @classmethod
    def parse_expression(cls, string):
        # type: (str) -> ASTExpression
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.expression())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_declaration(cls, string):
        # type: (str) -> ASTDeclaration
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.declaration())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_stmt(cls, string):
        # type: (str) -> ASTStmt
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.stmt())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_assignment(cls, string):
        # type: (str) -> ASTAssignment
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.assignment())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_bit_operator(cls, string):
        # type: (str) -> ASTArithmeticOperator
        builder, parser = tokenize(string)
        ret = builder.visit(parser.bitOperator())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_block(cls, string):
        # type: (str) -> ASTBlock
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.block())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_block_with_variables(cls, string):
        # type: (str) -> ASTBlockWithVariables
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.blockWithVariables())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_body(cls, string):
        # type: (str) -> ASTBody
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.body())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_comparison_operator(cls, string):
        # type: (str) -> ASTComparisonOperator
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.comparisonOperator())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_compound_stmt(cls, string):
        # type: (str) -> ASTCompoundStmt
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.compoundStmt())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_data_type(cls, string):
        # type: (str) -> ASTDataType
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.dataType())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_elif_clause(cls, string):
        # type: (str) -> ASTElifClause
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.elifClause())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_else_clause(cls, string):
        # type: (str) -> ASTElseClause
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.elseClause())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_equations_block(cls, string):
        # type: (str) -> ASTEquationsBlock
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.equationsBlock())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_for_stmt(cls, string):
        # type: (str) -> ASTForStmt
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.forStmt())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_function(cls, string):
        # type: (str) -> ASTFunction
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.function())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_function_call(cls, string):
        # type: (str) -> ASTFunctionCall
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.functionCall())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_if_clause(cls, string):
        # type: (str) -> ASTIfClause
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.ifClause())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_if_stmt(cls, string):
        # type: (str) -> ASTIfStmt
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.ifStmt())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_input_block(cls, string):
        # type: (str) -> ASTInputBlock
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.inputBlock())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_input_port(cls, string):
        # type: (str) -> ASTInputPort
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.inputPort())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_input_qualifier(cls, string):
        # type: (str) -> ASTInputQualifier
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.inputQualifier())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_logic_operator(cls, string):
        # type: (str) -> ASTLogicalOperator
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.logicalOperator())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_nestml_compilation_unit(cls, string):
        # type: (str) -> ASTNestMLCompilationUnit
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.nestMLCompilationUnit())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_neuron(cls, string):
        # type: (str) -> ASTNeuron
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.neuron())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_ode_equation(cls, string):
        # type: (str) -> ASTOdeEquation
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.odeEquation())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_inline_expression(cls, string):
        # type: (str) -> ASTInlineExpression
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.inlineExpression())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_kernel(cls, string):
        # type: (str) -> ASTKernel
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.kernel())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_output_block(cls, string):
        # type: (str) -> ASTOutputBlock
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.outputBlock())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_parameter(cls, string):
        # type: (str) -> ASTParameter
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.parameter())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_return_stmt(cls, string):
        # type: (str) -> ASTReturnStmt
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.returnStmt())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_simple_expression(cls, string):
        # type: (str) -> ASTSimpleExpression
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.simpleExpression())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_small_stmt(cls, string):
        # type: (str) -> ASTSmallStmt
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.smallStmt())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_unary_operator(cls, string):
        # type: (str) -> ASTUnaryOperator
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.unaryOperator())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_unit_type(cls, string):
        # type: (str) -> ASTUnitType
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.unitType())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_update_block(cls, string):
        # type: (str) -> ASTUpdateBlock
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.updateBlock())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_variable(cls, string):
        # type: (str) -> ASTVariable
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.variable())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_while_stmt(cls, string):
        # type: (str) -> ASTWhileStmt
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.whileStmt())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret


def tokenize(string):
    # type: (str) -> (ASTBuilderVisitor,PyNestMLParser)
    lexer = PyNestMLLexer(InputStream(string))
    # create a token stream
    stream = CommonTokenStream(lexer)
    stream.fill()
    parser = PyNestMLParser(stream)
    builder = ASTBuilderVisitor(stream.tokens)
    return builder, parser


def log_set_added_source_position(node):
    node.set_source_position(ASTSourceLocation.get_added_source_position())
