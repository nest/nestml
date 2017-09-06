# Generated from pynestml/src/main/grammars/org/PyNESTML.g4 by ANTLR 4.5.1
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by PyNESTMLParser.

class PyNESTMLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PyNESTMLParser#nestmlCompilationUnit.
    def visitNestmlCompilationUnit(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#datatype.
    def visitDatatype(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#unitType.
    def visitUnitType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#expression.
    def visitExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#simpleExpression.
    def visitSimpleExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#unaryOperator.
    def visitUnaryOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#bitOperator.
    def visitBitOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#comparisonOperator.
    def visitComparisonOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#logicalOperator.
    def visitLogicalOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#variable.
    def visitVariable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#functionCall.
    def visitFunctionCall(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#arguments.
    def visitArguments(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#odeDeclaration.
    def visitOdeDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#odeFunction.
    def visitOdeFunction(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#equation.
    def visitEquation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#derivative.
    def visitDerivative(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#differentialOrder.
    def visitDifferentialOrder(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#shape.
    def visitShape(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#block.
    def visitBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#stmt.
    def visitStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#compound_Stmt.
    def visitCompound_Stmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#small_Stmt.
    def visitSmall_Stmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#assignment.
    def visitAssignment(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#declaration.
    def visitDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#returnStmt.
    def visitReturnStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#if_Stmt.
    def visitIf_Stmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#if_Clause.
    def visitIf_Clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#elif_Clause.
    def visitElif_Clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#else_Clause.
    def visitElse_Clause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#for_Stmt.
    def visitFor_Stmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#while_Stmt.
    def visitWhile_Stmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#signedNumericLiteral.
    def visitSignedNumericLiteral(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#neuron.
    def visitNeuron(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#body.
    def visitBody(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#var_Block.
    def visitVar_Block(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#dynamics.
    def visitDynamics(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#equations.
    def visitEquations(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#inputBuffer.
    def visitInputBuffer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#inputLine.
    def visitInputLine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#inputType.
    def visitInputType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#outputBuffer.
    def visitOutputBuffer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#function.
    def visitFunction(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#parameters.
    def visitParameters(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#parameter.
    def visitParameter(self, ctx):
        return self.visitChildren(ctx)


