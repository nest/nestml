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
        else:
            expression = None
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
        else:
            binaryOperator = None
        rhs = (self.visit(ctx.right) if ctx.right is not None else None)
        condition = (self.visit(ctx.condition) if ctx.condition is not None else None)
        ifTrue = (self.visit(ctx.ifTrue) if ctx.ifTrue is not None else None)
        ifNot = (self.visit(ctx.ifNot) if ctx.ifNot is not None else None)
        if expression is not None:
            return ASTExpression.ASTExpression.makeExpression(_hasLeftParentheses=hasLeftParentheses,
                                                              _hasRightParentheses=hasRightParentheses,
                                                              _isLogicalNot=isLogicalNot,
                                                              _unaryOperator=unaryOperator,
                                                              _expression=expression)
        elif (lhs is not None) and (rhs is not None) and (binaryOperator is not None):
            return ASTExpression.ASTExpression.makeCompoundExpression(_lhs=lhs, _binaryOperator=binaryOperator,
                                                                      _rhs=rhs)
        elif (condition is not None) and (ifTrue is not None) and (ifNot is not None):
            return ASTExpression.ASTExpression.makeTernaryExpression(_condition=condition, _ifTrue=ifTrue, _ifNot=ifNot)
        else:
            raise UnknownExpressionTypeException('(NESTML) Type of expression not recognized.')

    # Visit a parse tree produced by PyNESTMLParser#simpleExpression.
    def visitSimpleExpression(self, ctx):
        functionCall = (self.visit(ctx.functionCall()) if ctx.functionCall() is not None else None)
        name = (str(ctx.NAME()) if ctx.NAME() is not None else None)
        booleanLiteral = ((True if str(
            ctx.BOOLEAN_LITERAL().text) == r'[T|t]rue' else False) if ctx.BOOLEAN_LITERAL() is not None else None)
        numericLiteral = (float(ctx.NUMERIC_LITERAL()) if ctx.NUMERIC_LITERAL() is not None else None)
        isInf = (True if ctx.isInf is not None else False)
        variable = (self.visit(ctx.variable()) if ctx.variable() is not None else False)
        return ASTSimpleExpression.ASTSimpleExpression.makeASTSimpleExpression(_functionCall=functionCall, _name=name,
                                                                               _booleanLiteral=booleanLiteral,
                                                                               _numericLiteral=numericLiteral,
                                                                               _isInf=isInf, _variable=variable)

    # Visit a parse tree produced by PyNESTMLParser#unaryOperator.
    def visitUnaryOperator(self, ctx):
        isUnaryPlus = (True if ctx.unaryPlus is not None else False)
        isUnaryMinus = (True if ctx.unaryMinus is not None else False)
        isUnaryTilde = (True if ctx.unaryTilde is not None else False)
        return ASTUnaryOperator.ASTUnaryOperator.makeASTUnaryOperator(_isUnaryPlus=isUnaryPlus,
                                                                      _isUnaryMinus=isUnaryMinus,
                                                                      _isUnaryTilde=isUnaryTilde)

    # Visit a parse tree produced by PyNESTMLParser#bitOperator.
    def visitBitOperator(self, ctx):
        isBitAnd = (True if ctx.bitAnd is not None else False)
        isBitXor = (True if ctx.bitXor is not None else False)
        isBitOr = (True if ctx.bitOr is not None else False)
        isBitShiftLeft = (True if ctx.bitShiftLeft is not None else False)
        isBitShiftRight = (True if ctx.bitShiftRight is not None else False)
        return ASTBitOperator.ASTBitOperator.makeASTBitOperator(_isBitAnd=isBitAnd, _isBitXor=isBitXor,
                                                                _isBitOr=isBitOr,
                                                                _isBitShiftLeft=isBitShiftLeft,
                                                                _isBitShiftRight=isBitShiftRight)

    # Visit a parse tree produced by PyNESTMLParser#comparisonOperator.
    def visitComparisonOperator(self, ctx):
        isLt = (True if ctx.lt is not None else False)
        isLe = (True if ctx.le is not None else False)
        isEq = (True if ctx.eq is not None else False)
        isNe = (True if ctx.ne is not None else False)
        isNe2 = (True if ctx.ne2 is not None else False)
        isGe = (True if ctx.ge is not None else False)
        isGt = (True if ctx.gt is not None else False)
        return ASTComparisonOperator.ASTComparisonOperator.makeASTComparisonOperator(_isLt=isLt, _isLe=isLe,
                                                                                     _isEq=isEq, _isNe=isNe,
                                                                                     _isNe2=isNe2,
                                                                                     _isGe=isGe, _isGt=isGt)

    # Visit a parse tree produced by PyNESTMLParser#logicalOperator.
    def visitLogicalOperator(self, ctx):
        isLogicalAnd = (True if ctx.logicalAnd is not None else False)
        isLogicalOr = (True if ctx.logicalOr is not None else False)
        return ASTLogicalOperator.ASTLogicalOperator.makeASTLogicalOperator(_isLogicalAnd=isLogicalAnd,
                                                                            _isLogicalOr=isLogicalOr)

    # Visit a parse tree produced by PyNESTMLParser#variable.
    def visitVariable(self, ctx):
        differentialOrder = (len(ctx.differentialOrder) if ctx.differentialOrder is not None else 0)
        return ASTVariable.ASTVariable.makeASTVariable(_name=str(ctx.NAME()),
                                                       _differentialOrder=differentialOrder)

    # Visit a parse tree produced by PyNESTMLParser#functionCall.
    def visitFunctionCall(self, ctx):
        name = (str(ctx.calleeName))
        args = (self.visit(ctx.args) if ctx.args is not None else list())
        return ASTFunctionCall.ASTFunctionCall.makeASTFunctionCall(_calleeName=name, _args=args)

    # Visit a parse tree produced by PyNESTMLParser#arguments.
    def visitArguments(self, ctx):
        args = list()
        if ctx.expression() is not None:
            for arg in ctx.expression():
                args.append(self.visit(arg))
        return args

    # Visit a parse tree produced by PyNESTMLParser#odeDeclaration.
    def visitOdeDeclaration(self, ctx):
        equations = list()
        if ctx.equation() is not None:
            for eq in ctx.equation():
                equations.append(self.visit(eq))
        shapes = list()
        if ctx.shape() is not None:
            for shape in ctx.shape():
                shapes.append(self.visit(shape))
        odeFunctions = list()
        if ctx.odeFunction() is not None:
            for fun in ctx.odeFunction():
                equations.append(self.visit(fun))
        return ASTOdeDeclaration.ASTOdeDeclaration.makeASTOdeDeclaration(_equations=equations, _shapes=shape,
                                                                         _odeFunctions=odeFunctions)

    # Visit a parse tree produced by PyNESTMLParser#odeFunction.
    def visitOdeFunction(self, ctx):
        isRecordable = (True if ctx.recordable is not None else False)
        variableName = (str(ctx.variableName) if ctx.variableName is not None else None)
        dataType = (self.visit(ctx.datatype()) if ctx.datatype() is not None else None)
        expression = (self.visit(ctx.expression()) if ctx.expression() is not None else None)
        return ASTOdeFunction.ASTOdeFunction.makeASTOdeFunction(_isRecordable=isRecordable, _variableName=variableName,
                                                                _dataType=dataType,
                                                                _expression=expression)

    # Visit a parse tree produced by PyNESTMLParser#equation.
    def visitEquation(self, ctx):
        lhs = self.visit(ctx.lhs) if ctx.lhs is not None else None
        rhs = self.visit(ctx.rhs) if ctx.rhs is not None else None
        return ASTEquation.ASTEquation.makeASTEquation(_lhs=lhs, _rhs=rhs)

    # Visit a parse tree produced by PyNESTMLParser#derivative.
    def visitDerivative(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        differentialOrder = len(ctx.differentialOrder) if ctx.differentialOrder is not None else 0
        return ASTDerivative.ASTDerivative.makeASTDerivative(_name=name, _differentialOrder=differentialOrder)

    # Visit a parse tree produced by PyNESTMLParser#shape.
    def visitShape(self, ctx):
        lhs = self.visit(ctx.lhs) if ctx.lhs is not None else None
        rhs = self.visit(ctx.rhs) if ctx.rhs is not None else None
        return ASTShape.ASTShape.makeASTShape(_lhs=lhs, _rhs=rhs)

    # Visit a parse tree produced by PyNESTMLParser#block.
    def visitBlock(self, ctx):
        stmts = list()
        if ctx.stmt() is not None:
            for stmt in ctx.stmt():
                stmts.append(self.visit(stmt))
        return ASTBlock.ASTBlock.makeASTBlock(_stmts=stmts)

    # Visit a parse tree produced by PyNESTMLParser#stmt.
    def visitStmt(self, ctx):
        small = self.visit(ctx.small_Stmt()) if ctx.small_Stmt() is not None else None
        compound = self.visit(ctx.compound_Stmt()) if ctx.compound_Stmt() is not None else None
        return ASTStmt.ASTStmt.makeASTStmt(_small_statement=small, _compound_statement=compound)

    # Visit a parse tree produced by PyNESTMLParser#compound_Stmt.
    def visitCompound_Stmt(self, ctx):
        ifStmt = self.visit(ctx.if_Stmt()) if ctx.if_Stmt() is not None else None
        whileStmt = self.visit(ctx.while_Stmt()) if ctx.while_Stmt() is not None else None
        forStmt = self.visit(ctx.for_Stmt()) if ctx.for_Stmt() is not None else None
        return ASTCompound_Stmt.ASTCompound_Stmt.makeASTCompound_Stmt(_if_stmt=ifStmt, _while_stmt=whileStmt,
                                                                      _for_stmt=forStmt)

    # Visit a parse tree produced by PyNESTMLParser#small_Stmt.
    def visitSmall_Stmt(self, ctx):
        assignment = self.visit(ctx.assignment()) if ctx.assignment() is not None else None
        functionCall = self.visit(ctx.functionCall()) if ctx.functionCall() is not None else None
        declaration = self.visit(ctx.declaration()) if ctx.declaration() is not None else None
        returnStmt = self.visit(ctx.returnStmt()) if ctx.returnStmt() is not None else None
        return ASTSmall_Stmt.ASTSmall_Stmt.makeASTSmall_Stmt(_assignment=assignment, _functionCall=functionCall,
                                                             _declaration=declaration, _returnStmt=returnStmt)

    # Visit a parse tree produced by PyNESTMLParser#assignment.
    def visitAssignment(self, ctx):
        lhs = self.visit(ctx.lhsVariable) if ctx.lhsVariable is not None else None
        isDirectAssignment = True if ctx.directAssignment is not None else False
        isCompoundSum = True if ctx.compoundSum is not None else False
        isCompoundMinus = True if ctx.compoundMinus is not None else False
        isCompoundProduct = True if ctx.compoundProduct is not None else False
        isCompoundQuotient = True if ctx.compoundQuotient is not None else False
        expression = self.visit(ctx.expression()) if ctx.expression() is not None else None
        return ASTAssignment.ASTAssignment.makeASTAssignment(_lhs=lhs, _isDirectAssignment=isDirectAssignment,
                                                             _isCompoundSum=isCompoundSum,
                                                             _isCompoundMinus=isCompoundMinus,
                                                             _isCompoundProduct=isCompoundProduct,
                                                             _isCompoundQuotient=isCompoundQuotient,
                                                             _expression=expression)

    # Visit a parse tree produced by PyNESTMLParser#declaration.
    def visitDeclaration(self, ctx):
        isRecordable = (True if ctx.isRecordable is not None else False)
        isFunction = (True if ctx.isFunction is not None else False)
        variables = list()
        for var in ctx.variable():
            variables.append(self.visit(var))
        dataType = self.visit(ctx.datatype()) if ctx.datatype() is not None else None
        sizeParam = str(ctx.NAME()) if ctx.NAME() is not None else None
        expression = self.visit(ctx.expression()[0]) if ctx.expression() is not None else None
        comment = str(ctx.SL_COMMENT()) if ctx.SL_COMMENT() is not None else None
        invariant = self.visit(ctx.invariant) if ctx.invariant is not None else None
        return ASTDeclaration.ASTDeclaration.makeASTDeclaration(_isRecordable=isRecordable, _isFunction=isFunction,
                                                                _variables=variables, _dataType=dataType,
                                                                _sizeParameter=sizeParam,
                                                                _expression=expression, _comment=comment,
                                                                _invariant=invariant)

    # Visit a parse tree produced by PyNESTMLParser#returnStmt.
    def visitReturnStmt(self, ctx):
        retExpression = self.visit(ctx.expression()) if ctx.expression() is not None else None
        return ASTReturnStmt.ASTReturnStmt.makeASTReturnStmt(_expression=retExpression)

    # Visit a parse tree produced by PyNESTMLParser#if_Stmt.
    def visitIf_Stmt(self, ctx):
        ifClause = self.visit(ctx.if_Clause()) if ctx.if_Clause() is not None else None
        elifClauses = list()
        if ctx.elif_Clause() is not None:
            for clause in ctx.elif_Clause():
                elifClauses.append(self.visit(clause))
        elseClause = self.visit(ctx.else_Clause()) if ctx.else_Clause() is not None else None
        return ASTIF_Stmt.ASTIF_Stmt.makeASTIF_Stmt(_ifClause=ifClause, _elifClauses=elifClauses,
                                                    _elseClause=elseClause)

    # Visit a parse tree produced by PyNESTMLParser#if_Clause.
    def visitIf_Clause(self, ctx):
        condition = self.visit(ctx.expression()) if ctx.expression() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        return ASTIF_Clause.ASTIF_Clause.makeASTIF_Clause(_condition=condition, _block=block)

    # Visit a parse tree produced by PyNESTMLParser#elif_Clause.
    def visitElif_Clause(self, ctx):
        condition = self.visit(ctx.expression()) if ctx.expression() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        return ASTELIF_Clause.ASTELIF_Clause.makeASTELIF_Clause(_condition=condition, _block=block)

    # Visit a parse tree produced by PyNESTMLParser#else_Clause.
    def visitElse_Clause(self, ctx):
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        return ASTELSE_Clause.ASTELSE_Clause.makeASTELSE_Clause(_block=block)

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


class UnknownExpressionTypeException(Exception):
    pass
