# -*- coding: utf-8 -*-
#
# ast_builder_visitor.py
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

import ntpath
import re

from pynestml.cocos.co_co_each_block_unique_and_defined import CoCoEachBlockUniqueAndDefined
from pynestml.cocos.co_cos_manager import CoCosManager
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.generated.PyNestMLParserVisitor import PyNestMLParserVisitor
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import Logger
from pynestml.utils.port_signal_type import PortSignalType
from pynestml.visitors.ast_data_type_visitor import ASTDataTypeVisitor
from pynestml.visitors.comment_collector_visitor import CommentCollectorVisitor


class ASTBuilderVisitor(PyNestMLParserVisitor):
    """
    This class is used to create an internal representation of the model by means of an abstract syntax tree.
    """

    def __init__(self, tokens):
        self.__comments = CommentCollectorVisitor(tokens)
        self.data_type_visitor = ASTDataTypeVisitor()

    # Visit a parse tree produced by PyNESTMLParser#nestmlCompilationUnit.
    def visitNestMLCompilationUnit(self, ctx):
        # now process the actual model
        neurons = list()
        for child in ctx.neuron():
            neurons.append(self.visit(child))
        # extract the name of the artifact from the context
        artifact_name = ntpath.basename(ctx.start.source[1].fileName)
        compilation_unit = ASTNodeFactory.create_ast_nestml_compilation_unit(list_of_neurons=neurons,
                                                                             source_position=create_source_pos(ctx),
                                                                             artifact_name=artifact_name)
        # first ensure certain properties of the neuron
        CoCosManager.check_neuron_names_unique(compilation_unit)
        return compilation_unit

    # Visit a parse tree produced by PyNESTMLParser#datatype.
    def visitDataType(self, ctx):
        is_int = (True if ctx.isInt is not None else False)
        is_real = (True if ctx.isReal is not None else False)
        is_string = (True if ctx.isString is not None else False)
        is_bool = (True if ctx.isBool is not None else False)
        is_void = (True if ctx.isVoid is not None else False)
        unit = self.visit(ctx.unitType()) if ctx.unitType() is not None else None
        ret = ASTNodeFactory.create_ast_data_type(is_integer=is_int, is_boolean=is_bool,
                                                  is_real=is_real, is_string=is_string, is_void=is_void,
                                                  is_unit_type=unit, source_position=create_source_pos(ctx))
        # now update the type
        ret.accept(ASTDataTypeVisitor())
        # self.data_type_visitor.visit_datatype(ret)
        return ret

    # Visit a parse tree produced by PyNESTMLParser#unitType.
    def visitUnitType(self, ctx):
        left_parenthesis = True if ctx.leftParentheses is not None else False
        compound_unit = self.visit(ctx.compoundUnit) if ctx.compoundUnit is not None else None
        is_encapsulated = left_parenthesis and True if ctx.rightParentheses is not None else False
        base = self.visit(ctx.base) if ctx.base is not None else None
        is_pow = True if ctx.powOp is not None else False
        exponent = int(str(ctx.exponent.getText())) if ctx.exponent is not None else None
        if ctx.unitlessLiteral is not None:
            lhs = int(str(ctx.unitlessLiteral.text))
        else:
            lhs = self.visit(ctx.left) if ctx.left is not None else None
        is_times = True if ctx.timesOp is not None else False
        is_div = True if ctx.divOp is not None else False
        rhs = self.visit(ctx.right) if ctx.right is not None else None
        unit = str(ctx.unit.text) if ctx.unit is not None else None
        return ASTNodeFactory.create_ast_unit_type(is_encapsulated=is_encapsulated, compound_unit=compound_unit,
                                                   base=base, is_pow=is_pow,
                                                   exponent=exponent, lhs=lhs, rhs=rhs, is_div=is_div,
                                                   is_times=is_times, unit=unit, source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#rhs.
    def visitExpression(self, ctx):
        # first check if it is a simple rhs
        if ctx.simpleExpression() is not None:
            return self.visitSimpleExpression(ctx.simpleExpression())
        # now it is not directly a simple rhs
        # check if it is an encapsulated rhs
        is_encapsulated = (True if ctx.leftParentheses is not None and ctx.rightParentheses else False)
        # or a term or negated
        unary_operator = (self.visit(ctx.unaryOperator()) if ctx.unaryOperator() is not None else None)
        is_logical_not = (True if ctx.logicalNot is not None else False)
        expression = self.visit(ctx.term) if ctx.term is not None else None
        # otherwise it is a combined one, check first lhs, then the operator and finally rhs
        lhs = (self.visit(ctx.left) if ctx.left is not None else None)
        if ctx.powOp is not None:
            source_pos = ASTSourceLocation.make_ast_source_position(start_line=ctx.powOp.line,
                                                                    start_column=ctx.powOp.column,
                                                                    end_line=ctx.powOp.line,
                                                                    end_column=ctx.powOp.column)
            binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_pow_op=True,
                                                                            source_position=source_pos)
        elif ctx.timesOp is not None:
            source_pos = ASTSourceLocation.make_ast_source_position(start_line=ctx.timesOp.line,
                                                                    start_column=ctx.timesOp.column,
                                                                    end_line=ctx.timesOp.line,
                                                                    end_column=ctx.timesOp.column)
            binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True,
                                                                            source_position=source_pos)
        elif ctx.divOp is not None:
            source_pos = ASTSourceLocation.make_ast_source_position(start_line=ctx.divOp.line,
                                                                    start_column=ctx.divOp.column,
                                                                    end_line=ctx.divOp.line,
                                                                    end_column=ctx.divOp.column)
            binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True,
                                                                            source_position=source_pos)
        elif ctx.moduloOp is not None:
            source_pos = ASTSourceLocation.make_ast_source_position(start_line=ctx.moduloOp.line,
                                                                    start_column=ctx.moduloOp.column,
                                                                    end_line=ctx.moduloOp.line,
                                                                    end_column=ctx.moduloOp.column)
            binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_modulo_op=True,
                                                                            source_position=source_pos)
        elif ctx.plusOp is not None:
            source_pos = ASTSourceLocation.make_ast_source_position(start_line=ctx.plusOp.line,
                                                                    start_column=ctx.plusOp.column,
                                                                    end_line=ctx.plusOp.line,
                                                                    end_column=ctx.plusOp.column)
            binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_plus_op=True,
                                                                            source_position=source_pos)
        elif ctx.minusOp is not None:
            source_pos = ASTSourceLocation.make_ast_source_position(start_line=ctx.minusOp.line,
                                                                    start_column=ctx.minusOp.column,
                                                                    end_line=ctx.minusOp.line,
                                                                    end_column=ctx.minusOp.column)
            binary_operator = ASTNodeFactory.create_ast_arithmetic_operator(is_minus_op=True,
                                                                            source_position=source_pos)
        elif ctx.bitOperator() is not None:
            binary_operator = self.visit(ctx.bitOperator())
        elif ctx.comparisonOperator() is not None:
            binary_operator = self.visit(ctx.comparisonOperator())
        elif ctx.logicalOperator() is not None:
            binary_operator = self.visit(ctx.logicalOperator())
        else:
            binary_operator = None
        rhs = (self.visit(ctx.right) if ctx.right is not None else None)
        # not it was not an operator, thus the ternary one ?
        condition = (self.visit(ctx.condition) if ctx.condition is not None else None)
        if_true = (self.visit(ctx.ifTrue) if ctx.ifTrue is not None else None)
        if_not = (self.visit(ctx.ifNot) if ctx.ifNot is not None else None)
        source_pos = create_source_pos(ctx)
        # finally construct the corresponding rhs
        if expression is not None:
            return ASTNodeFactory.create_ast_expression(is_encapsulated=is_encapsulated,
                                                        is_logical_not=is_logical_not,
                                                        unary_operator=unary_operator,
                                                        expression=expression, source_position=source_pos)
        elif (lhs is not None) and (rhs is not None) and (binary_operator is not None):
            return ASTNodeFactory.create_ast_compound_expression(lhs=lhs, binary_operator=binary_operator,
                                                                 rhs=rhs, source_position=source_pos)
        elif (condition is not None) and (if_true is not None) and (if_not is not None):
            return ASTNodeFactory.create_ast_ternary_expression(condition=condition, if_true=if_true,
                                                                if_not=if_not, source_position=source_pos)
        else:
            raise RuntimeError('Type of rhs @%s,%s not recognized!' % (ctx.start.line, ctx.start.column))

    # Visit a parse tree produced by PyNESTMLParser#simpleExpression.
    def visitSimpleExpression(self, ctx):
        function_call = (self.visit(ctx.functionCall()) if ctx.functionCall() is not None else None)
        boolean_literal = ((True if re.match(r'[Tt]rue', str(
            ctx.BOOLEAN_LITERAL())) else False) if ctx.BOOLEAN_LITERAL() is not None else None)
        if ctx.UNSIGNED_INTEGER() is not None:
            numeric_literal = int(str(ctx.UNSIGNED_INTEGER()))
        elif ctx.FLOAT() is not None:
            numeric_literal = float(str(ctx.FLOAT()))
        else:
            numeric_literal = None
        is_inf = (True if ctx.isInf is not None else False)
        variable = (self.visit(ctx.variable()) if ctx.variable() is not None else None)
        string = (str(ctx.string.text) if ctx.string is not None else None)
        return ASTNodeFactory.create_ast_simple_expression(function_call=function_call,
                                                           boolean_literal=boolean_literal,
                                                           numeric_literal=numeric_literal,
                                                           is_inf=is_inf, variable=variable,
                                                           string=string,
                                                           source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#unaryOperator.
    def visitUnaryOperator(self, ctx):
        is_unary_plus = (True if ctx.unaryPlus is not None else False)
        is_unary_minus = (True if ctx.unaryMinus is not None else False)
        is_unary_tilde = (True if ctx.unaryTilde is not None else False)
        return ASTNodeFactory.create_ast_unary_operator(is_unary_plus=is_unary_plus,
                                                        is_unary_minus=is_unary_minus,
                                                        is_unary_tilde=is_unary_tilde,
                                                        source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#bitOperator.
    def visitBitOperator(self, ctx):
        is_bit_and = (True if ctx.bitAnd is not None else False)
        is_bit_xor = (True if ctx.bitXor is not None else False)
        is_bit_or = (True if ctx.bitOr is not None else False)
        is_bit_shift_left = (True if ctx.bitShiftLeft is not None else False)
        is_bit_shift_right = (True if ctx.bitShiftRight is not None else False)
        return ASTNodeFactory.create_ast_bit_operator(is_bit_and=is_bit_and, is_bit_xor=is_bit_xor,
                                                      is_bit_or=is_bit_or,
                                                      is_bit_shift_left=is_bit_shift_left,
                                                      is_bit_shift_right=is_bit_shift_right,
                                                      source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#comparisonOperator.
    def visitComparisonOperator(self, ctx):
        is_lt = (True if ctx.lt is not None else False)
        is_le = (True if ctx.le is not None else False)
        is_eq = (True if ctx.eq is not None else False)
        is_ne = (True if ctx.ne is not None else False)
        is_ne2 = (True if ctx.ne2 is not None else False)
        is_ge = (True if ctx.ge is not None else False)
        is_gt = (True if ctx.gt is not None else False)
        return ASTNodeFactory.create_ast_comparison_operator(is_lt, is_le, is_eq, is_ne, is_ne2, is_ge, is_gt,
                                                             create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#logicalOperator.
    def visitLogicalOperator(self, ctx):
        is_logical_and = (True if ctx.logicalAnd is not None else False)
        is_logical_or = (True if ctx.logicalOr is not None else False)
        return ASTNodeFactory.create_ast_logical_operator(is_logical_and=is_logical_and,
                                                          is_logical_or=is_logical_or,
                                                          source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#variable.
    def visitVariable(self, ctx):
        differential_order = (len(ctx.DIFFERENTIAL_ORDER()) if ctx.DIFFERENTIAL_ORDER() is not None else 0)
        return ASTNodeFactory.create_ast_variable(name=str(ctx.NAME()),
                                                  differential_order=differential_order,
                                                  source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#functionCall.
    def visitFunctionCall(self, ctx):
        name = (str(ctx.calleeName.text))
        args = list()
        if type(ctx.expression()) == list:
            for arg in ctx.expression():
                args.append(self.visit(arg))
        elif ctx.expression() is not None:
            args.append(self.visit(ctx.expression()))
        node = ASTNodeFactory.create_ast_function_call(callee_name=name, args=args,
                                                       source_position=create_source_pos(ctx))
        return node

    # Visit a parse tree produced by PyNESTMLParser#inline.
    def visitInlineExpression(self, ctx):
        is_recordable = (True if ctx.recordable is not None else False)
        variable_name = (str(ctx.variableName.text) if ctx.variableName is not None else None)
        data_type = (self.visit(ctx.dataType()) if ctx.dataType() is not None else None)
        expression = (self.visit(ctx.expression()) if ctx.expression() is not None else None)
        inlineExpr = ASTNodeFactory.create_ast_inline_expression(is_recordable=is_recordable, variable_name=variable_name,
                                                                 data_type=data_type, expression=expression,
                                                                 source_position=create_source_pos(ctx))
        update_node_comments(inlineExpr, self.__comments.visit(ctx))
        return inlineExpr

    # Visit a parse tree produced by PyNESTMLParser#equation.
    def visitOdeEquation(self, ctx):
        lhs = self.visit(ctx.lhs) if ctx.lhs is not None else None
        rhs = self.visit(ctx.rhs) if ctx.rhs is not None else None
        ode_equation = ASTNodeFactory.create_ast_ode_equation(lhs=lhs, rhs=rhs, source_position=create_source_pos(ctx))
        update_node_comments(ode_equation, self.__comments.visit(ctx))
        return ode_equation

    # Visit a parse tree produced by PyNESTMLParser#kernel.
    def visitKernel(self, ctx):
        var_nodes = []
        expr_nodes = []
        for var, expr in zip(ctx.variable(), ctx.expression()):
            var_node = self.visit(var)
            expr_node = self.visit(expr)
            var_nodes.append(var_node)
            expr_nodes.append(expr_node)
        kernel = ASTNodeFactory.create_ast_kernel(
            variables=var_nodes, expressions=expr_nodes, source_position=create_source_pos(ctx))
        update_node_comments(kernel, self.__comments.visit(ctx))
        return kernel

    # Visit a parse tree produced by PyNESTMLParser#block.
    def visitBlock(self, ctx):
        stmts = list()
        if ctx.stmt() is not None:
            for stmt in ctx.stmt():
                stmts.append(self.visit(stmt))
        block = ASTNodeFactory.create_ast_block(stmts=stmts, source_position=create_source_pos(ctx))
        return block

    # Visit a parse tree produced by PyNESTMLParser#compound_Stmt.
    def visitCompoundStmt(self, ctx):
        if_stmt = self.visit(ctx.ifStmt()) if ctx.ifStmt() is not None else None
        while_stmt = self.visit(ctx.whileStmt()) if ctx.whileStmt() is not None else None
        for_stmt = self.visit(ctx.forStmt()) if ctx.forStmt() is not None else None
        node = ASTNodeFactory.create_ast_compound_stmt(if_stmt, while_stmt, for_stmt, create_source_pos(ctx))
        update_node_comments(node, self.__comments.visit(ctx))
        return node

    # Visit a parse tree produced by PyNESTMLParser#small_Stmt.
    def visitSmallStmt(self, ctx):
        assignment = self.visit(ctx.assignment()) if ctx.assignment() is not None else None
        function_call = self.visit(ctx.functionCall()) if ctx.functionCall() is not None else None
        declaration = self.visit(ctx.declaration()) if ctx.declaration() is not None else None
        return_stmt = self.visit(ctx.returnStmt()) if ctx.returnStmt() is not None else None
        node = ASTNodeFactory.create_ast_small_stmt(assignment=assignment, function_call=function_call,
                                                    declaration=declaration, return_stmt=return_stmt,
                                                    source_position=create_source_pos(ctx))
        # update_node_comments(node, self.__comments.visit(ctx))
        update_node_comments(node, self.__comments.visit(ctx))
        return node

    # Visit a parse tree produced by PyNESTMLParser#assignment.
    def visitAssignment(self, ctx):
        lhs = self.visit(ctx.lhs_variable) if ctx.lhs_variable is not None else None
        is_direct_assignment = True if ctx.directAssignment is not None else False
        is_compound_sum = True if ctx.compoundSum is not None else False
        is_compound_minus = True if ctx.compoundMinus is not None else False
        is_compound_product = True if ctx.compoundProduct is not None else False
        is_compound_quotient = True if ctx.compoundQuotient is not None else False
        expression = self.visit(ctx.expression()) if ctx.expression() is not None else None
        node = ASTNodeFactory.create_ast_assignment(lhs=lhs, is_direct_assignment=is_direct_assignment,
                                                    is_compound_sum=is_compound_sum,
                                                    is_compound_minus=is_compound_minus,
                                                    is_compound_product=is_compound_product,
                                                    is_compound_quotient=is_compound_quotient,
                                                    expression=expression, source_position=create_source_pos(ctx))
        update_node_comments(node, self.__comments.visit(ctx))
        return node

    # Visit a parse tree produced by PyNESTMLParser#declaration.
    def visitDeclaration(self, ctx):
        is_recordable = (True if ctx.isRecordable is not None else False)
        is_function = (True if ctx.isFunction is not None else False)
        variables = list()
        for var in ctx.variable():
            variables.append(self.visit(var))
        data_type = self.visit(ctx.dataType()) if ctx.dataType() is not None else None
        size_param = str(ctx.sizeParameter.text) if ctx.sizeParameter is not None else None
        expression = self.visit(ctx.rhs) if ctx.rhs is not None else None
        invariant = self.visit(ctx.invariant) if ctx.invariant is not None else None
        declaration = ASTNodeFactory.create_ast_declaration(is_recordable=is_recordable, is_function=is_function,
                                                            variables=variables, data_type=data_type,
                                                            size_parameter=size_param,
                                                            expression=expression,
                                                            invariant=invariant, source_position=create_source_pos(ctx))
        update_node_comments(declaration, self.__comments.visit(ctx))
        return declaration

    # Visit a parse tree produced by PyNESTMLParser#returnStmt.
    def visitReturnStmt(self, ctx):
        ret_expression = self.visit(ctx.expression()) if ctx.expression() is not None else None
        return ASTNodeFactory.create_ast_return_stmt(expression=ret_expression, source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#ifStmt.
    def visitIfStmt(self, ctx):
        if_clause = self.visit(ctx.ifClause()) if ctx.ifClause() is not None else None
        elif_clauses = list()
        if ctx.elifClause() is not None:
            for clause in ctx.elifClause():
                elif_clauses.append(self.visit(clause))
        else_clause = self.visit(ctx.elseClause()) if ctx.elseClause() is not None else None
        return ASTNodeFactory.create_ast_if_stmt(if_clause=if_clause, elif_clauses=elif_clauses,
                                                 else_clause=else_clause, source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#ifClause.
    def visitIfClause(self, ctx):
        condition = self.visit(ctx.expression()) if ctx.expression() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        ret = ASTNodeFactory.create_ast_if_clause(condition=condition, block=block,
                                                  source_position=create_source_pos(ctx))
        update_node_comments(ret, self.__comments.visitStmt(ctx))
        return ret

    # Visit a parse tree produced by PyNESTMLParser#elifClause.
    def visitElifClause(self, ctx):
        condition = self.visit(ctx.expression()) if ctx.expression() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        node = ASTNodeFactory.create_ast_elif_clause(condition=condition, block=block,
                                                     source_position=create_source_pos(ctx))
        update_node_comments(node, self.__comments.visit(ctx))
        return node

    # Visit a parse tree produced by PyNESTMLParser#elseClause.
    def visitElseClause(self, ctx):
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        node = ASTNodeFactory.create_ast_else_clause(block=block, source_position=create_source_pos(ctx))
        update_node_comments(node, self.__comments.visit(ctx))
        return node

    # Visit a parse tree produced by PyNESTMLParser#forStmt.
    def visitForStmt(self, ctx):
        variable = str(ctx.NAME()) if ctx.NAME() is not None else None
        start_from = self.visit(ctx.start_from) if ctx.start_from is not None else None
        end_at = self.visit(ctx.end_at) if ctx.end_at is not None else None
        step_scalar = -1 if ctx.negative is not None else 1
        if ctx.UNSIGNED_INTEGER() is not None:
            value = int(str(ctx.UNSIGNED_INTEGER()))
        else:
            value = float(str(ctx.FLOAT()))

        step = step_scalar * value
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        node = ASTNodeFactory.create_ast_for_stmt(variable=variable, start_from=start_from, end_at=end_at, step=step,
                                                  block=block, source_position=create_source_pos(ctx))
        update_node_comments(node, self.__comments.visit(ctx))
        return node

    # Visit a parse tree produced by PyNESTMLParser#whileStmt.
    def visitWhileStmt(self, ctx):
        cond = self.visit(ctx.expression()) if ctx.expression() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        node = ASTNodeFactory.create_ast_while_stmt(condition=cond, block=block, source_position=create_source_pos(ctx))
        update_node_comments(node, self.__comments.visit(ctx))
        return node

    # Visit a parse tree produced by PyNESTMLParser#neuron.
    def visitNeuron(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        body = self.visit(ctx.body()) if ctx.body() is not None else None
        # after we have constructed the meta_model of the neuron,
        # we can ensure some basic properties which should always hold
        # we have to check if each type of block is defined at most once (except for function), and that input,output
        # and update are defined once
        if hasattr(ctx.start.source[1], 'fileName'):
            artifact_name = ntpath.basename(ctx.start.source[1].fileName)
        else:
            artifact_name = 'parsed from string'
        neuron = ASTNodeFactory.create_ast_neuron(name=name + FrontendConfiguration.suffix, body=body, source_position=create_source_pos(ctx),
                                                  artifact_name=artifact_name)
        # update the comments
        update_node_comments(neuron, self.__comments.visit(ctx))
        # in order to enable the logger to print correct messages set as the source the corresponding neuron
        Logger.set_current_node(neuron)
        CoCoEachBlockUniqueAndDefined.check_co_co(node=neuron)
        Logger.set_current_node(neuron)
        # now the meta_model seems to be correct, return it
        return neuron

    # Visit a parse tree produced by PyNESTMLParser#body.
    def visitBody(self, ctx):
        """
        Here, in order to ensure that the correct order of elements is kept, we use a method which inspects
        a list of elements and returns the one with the smallest source line.
        """
        body_elements = list()
        # visit all var_block children
        if ctx.blockWithVariables() is not None:
            for child in ctx.blockWithVariables():
                body_elements.append(child)
        if ctx.updateBlock() is not None:
            for child in ctx.updateBlock():
                body_elements.append(child)
        if ctx.equationsBlock() is not None:
            for child in ctx.equationsBlock():
                body_elements.append(child)
        if ctx.inputBlock() is not None:
            for child in ctx.inputBlock():
                body_elements.append(child)
        if ctx.outputBlock() is not None:
            for child in ctx.outputBlock():
                body_elements.append(child)
        if ctx.function() is not None:
            for child in ctx.function():
                body_elements.append(child)
        elements = list()
        while len(body_elements) > 0:
            elem = get_next(body_elements)
            elements.append(self.visit(elem))
            body_elements.remove(elem)
        body = ASTNodeFactory.create_ast_body(elements, create_source_pos(ctx))
        return body

    # Visit a parse tree produced by PyNESTMLParser#blockWithVariables.
    def visitBlockWithVariables(self, ctx):
        declarations = list()
        if ctx.declaration() is not None:
            for child in ctx.declaration():
                declarations.append(self.visit(child))
        block_type = ctx.blockType.text  # the text field stores the exact name of the token, e.g., state
        source_pos = create_source_pos(ctx)
        if block_type == 'state':
            ret = ASTNodeFactory.create_ast_block_with_variables(True, False, False, False, declarations, source_pos)
        elif block_type == 'parameters':
            ret = ASTNodeFactory.create_ast_block_with_variables(False, True, False, False, declarations, source_pos)
        elif block_type == 'internals':
            ret = ASTNodeFactory.create_ast_block_with_variables(False, False, True, False, declarations, source_pos)
        elif block_type == 'initial_values':
            ret = ASTNodeFactory.create_ast_block_with_variables(False, False, False, True, declarations, source_pos)
        else:
            raise RuntimeError('(PyNestML.ASTBuilder) Unspecified type (=%s) of var-block.' % str(ctx.blockType))
        update_node_comments(ret, self.__comments.visit(ctx))
        return ret

    def visitUpdateBlock(self, ctx):
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        ret = ASTNodeFactory.create_ast_update_block(block=block, source_position=create_source_pos(ctx))
        update_node_comments(ret, self.__comments.visit(ctx))
        return ret

    # Visit a parse tree produced by PyNESTMLParser#equations.
    def visitEquationsBlock(self, ctx):
        elements = list()
        if ctx.odeEquation() is not None:
            for eq in ctx.odeEquation():
                elements.append(eq)
        if ctx.kernel() is not None:
            for kernel in ctx.kernel():
                elements.append(kernel)
        if ctx.inlineExpression() is not None:
            for fun in ctx.inlineExpression():
                elements.append(fun)
        ordered = list()
        while len(elements) > 0:
            elem = get_next(elements)
            ordered.append(self.visit(elem))
            elements.remove(elem)
        ret = ASTNodeFactory.create_ast_equations_block(declarations=ordered,
                                                        source_position=create_source_pos(ctx))
        update_node_comments(ret, self.__comments.visit(ctx))
        return ret

    # Visit a parse tree produced by PyNESTMLParser#inputBuffer.
    def visitInputBlock(self, ctx):
        input_ports = []
        if ctx.inputPort() is not None:
            for port in ctx.inputPort():
                input_ports.append(self.visit(port))
        ret = ASTNodeFactory.create_ast_input_block(input_definitions=input_ports,
                                                    source_position=create_source_pos(ctx))
        update_node_comments(ret, self.__comments.visit(ctx))
        return ret

    # Visit a parse tree produced by PyNESTMLParser#inputPort.
    def visitInputPort(self, ctx):
        name = str(ctx.name.text) if ctx.name is not None else None
        size_parameter = str(ctx.sizeParameter.text) if ctx.sizeParameter is not None else None
        input_qualifiers = []
        if ctx.inputQualifier() is not None:
            for qual in ctx.inputQualifier():
                input_qualifiers.append(self.visit(qual))
        data_type = self.visit(ctx.dataType()) if ctx.dataType() is not None else None
        if ctx.isCurrent:
            signal_type = PortSignalType.CURRENT
        elif ctx.isSpike:
            signal_type = PortSignalType.SPIKE
        else:
            signal_type = None
        ret = ASTNodeFactory.create_ast_input_port(name=name, size_parameter=size_parameter, data_type=data_type,
                                                   input_qualifiers=input_qualifiers, signal_type=signal_type,
                                                   source_position=create_source_pos(ctx))
        update_node_comments(ret, self.__comments.visit(ctx))
        return ret

    # Visit a parse tree produced by PyNESTMLParser#inputQualifier.
    def visitInputQualifier(self, ctx):
        is_inhibitory = True if ctx.isInhibitory is not None else False
        is_excitatory = True if ctx.isExcitatory is not None else False
        return ASTNodeFactory.create_ast_input_qualifier(is_inhibitory=is_inhibitory, is_excitatory=is_excitatory,
                                                         source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#outputBuffer.
    def visitOutputBlock(self, ctx):
        source_pos = create_source_pos(ctx)
        if ctx.isSpike is not None:
            ret = ASTNodeFactory.create_ast_output_block(s_type=PortSignalType.SPIKE, source_position=source_pos)
            update_node_comments(ret, self.__comments.visit(ctx))
            return ret
        elif ctx.isCurrent is not None:
            ret = ASTNodeFactory.create_ast_output_block(s_type=PortSignalType.CURRENT, source_position=source_pos)
            update_node_comments(ret, self.__comments.visit(ctx))
            return ret
        else:
            raise RuntimeError('(PyNestML.ASTBuilder) Type of output buffer not recognized.')

    # Visit a parse tree produced by PyNESTMLParser#function.
    def visitFunction(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        parameters = list()
        if type(ctx.parameter()) is list:
            for par in ctx.parameter():
                parameters.append(self.visit(par))
        elif ctx.parameters() is not None:
            parameters.append(ctx.parameter())
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        return_type = self.visit(ctx.returnType) if ctx.returnType is not None else None
        node = ASTNodeFactory.create_ast_function(name=name, parameters=parameters, block=block,
                                                  return_type=return_type, source_position=create_source_pos(ctx))
        update_node_comments(node, self.__comments.visit(ctx))
        return node

    # Visit a parse tree produced by PyNESTMLParser#parameter.
    def visitParameter(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        data_type = self.visit(ctx.dataType()) if ctx.dataType() is not None else None
        return ASTNodeFactory.create_ast_parameter(name=name, data_type=data_type,
                                                   source_position=create_source_pos(ctx))

    # Visit a parse tree produced by PyNESTMLParser#stmt.
    def visitStmt(self, ctx):
        small = self.visit(ctx.smallStmt()) if ctx.smallStmt() is not None else None
        compound = self.visit(ctx.compoundStmt()) if ctx.compoundStmt() is not None else None
        return ASTNodeFactory.create_ast_stmt(small, compound, create_source_pos(ctx))


def update_node_comments(node, comments):
    node.comment = comments[0]
    node.pre_comments = comments[1]
    node.in_comment = comments[2]
    node.post_comments = comments[3]


def get_next(_elements=list()):
    """
    This method is used to get the next element according to its source position.
    :type _elements: a list of elements
    :return: the next element
    :rtype: object
    """
    current_first = None
    for elem in _elements:
        if current_first is None or current_first.start.line > elem.start.line:
            current_first = elem
    return current_first


def create_source_pos(ctx):
    """
    Returns a new source location object. Used in order to avoid code duplication.
    :param ctx: a context variable
    :return: ctx
    """
    return ASTSourceLocation.make_ast_source_position(start_line=ctx.start.line,
                                                      start_column=ctx.start.column,
                                                      end_line=ctx.stop.line,
                                                      end_column=ctx.stop.column)
