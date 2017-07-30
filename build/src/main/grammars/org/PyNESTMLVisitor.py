# Generated from src/main/grammars/org/PyNESTML.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .PyNESTMLParser import PyNESTMLParser
else:
    from PyNESTMLParser import PyNESTMLParser

# This class defines a complete generic visitor for a parse tree produced by PyNESTMLParser.

class PyNESTMLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PyNESTMLParser#variable.
    def visitVariable(self, ctx:PyNESTMLParser.VariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#expression.
    def visitExpression(self, ctx:PyNESTMLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#simpleExpression.
    def visitSimpleExpression(self, ctx:PyNESTMLParser.SimpleExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#compoundExpression.
    def visitCompoundExpression(self, ctx:PyNESTMLParser.CompoundExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#arithmeticExpression.
    def visitArithmeticExpression(self, ctx:PyNESTMLParser.ArithmeticExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#logicalExpression.
    def visitLogicalExpression(self, ctx:PyNESTMLParser.LogicalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#functionCall.
    def visitFunctionCall(self, ctx:PyNESTMLParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNESTMLParser#parameter.
    def visitParameter(self, ctx:PyNESTMLParser.ParameterContext):
        return self.visitChildren(ctx)



del PyNESTMLParser