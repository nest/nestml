# Generated from pynestml/src/main/grammars/org/PyNESTML.g4 by ANTLR 4.7
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by PyNESTMLParser.

class PyNESTMLVisitor(ParseTreeVisitor):

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


    # Visit a parse tree produced by PyNESTMLParser#odeFunction.
    def visitOdeFunction(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#odeEquation.
    def visitOdeEquation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#derivative.
    def visitDerivative(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#differentialOrder.
    def visitDifferentialOrder(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#odeShape.
    def visitOdeShape(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#block.
    def visitBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#stmt.
    def visitStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#compoundStmt.
    def visitCompoundStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#smallStmt.
    def visitSmallStmt(self, ctx):
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


    # Visit a parse tree produced by PyNESTMLParser#ifStmt.
    def visitIfStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#ifClause.
    def visitIfClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#elifClause.
    def visitElifClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#elseClause.
    def visitElseClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#forStmt.
    def visitForStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#whileStmt.
    def visitWhileStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#signedNumericLiteral.
    def visitSignedNumericLiteral(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#nestmlCompilationUnit.
    def visitNestmlCompilationUnit(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#neuron.
    def visitNeuron(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#body.
    def visitBody(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#blockWithVariables.
    def visitBlockWithVariables(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#updateBlock.
    def visitUpdateBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#equationsBlock.
    def visitEquationsBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#inputBlock.
    def visitInputBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#inputLine.
    def visitInputLine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#inputType.
    def visitInputType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#outputBlock.
    def visitOutputBlock(self, ctx):
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


