"""
@author kperun
TODO header
"""

from antlr4 import *
# import all ASTClasses
from pynestml.src.main.python.org.nestml.ast import *
from pynestml.src.main.grammars.org.PyNESTMLVisitor import PyNESTMLVisitor


class ASTBuilderVisitor(ParseTreeVisitor):
    """
    This class is used to create an internal representation of the model by means of an abstract syntax tree.
    """

    # Visit a parse tree produced by PyNESTMLParser#nestmlCompilationUnit.
    def visitNestmlCompilationUnit(self, ctx):
        neurons = list()
        for child in ctx.neuron():
            neurons.append(self.visit(child))
        return ASTNESTMLCompilationUnit.ASTNESTMLCompilationUnit.makeASTNESTMLCompilationUnit(neurons)

    # Visit a parse tree produced by PyNESTMLParser#datatype.
    def visitDatatype(self, ctx):
        isInt = (True if ctx.isInt is not None else False)
        isReal = (True if ctx.isReal is not None else False)
        isString = (True if ctx.isString is not None else False)
        isBool = (True if ctx.isBool is not None else False)
        isVoid = (True if ctx.isVoid is not None else False)
        unit = self.visit(ctx.unitType());
        return ASTDatatype.ASTDatatype.makeASTDatatype(_isInteger=isInt, _isBoolean=isBool,
                                                       _isReal=isReal, _isString=isString, _isVoid=isVoid,
                                                       _isUnitType=unit)

    # Visit a parse tree produced by PyNESTMLParser#unitType.
    def visitUnitType(self, ctx):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by PyNESTMLParser#expression.
    def visitExpression(self, ctx):
        hasLeftParentheses = (True if ctx.leftParentheses is not None else False)
        hasRightParentheses = (True if ctx.rightParentheses is not None else False)
        unaryOperator = (self.visit(ctx.unaryOperator()) if ctx.unaryOperator() is not None else None)
        isLogicalNot = (True if ctx.logicalNot is not None else False)
        if ctx.simpleExpression() is not None:
            expression = self.visit(ctx.simpleExpression())
        elif ctx.term is not None:
            expression = self.visit(ctx.term)
        lhs = (self.visit(ctx.left) if ctx.left is not None else None)
        if ctx.powOp is not None:
            binaryOperator = ASTArithmeticOperator.ASTArithmeticOperator.makeASTArithmeticOperator(_isPowOp=True)
        elif ctx.timesOp is not None:
            binaryOperator = ASTArithmeticOperator.ASTArithmeticOperator.makeASTArithmeticOperator(_isTimesOp=True)
        elif ctx.divOp is not None:
            binaryOperator = ASTArithmeticOperator.ASTArithmeticOperator.makeASTArithmeticOperator(_isDivOp=True)
        elif ctx.moduloOp is not None:
            binaryOperator = ASTArithmeticOperator.ASTArithmeticOperator.makeASTArithmeticOperator(_isModuloOp=True)
        elif ctx.plusOp is not None:
            binaryOperator = ASTArithmeticOperator.ASTArithmeticOperator.makeASTArithmeticOperator(_isPlusOp=True)
        elif ctx.minusOp is not None:
            binaryOperator = ASTArithmeticOperator.ASTArithmeticOperator.makeASTArithmeticOperator(_isMinusOp=True)
        elif ctx.bitOperator() is not None:
            binaryOperator = self.visit(ctx.bitOperator())
        elif ctx.comparisonOperator() is not None:
            binaryOperator = self.visit(ctx.comparisonOperator())
        elif ctx.logicalOperator() is not None:
            binaryOperator = self.visit(ctx.logicalOperator())
        rhs = (self.visit(ctx.right) if ctx.right is not None else None)
        condition = (self.visit(ctx.condition) if ctx.condition is not None else None)
        ifTrue = (self.visit(ctx.ifTrue) if ctx.ifTrue is not None else None)
        ifNot = (self.visit(ctx.ifNot) if ctx.ifNot is not None else None)
        """
        TODO
        return ASTExpression.ASTExpression.makeASTExpression(_hasLeftParentheses=hasLeftParentheses,
                                                             _hasRightParentheses=hasRightParentheses,
                                                             _unaryOperator=unaryOperator, _isLogicalNot=isLogicalNot,
                                                             _expression=expression, _lhs=lhs,
                                                             _binaryOperator=binaryOperator,
                                                             _rhs=rhs, _condition=condition, _ifTrue=ifTrue,
                                                             _ifNot=ifNot)
        """

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
        diffOrder = (int(ctx.differentialOrder) if ctx.differentialOrder is not None else 0)
        return ASTVariable.ASTVariable.makeASTVariable(_name=str(ctx.NAME()),
                                                       _differentialOrder=diffOrder)

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
        isRecordable = (True if ctx.isRecordable is not None else False)
        isFunction = (True if ctx.isFunction is not None else False)
        variables = list()
        for var in ctx.variable():
            variables.append(self.visit(var))
        dataType = self.visit(ctx.datatype())
        sizeParam = str(ctx.NAME())

        """
        TODO
        """
        expression = self.visit(ctx.expression()[0])
        comment = str(ctx.SL_COMMENT())
        invariant = self.visit(ctx.invariant)
        return ASTDeclaration.ASTDeclaration.makeASTDeclaration(_isRecordable=isRecordable, _isFunction=isFunction,
                                                                _variables=variables, _dataType=dataType,
                                                                _sizeParameter=sizeParam,
                                                                _expression=expression, _comment=comment,
                                                                _invariant=invariant)

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
        return ASTNeuron.ASTNeuron.makeASTNeuron(_name=str(ctx.NAME()), _body=self.visit(ctx.body()))

    # Visit a parse tree produced by PyNESTMLParser#body.
    def visitBody(self, ctx):
        body_elements = list()
        # visit all var_block children
        for child in ctx.var_Block():
            body_elements.append(self.visit(child))
        for child in ctx.dynamics():
            body_elements.append(self.visit(child))
        for child in ctx.equations():
            body_elements.append(self.visit(child))
        for child in ctx.inputBuffer():
            body_elements.append(self.visit(child))
        for child in ctx.outputBuffer():
            body_elements.append(self.visit(child))
        for child in ctx.function():
            body_elements.append(self.visit(child))
        return ASTBody.ASTBody.makeASTBody(_bodyElements=body_elements)

    # Visit a parse tree produced by PyNESTMLParser#var_Block.
    def visitVar_Block(self, ctx):
        declarations = list()
        blockType = ctx.blockType.text  # the text field stores the exact name of the token, e.g., state
        for child in ctx.declaration():
            declarations.append(self.visit(child))
        if blockType == 'state':
            return ASTVar_Block.ASTVar_Block.makeASTVar_Block(_isInternals=False, _isParameters=False, _isState=True,
                                                              _declarations=declarations)
        elif blockType == 'parameters':
            return ASTVar_Block.ASTVar_Block.makeASTVar_Block(_isInternals=False, _isParameters=True, _isState=False,
                                                              _declarations=declarations)
        elif blockType == 'internals':
            return ASTVar_Block.ASTVar_Block.makeASTVar_Block(_isInternals=True, _isParameters=False, _isState=True,
                                                              _declarations=declarations)
        else:
            raise UnknownBodyTypeException('(NESTML) Unspecified type (=%s) of var-block.' % str(ctx.blockType))
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


class UnknownBodyTypeException(Exception):
    pass
