# Generated from PyNestMLParser.g4 by ANTLR 4.9
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by PyNestMLParser.

class PyNestMLParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PyNestMLParser#dataType.
    def visitDataType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#unitType.
    def visitUnitType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#unitTypeExponent.
    def visitUnitTypeExponent(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#expression.
    def visitExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#simpleExpression.
    def visitSimpleExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#unaryOperator.
    def visitUnaryOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#bitOperator.
    def visitBitOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#comparisonOperator.
    def visitComparisonOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#logicalOperator.
    def visitLogicalOperator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#variable.
    def visitVariable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#functionCall.
    def visitFunctionCall(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#inlineExpression.
    def visitInlineExpression(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#odeEquation.
    def visitOdeEquation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#kernel.
    def visitKernel(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#block.
    def visitBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#stmt.
    def visitStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#compoundStmt.
    def visitCompoundStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#smallStmt.
    def visitSmallStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#assignment.
    def visitAssignment(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#declaration.
    def visitDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#returnStmt.
    def visitReturnStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#ifStmt.
    def visitIfStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#ifClause.
    def visitIfClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#elifClause.
    def visitElifClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#elseClause.
    def visitElseClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#forStmt.
    def visitForStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#whileStmt.
    def visitWhileStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#nestMLCompilationUnit.
    def visitNestMLCompilationUnit(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#neuron.
    def visitNeuron(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#body.
    def visitBody(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#blockWithVariables.
    def visitBlockWithVariables(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#updateBlock.
    def visitUpdateBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#equationsBlock.
    def visitEquationsBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#inputBlock.
    def visitInputBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#inputPort.
    def visitInputPort(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#inputQualifier.
    def visitInputQualifier(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#outputBlock.
    def visitOutputBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#function.
    def visitFunction(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#parameter.
    def visitParameter(self, ctx):
        return self.visitChildren(ctx)


