# Generated from PyNestMLParser.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .PyNestMLParser import PyNestMLParser
else:
    from PyNestMLParser import PyNestMLParser

# This class defines a complete generic visitor for a parse tree produced by PyNestMLParser.

class PyNestMLParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PyNestMLParser#dataType.
    def visitDataType(self, ctx:PyNestMLParser.DataTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#unitType.
    def visitUnitType(self, ctx:PyNestMLParser.UnitTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#unitTypeExponent.
    def visitUnitTypeExponent(self, ctx:PyNestMLParser.UnitTypeExponentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#expression.
    def visitExpression(self, ctx:PyNestMLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#simpleExpression.
    def visitSimpleExpression(self, ctx:PyNestMLParser.SimpleExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#unaryOperator.
    def visitUnaryOperator(self, ctx:PyNestMLParser.UnaryOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#bitOperator.
    def visitBitOperator(self, ctx:PyNestMLParser.BitOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#comparisonOperator.
    def visitComparisonOperator(self, ctx:PyNestMLParser.ComparisonOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#logicalOperator.
    def visitLogicalOperator(self, ctx:PyNestMLParser.LogicalOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#variable.
    def visitVariable(self, ctx:PyNestMLParser.VariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#functionCall.
    def visitFunctionCall(self, ctx:PyNestMLParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#inlineExpression.
    def visitInlineExpression(self, ctx:PyNestMLParser.InlineExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#odeEquation.
    def visitOdeEquation(self, ctx:PyNestMLParser.OdeEquationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#kernel.
    def visitKernel(self, ctx:PyNestMLParser.KernelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#block.
    def visitBlock(self, ctx:PyNestMLParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#stmt.
    def visitStmt(self, ctx:PyNestMLParser.StmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#compoundStmt.
    def visitCompoundStmt(self, ctx:PyNestMLParser.CompoundStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#smallStmt.
    def visitSmallStmt(self, ctx:PyNestMLParser.SmallStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#assignment.
    def visitAssignment(self, ctx:PyNestMLParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#declaration.
    def visitDeclaration(self, ctx:PyNestMLParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#declaration_newline.
    def visitDeclaration_newline(self, ctx:PyNestMLParser.Declaration_newlineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#anyDecorator.
    def visitAnyDecorator(self, ctx:PyNestMLParser.AnyDecoratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#namespaceDecoratorNamespace.
    def visitNamespaceDecoratorNamespace(self, ctx:PyNestMLParser.NamespaceDecoratorNamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#namespaceDecoratorName.
    def visitNamespaceDecoratorName(self, ctx:PyNestMLParser.NamespaceDecoratorNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#returnStmt.
    def visitReturnStmt(self, ctx:PyNestMLParser.ReturnStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#ifStmt.
    def visitIfStmt(self, ctx:PyNestMLParser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#ifClause.
    def visitIfClause(self, ctx:PyNestMLParser.IfClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#elifClause.
    def visitElifClause(self, ctx:PyNestMLParser.ElifClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#elseClause.
    def visitElseClause(self, ctx:PyNestMLParser.ElseClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#forStmt.
    def visitForStmt(self, ctx:PyNestMLParser.ForStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#whileStmt.
    def visitWhileStmt(self, ctx:PyNestMLParser.WhileStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#nestMLCompilationUnit.
    def visitNestMLCompilationUnit(self, ctx:PyNestMLParser.NestMLCompilationUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#neuron.
    def visitNeuron(self, ctx:PyNestMLParser.NeuronContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#neuronBody.
    def visitNeuronBody(self, ctx:PyNestMLParser.NeuronBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#synapse.
    def visitSynapse(self, ctx:PyNestMLParser.SynapseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#synapseBody.
    def visitSynapseBody(self, ctx:PyNestMLParser.SynapseBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#onReceiveBlock.
    def visitOnReceiveBlock(self, ctx:PyNestMLParser.OnReceiveBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#blockWithVariables.
    def visitBlockWithVariables(self, ctx:PyNestMLParser.BlockWithVariablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#updateBlock.
    def visitUpdateBlock(self, ctx:PyNestMLParser.UpdateBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#equationsBlock.
    def visitEquationsBlock(self, ctx:PyNestMLParser.EquationsBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#inputBlock.
    def visitInputBlock(self, ctx:PyNestMLParser.InputBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#spikeInputPort.
    def visitSpikeInputPort(self, ctx:PyNestMLParser.SpikeInputPortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#continuousInputPort.
    def visitContinuousInputPort(self, ctx:PyNestMLParser.ContinuousInputPortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#inputQualifier.
    def visitInputQualifier(self, ctx:PyNestMLParser.InputQualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#outputBlock.
    def visitOutputBlock(self, ctx:PyNestMLParser.OutputBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#function.
    def visitFunction(self, ctx:PyNestMLParser.FunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#parameter.
    def visitParameter(self, ctx:PyNestMLParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PyNestMLParser#constParameter.
    def visitConstParameter(self, ctx:PyNestMLParser.ConstParameterContext):
        return self.visitChildren(ctx)



del PyNestMLParser