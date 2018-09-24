# Generated from PyNestML.g4 by ANTLR 4.7.1
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by PyNestML.

class PyNestMLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PyNestML#dataType.
    def visitDataType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#unitType.
    def visitUnitType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#expression.
    def visitExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#simpleExpression.
    def visitSimpleExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#unaryOperator.
    def visitUnaryOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#bitOperator.
    def visitBitOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#comparisonOperator.
    def visitComparisonOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#logicalOperator.
    def visitLogicalOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#variable.
    def visitVariable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#functionCall.
    def visitFunctionCall(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#odeFunction.
    def visitOdeFunction(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#odeEquation.
    def visitOdeEquation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#odeShape.
    def visitOdeShape(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#block.
    def visitBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#stmt.
    def visitStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#compoundStmt.
    def visitCompoundStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#smallStmt.
    def visitSmallStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#assignment.
    def visitAssignment(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#declaration.
    def visitDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#returnStmt.
    def visitReturnStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#ifStmt.
    def visitIfStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#ifClause.
    def visitIfClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#elifClause.
    def visitElifClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#elseClause.
    def visitElseClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#forStmt.
    def visitForStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#whileStmt.
    def visitWhileStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#nestMLCompilationUnit.
    def visitNestMLCompilationUnit(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#neuron.
    def visitNeuron(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#body.
    def visitBody(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#blockWithVariables.
    def visitBlockWithVariables(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#updateBlock.
    def visitUpdateBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#equationsBlock.
    def visitEquationsBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#inputBlock.
    def visitInputBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#inputLine.
    def visitInputLine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#inputType.
    def visitInputType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#outputBlock.
    def visitOutputBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#function.
    def visitFunction(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestML#parameter.
    def visitParameter(self, ctx):
        return self.visitChildren(ctx)


