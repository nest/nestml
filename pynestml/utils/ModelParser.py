#
# ModelParser.py
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
from antlr4 import *

from pynestml.generated.PyNestMLParser import PyNestMLParser
from pynestml.generated.PyNestMLLexer import PyNestMLLexer

from pynestml.modelprocessor.ASTSymbolTableVisitor import ASTSymbolTableVisitor
from pynestml.modelprocessor.ASTBuilderVisitor import ASTBuilderVisitor
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.modelprocessor.ASTSourceLocation import ASTSourceLocation
from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTBlock import ASTBlock
from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
from pynestml.modelprocessor.ASTBody import ASTBody
from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
from pynestml.modelprocessor.ASTDataType import ASTDataType
from pynestml.modelprocessor.ASTAssignment import ASTAssignment
from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
from pynestml.modelprocessor.ASTElifClause import ASTElifClause
from pynestml.modelprocessor.ASTElseClause import ASTElseClause
from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTForStmt import ASTForStmt
from pynestml.modelprocessor.ASTFunction import ASTFunction
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTIfClause import ASTIfClause
from pynestml.modelprocessor.ASTIfStmt import ASTIfStmt
from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
from pynestml.modelprocessor.ASTInputLine import ASTInputLine
from pynestml.modelprocessor.ASTInputType import ASTInputType
from pynestml.modelprocessor.ASTStmt import ASTStmt
from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
from pynestml.modelprocessor.ASTNestMLCompilationUnit import ASTNestMLCompilationUnit
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
from pynestml.modelprocessor.ASTParameter import ASTParameter
from pynestml.modelprocessor.ASTReturnStmt import ASTReturnStmt
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTUnitType import ASTUnitType
from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.ASTWhileStmt import ASTWhileStmt


from pynestml.utils.Logger import Logger, LoggingLevel
from pynestml.utils.Messages import Messages


class ModelParser(object):
    """
    This class contains several method used to parse handed over models and returns them as one or more AST trees.
    """

    @classmethod
    def parse_model(cls, file_path=None):
        """
        Parses a handed over model and returns the ast representation of it.
        :param file_path: the path to the file which shall be parsed.
        :type file_path: str
        :return: a new ASTNESTMLCompilationUnit object.
        :rtype: ASTNestMLCompilationUnit
        """
        try:
            input_file = FileStream(file_path)
        except IOError:
            print('(PyNestML.Parser) File ' + str(file_path) + ' not found. Processing is stopped!')
            return
        code, message = Messages.getStartProcessingFile(file_path)
        Logger.log_message(neuron=None, code=code, message=message, error_position=None, log_level=LoggingLevel.INFO)
        # create a lexer and hand over the input
        lexer = PyNestMLLexer(input_file)
        # create a token stream
        stream = CommonTokenStream(lexer)
        stream.fill()
        # parse the file
        parser = PyNestMLParser(stream)
        compilation_unit = parser.nestMLCompilationUnit()
        # create a new visitor and return the new AST
        ast_builder_visitor = ASTBuilderVisitor(stream.tokens)
        ast = ast_builder_visitor.visit(compilation_unit)
        # create and update the corresponding symbol tables
        SymbolTable.initialize_symbol_table(ast.get_source_position())
        symbol_table_visitor = ASTSymbolTableVisitor()
        for neuron in ast.get_neuron_list():
            neuron.accept(symbol_table_visitor)
            SymbolTable.add_neuron_scope(neuron.get_name(), neuron.get_scope())
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
    def parse_input_line(cls, string):
        # type: (str) -> ASTInputLine
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.inputLine())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_input_type(cls, string):
        # type: (str) -> ASTInputType
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.inputType())
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
    def parse_ode_function(cls, string):
        # type: (str) -> ASTOdeFunction
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.odeFunction())
        ret.accept(ASTHigherOrderVisitor(log_set_added_source_position))
        return ret

    @classmethod
    def parse_ode_shape(cls, string):
        # type: (str) -> ASTOdeShape
        (builder, parser) = tokenize(string)
        ret = builder.visit(parser.odeShape())
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
