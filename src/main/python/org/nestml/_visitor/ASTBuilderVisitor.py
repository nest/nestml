"""
@author kperun
TODO header
"""
import sys

sys.path.append('../../../../../build/src/main/grammars/org')
sys.path.append('../ast')

from antlr4 import *
# import all ASTClasses
from ASTArithmeticOperator import ASTArithmeticOperator
from ASTAssignment import ASTAssignment
from ASTBitOperator import ASTBitOperator
from ASTBlock import ASTBlock
from ASTBody import ASTBody
from ASTComparisonOperator import ASTComparisonOperator
from ASTCompound_Stmt import ASTCompound_Stmt
from ASTDatatype import ASTDatatype
from ASTDeclaration import ASTDeclaration
from ASTDerivative import ASTDerivative
from ASTDynamics import ASTDynamics
from ASTELIF_Clause import ASTELIF_Clause
from ASTELSE_Clause import ASTELSE_Clause
from ASTEquation import ASTEquation
from ASTEquations import ASTEquations
from ASTExpression import ASTExpression
from ASTFOR_Stmt import ASTFOR_Stmt
from ASTFunction import ASTFunction
from ASTFunctionCall import ASTFunctionCall
from ASTIF_Clause import ASTIF_Clause
from ASTIF_Stmt import ASTIF_Stmt
from ASTInput import ASTInput
from ASTInputLine import ASTInputLine
from ASTInputType import ASTInputType
from ASTLogicalOperator import ASTLogicalOperator
from ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
from ASTNeuron import ASTNeuron
from ASTOdeDeclaration import ASTOdeDeclaration
from ASTOdeFunction import ASTOdeFunction
from ASTOutput import ASTOutput
from ASTParameter import ASTParameter
from ASTParameters import ASTParameters
from ASTReturnStmt import ASTReturnStmt
from ASTShape import ASTShape
from ASTSimpleExpression import ASTSimpleExpression
from ASTSmall_Stmt import ASTSmall_Stmt
from ASTStmt import ASTStmt
from ASTUnaryOperator import ASTUnaryOperator
from ASTUnitType import ASTUnitType
from ASTVar_Block import ASTVar_Block
from ASTVariable import ASTVariable
from ASTWHILE_Stmt import ASTWHILE_Stmt
# import lexer and parser
from PyNESTMLVisitor import PyNESTMLVisitor
from PyNESTMLParser import PyNESTMLParser


class ASTBuilderVisitor(ParseTreeVisitor):
    """
    This class is used to create an internal representation of the model by means of an abstract syntax tree.
    """

    # Visit a parse tree produced by PyNESTMLParser#nestmlCompilationUnit.
    def visitNestmlCompilationUnit(self, ctx: PyNESTMLParser.NestmlCompilationUnitContext):
        return ASTNESTMLCompilationUnit.makeASTNESTMLCompilationUnit(self.visitChildren(ctx))

    # Visit a parse tree produced by PyNESTMLParser#datatype.
    def visitDatatype(self, ctx: PyNESTMLParser.DatatypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#unitType.
    def visitUnitType(self, ctx: PyNESTMLParser.UnitTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#expression.
    def visitExpression(self, ctx: PyNESTMLParser.ExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#simpleExpression.
    def visitSimpleExpression(self, ctx: PyNESTMLParser.SimpleExpressionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#unaryOperator.
    def visitUnaryOperator(self, ctx: PyNESTMLParser.UnaryOperatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#bitOperator.
    def visitBitOperator(self, ctx: PyNESTMLParser.BitOperatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#comparisonOperator.
    def visitComparisonOperator(self, ctx: PyNESTMLParser.ComparisonOperatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#logicalOperator.
    def visitLogicalOperator(self, ctx: PyNESTMLParser.LogicalOperatorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#variable.
    def visitVariable(self, ctx: PyNESTMLParser.VariableContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#functionCall.
    def visitFunctionCall(self, ctx: PyNESTMLParser.FunctionCallContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#arguments.
    def visitArguments(self, ctx: PyNESTMLParser.ArgumentsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#odeDeclaration.
    def visitOdeDeclaration(self, ctx: PyNESTMLParser.OdeDeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#odeFunction.
    def visitOdeFunction(self, ctx: PyNESTMLParser.OdeFunctionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#equation.
    def visitEquation(self, ctx: PyNESTMLParser.EquationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#derivative.
    def visitDerivative(self, ctx: PyNESTMLParser.DerivativeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#shape.
    def visitShape(self, ctx: PyNESTMLParser.ShapeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#block.
    def visitBlock(self, ctx: PyNESTMLParser.BlockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#stmt.
    def visitStmt(self, ctx: PyNESTMLParser.StmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#compound_Stmt.
    def visitCompound_Stmt(self, ctx: PyNESTMLParser.Compound_StmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#small_Stmt.
    def visitSmall_Stmt(self, ctx: PyNESTMLParser.Small_StmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#assignment.
    def visitAssignment(self, ctx: PyNESTMLParser.AssignmentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#declaration.
    def visitDeclaration(self, ctx: PyNESTMLParser.DeclarationContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#returnStmt.
    def visitReturnStmt(self, ctx: PyNESTMLParser.ReturnStmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#if_Stmt.
    def visitIf_Stmt(self, ctx: PyNESTMLParser.If_StmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#if_Clause.
    def visitIf_Clause(self, ctx: PyNESTMLParser.If_ClauseContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#elif_Clause.
    def visitElif_Clause(self, ctx: PyNESTMLParser.Elif_ClauseContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#else_Clause.
    def visitElse_Clause(self, ctx: PyNESTMLParser.Else_ClauseContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#for_Stmt.
    def visitFor_Stmt(self, ctx: PyNESTMLParser.For_StmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#while_Stmt.
    def visitWhile_Stmt(self, ctx: PyNESTMLParser.While_StmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#signedNumericLiteral.
    def visitSignedNumericLiteral(self, ctx: PyNESTMLParser.SignedNumericLiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#neuron.
    def visitNeuron(self, ctx: PyNESTMLParser.NeuronContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#body.
    def visitBody(self, ctx: PyNESTMLParser.BodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#var_Block.
    def visitVar_Block(self, ctx: PyNESTMLParser.Var_BlockContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#dynamics.
    def visitDynamics(self, ctx: PyNESTMLParser.DynamicsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#equations.
    def visitEquations(self, ctx: PyNESTMLParser.EquationsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#inputBuffer.
    def visitInputBuffer(self, ctx: PyNESTMLParser.InputBufferContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#inputLine.
    def visitInputLine(self, ctx: PyNESTMLParser.InputLineContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#inputType.
    def visitInputType(self, ctx: PyNESTMLParser.InputTypeContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#outputBuffer.
    def visitOutputBuffer(self, ctx: PyNESTMLParser.OutputBufferContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#function.
    def visitFunction(self, ctx: PyNESTMLParser.FunctionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#parameters.
    def visitParameters(self, ctx: PyNESTMLParser.ParametersContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#parameter.
    def visitParameter(self, ctx: PyNESTMLParser.ParameterContext):
        return self.visitChildren(ctx)
