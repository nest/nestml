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

from typing import List, Tuple, Union

from antlr4 import CommonTokenStream, FileStream, InputStream
from antlr4.error.ErrorStrategy import BailErrorStrategy, DefaultErrorStrategy
from antlr4.error.ErrorListener import ConsoleErrorListener, ErrorListener
from antlr4.error.Errors import ParseCancellationException

from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.generated.PyNestMLLexer import PyNestMLLexer
from pynestml.generated.PyNestMLParser import PyNestMLParser
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_stmts_body import ASTStmtsBody
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
from pynestml.meta_model.ast_nestml_compilation_unit import ASTNestMLCompilationUnit
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_model_body import ASTModelBody
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_on_condition_block import ASTOnConditionBlock
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock
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
from pynestml.symbol_table.scope import Scope, ScopeType
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.error_listener import NestMLErrorListener
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.assign_implicit_conversion_factors_visitor import AssignImplicitConversionFactorsVisitor
from pynestml.visitors.ast_builder_visitor import ASTBuilderVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.visitors.ast_parent_visitor import ASTParentVisitor
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor


class ModelParser:
    @classmethod
    def parse_file(cls, file_path=None):
        """
        Parses a handed over model and returns the meta_model representation of it.
        :param file_path: the path to the file which shall be parsed.
        :type file_path: str
        :return: a new ASTNESTMLCompilationUnit object.
        :rtype: ASTNestMLCompilationUnit
        """
        try:
            input_file = FileStream(file_path, encoding='utf-8')
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
        lexerErrorListener = NestMLErrorListener()
        lexer.addErrorListener(lexerErrorListener)
        lexer._errHandler = BailErrorStrategy()  # halt immediately on lexer errors
        lexer._errHandler.reset(lexer)
        lexer.inputStream = input_file
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        if lexerErrorListener._error_occurred:
            error_location = ASTSourceLocation(lexerErrorListener.line,
                                               lexerErrorListener.column,
                                               lexerErrorListener.line,
                                               lexerErrorListener.column)
            code, message = Messages.get_lexer_error(lexerErrorListener.msg)
            Logger.log_message(node=None, code=None, message=message,
                               error_position=error_location, log_level=LoggingLevel.ERROR)
            return

        # parse the file
        parser = PyNestMLParser(None)
        parser.removeErrorListeners()
        parserErrorListener = NestMLErrorListener()
        parser.addErrorListener(parserErrorListener)
        # parser._errHandler = BailErrorStrategy()	# N.B. uncomment this line and the next to halt immediately on parse errors
        # parser._errHandler.reset(parser)
        parser.setTokenStream(stream)
        compilation_unit = parser.nestMLCompilationUnit()
        if parserErrorListener._error_occurred:
            error_location = ASTSourceLocation(parserErrorListener.line,
                                               parserErrorListener.column,
                                               parserErrorListener.line,
                                               parserErrorListener.column)
            code, message = Messages.get_parser_error(parserErrorListener.msg)
            Logger.log_message(node=None, code=None, message=message,
                               error_position=error_location, log_level=LoggingLevel.ERROR)
            return

        # create a new visitor and return the new AST
        ast_builder_visitor = ASTBuilderVisitor(stream.tokens)
        ast = ast_builder_visitor.visit(compilation_unit)

        # create links back from children in the tree to their parents
        for model in ast.get_model_list():
            model.parent_ = None   # root node has no parent
            model.accept(ASTParentVisitor())

        # create and update the corresponding symbol tables
        SymbolTable.initialize_symbol_table(ast.get_source_position())
        for model in ast.get_model_list():
            model.accept(ASTSymbolTableVisitor())
            SymbolTable.add_model_scope(model.get_name(), model.get_scope())

        # .......
        for model in ast.get_model_list():
            model.accept(AssignImplicitConversionFactorsVisitor())

        # store source paths
        for model in ast.get_model_list():
            model.file_path = file_path

        ast.file_path = file_path

        return ast

    @classmethod
    def parse_expression(cls, string: str, verbose: bool = True) -> ASTExpression:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.expression())

        return ret

    @classmethod
    def parse_declaration(cls, string: str, verbose: bool = True) -> ASTDeclaration:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.declaration())

        return ret

    @classmethod
    def parse_stmt(cls, string: str, verbose: bool = True) -> ASTStmt:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.stmt())

        return ret

    @classmethod
    def parse_assignment(cls, string: str, verbose: bool = True) -> ASTAssignment:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.assignment())

        return ret

    @classmethod
    def parse_bit_operator(cls, string: str, verbose: bool = True) -> ASTArithmeticOperator:
        builder, parser = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.bitOperator())

    @classmethod
    def parse_block_with_variables(cls, string: str, verbose: bool = True) -> ASTBlockWithVariables:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.blockWithVariables())

        return ret

    @classmethod
    def parse_model_body(cls, string: str, verbose: bool = True) -> ASTModelBody:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.modelBody())

        return ret

    @classmethod
    def parse_comparison_operator(cls, string: str, verbose: bool = True) -> ASTComparisonOperator:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.comparisonOperator())

        return ret

    @classmethod
    def parse_compound_stmt(cls, string: str, verbose: bool = True) -> ASTCompoundStmt:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.compoundStmt())

        return ret

    @classmethod
    def parse_data_type(cls, string: str, verbose: bool = True) -> ASTDataType:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.dataType())

        return ret

    @classmethod
    def parse_elif_clause(cls, string: str, verbose: bool = True) -> ASTElifClause:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.elifClause())

        return ret

    @classmethod
    def parse_else_clause(cls, string: str, verbose: bool = True) -> ASTElseClause:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.elseClause())

        return ret

    @classmethod
    def parse_equations_block(cls, string: str, verbose: bool = True) -> ASTEquationsBlock:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.equationsBlock())

        return ret

    @classmethod
    def parse_for_stmt(cls, string: str, verbose: bool = True) -> ASTForStmt:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.forStmt())

        return ret

    @classmethod
    def parse_function(cls, string: str, verbose: bool = True) -> ASTFunction:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.function())

        return ret

    @classmethod
    def parse_function_call(cls, string: str, verbose: bool = True) -> ASTFunctionCall:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.functionCall())

        return ret

    @classmethod
    def parse_if_clause(cls, string: str, verbose: bool = True) -> ASTIfClause:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.ifClause())

        return ret

    @classmethod
    def parse_if_stmt(cls, string: str, verbose: bool = True) -> ASTIfStmt:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.ifStmt())

        return ret

    @classmethod
    def parse_input_block(cls, string: str, verbose: bool = True) -> ASTInputBlock:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.inputBlock())

        return ret

    @classmethod
    def parse_input_port(cls, string: str, verbose: bool = True) -> ASTInputPort:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.inputPort())

        return ret

    @classmethod
    def parse_input_qualifier(cls, string: str, verbose: bool = True) -> ASTInputQualifier:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.inputQualifier())

        return ret

    @classmethod
    def parse_logic_operator(cls, string: str, verbose: bool = True) -> ASTLogicalOperator:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.logicalOperator())

        return ret

    @classmethod
    def parse_nestml_compilation_unit(cls, string: str, verbose: bool = True) -> ASTNestMLCompilationUnit:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.nestMLCompilationUnit())

        return ret

    @classmethod
    def parse_model(cls, string: str, verbose: bool = True) -> ASTModel:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.model())

        return ret

    @classmethod
    def parse_ode_equation(cls, string: str, verbose: bool = True) -> ASTOdeEquation:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.odeEquation())

        return ret

    @classmethod
    def parse_inline_expression(cls, string: str, verbose: bool = True) -> ASTInlineExpression:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.inlineExpression())

        return ret

    @classmethod
    def parse_kernel(cls, string: str, verbose: bool = True) -> ASTKernel:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.kernel())

        return ret

    @classmethod
    def parse_output_block(cls, string: str, verbose: bool = True) -> ASTOutputBlock:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.outputBlock())

        return ret

    @classmethod
    def parse_on_receive_block(cls, string: str, verbose: bool = True) -> ASTOnReceiveBlock:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.onReceiveBlock())

        return ret

    @classmethod
    def parse_on_condition_block(cls, string: str, verbose: bool = True) -> ASTOnConditionBlock:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.onConditionBlock())

        return ret

    @classmethod
    def parse_parameter(cls, string: str, verbose: bool = True) -> ASTParameter:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.parameter())

        return ret

    @classmethod
    def parse_return_stmt(cls, string: str, verbose: bool = True) -> ASTReturnStmt:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.returnStmt())

        return ret

    @classmethod
    def parse_simple_expression(cls, string: str, verbose: bool = True) -> ASTSimpleExpression:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.simpleExpression())

        return ret

    @classmethod
    def parse_small_stmt(cls, string: str, verbose: bool = True) -> ASTSmallStmt:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.smallStmt())

        return ret

    @classmethod
    def parse_unary_operator(cls, string: str, verbose: bool = True) -> ASTUnaryOperator:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.unaryOperator())

        return ret

    @classmethod
    def parse_unit_type(cls, string: str, verbose: bool = True) -> ASTUnitType:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.unitType())

        return ret

    @classmethod
    def parse_update_block(cls, string: str, verbose: bool = True) -> ASTUpdateBlock:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.updateBlock())

        return ret

    @classmethod
    def parse_variable(cls, string: str, verbose: bool = True) -> ASTVariable:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.variable())

        return ret

    @classmethod
    def parse_while_stmt(cls, string: str, verbose: bool = True) -> ASTWhileStmt:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.whileStmt())

        return ret

    @classmethod
    def parse_stmts_body(cls, string: str, verbose: bool = True) -> ASTStmtsBody:
        (builder, parser) = tokenize(string, verbose=verbose)
        ret = builder.visit(parser.stmtsBody())

        return ret

    @classmethod
    def parse_included_file(cls, filename: str) -> Union[ASTNode, List[ASTNode]]:
        with open(filename, 'r') as file:
            lines = file.read()
            ast = None
            try:
                ast = ModelParser.parse_model(lines, verbose=False)
            except (ParseCancellationException, AttributeError):
                pass

            if not ast:
                try:
                    ast = ModelParser.parse_model_body(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_block_with_variables(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_equations_block(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_input_block(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_output_block(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_on_receive_block(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_on_condition_block(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_update_block(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_stmts_body(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_stmt(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

            if not ast:
                try:
                    ast = ModelParser.parse_small_stmt(lines, verbose=False)
                except (ParseCancellationException, AttributeError):
                    pass

        assert ast

        return ast


def tokenize(string: str, verbose: bool = True) -> Tuple[ASTBuilderVisitor, PyNestMLParser]:
    lexer = PyNestMLLexer(InputStream(string))
    # create a token stream
    stream = CommonTokenStream(lexer)
    stream.fill()
    parser = PyNestMLParser(stream)
    if verbose:
        parser.addErrorListener(BailConsoleErrorListener())
    else:
        parser._errHandler = BailErrorStrategy()
        parser._errHandler.reset(parser)

    builder = ASTBuilderVisitor(stream.tokens)

    return builder, parser


class BailConsoleErrorListener(ErrorListener):
    """Print error message to the console as well as bail"""
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        code, message = Messages.get_parser_error_verbose(msg)
        Logger.log_message(message=message,
                           error_position=ASTSourceLocation(start_line=line, start_column=column, end_line=line, end_column=column + 1),
                           code=code,
                           log_level=LoggingLevel.ERROR)
        raise ParseCancellationException(message)
