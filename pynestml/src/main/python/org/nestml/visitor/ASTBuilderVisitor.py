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
        unit = self.visit(ctx.unitType()) if ctx.unitType() is not None else None
        return ASTDatatype.ASTDatatype.makeASTDatatype(_isInteger=isInt, _isBoolean=isBool,
                                                       _isReal=isReal, _isString=isString, _isVoid=isVoid,
                                                       _isUnitType=unit)

    # Visit a parse tree produced by PyNESTMLParser#unitType.
    def visitUnitType(self, ctx):
        leftParenthesis = True if ctx.leftParentheses is not None else False
        compoundUnit = self.visit(ctx.compoundUnit) if ctx.compoundUnit is not None else None
        rightParenthesis = True if ctx.rightParentheses is not None else False
        base = self.visit(ctx.base) if ctx.base is not None else None
        isPow = True if ctx.powOp is not None else False
        exponent = int(str(ctx.exponent)) if ctx.exponent is not None else None
        lhs = (
            int(str(ctx.left)) if str(ctx.left).isdigit() else self.visit(ctx.left)) if ctx.left is not None else None
        isTimes = True if ctx.timesOp is not None else False
        isDiv = True if ctx.divOp is not None else False
        rhs = self.visit(ctx.right) if ctx.right is not None else None
        unit = str(ctx.unit.text) if ctx.unit is not None else None

        return ASTUnitType.ASTUnitType.makeASTUnitType(_leftParentheses=leftParenthesis, _compoundUnit=compoundUnit,
                                                       _rightParentheses=rightParenthesis, _base=base, _isPow=isPow,
                                                       _exponent=exponent, _lhs=lhs, _rhs=rhs, _isDiv=isDiv,
                                                       _isTimes=isTimes, _unit=unit)

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
            sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.powOp.line,
                                                                                  _startColumn=ctx.powOp.column,
                                                                                  _endLine=ctx.powOp.line,
                                                                                  _endColumn=ctx.powOp.column)
            binaryOperator = ASTArithmeticOperator. \
                ASTArithmeticOperator.makeASTArithmeticOperator(_isPowOp=True, _sourcePosition=sourcePos)
        elif ctx.timesOp is not None:
            sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.timesOp.line,
                                                                                  _startColumn=ctx.timesOp.column,
                                                                                  _endLine=ctx.timesOp.line,
                                                                                  _endColumn=ctx.timesOp.column)
            binaryOperator = ASTArithmeticOperator. \
                ASTArithmeticOperator.makeASTArithmeticOperator(_isTimesOp=True, _sourcePosition=sourcePos)
        elif ctx.divOp is not None:
            sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.divOp.line,
                                                                                  _startColumn=ctx.divOp.column,
                                                                                  _endLine=ctx.divOp.line,
                                                                                  _endColumn=ctx.divOp.column)
            binaryOperator = ASTArithmeticOperator. \
                ASTArithmeticOperator.makeASTArithmeticOperator(_isDivOp=True, _sourcePosition=sourcePos)
        elif ctx.moduloOp is not None:
            sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.moduloOp.line,
                                                                                  _startColumn=ctx.moduloOp.column,
                                                                                  _endLine=ctx.moduloOp.line,
                                                                                  _endColumn=ctx.moduloOp.column)
            binaryOperator = ASTArithmeticOperator. \
                ASTArithmeticOperator.makeASTArithmeticOperator(_isModuloOp=True, _sourcePosition=sourcePos)
        elif ctx.plusOp is not None:
            sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.plusOp.line,
                                                                                  _startColumn=ctx.plusOp.column,
                                                                                  _endLine=ctx.plusOp.line,
                                                                                  _endColumn=ctx.plusOp.column)
            binaryOperator = ASTArithmeticOperator. \
                ASTArithmeticOperator.makeASTArithmeticOperator(_isPlusOp=True, _sourcePosition=sourcePos)
        elif ctx.minusOp is not None:
            sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.minusOp.line,
                                                                                  _startColumn=ctx.minusOp.column,
                                                                                  _endLine=ctx.minusOp.line,
                                                                                  _endColumn=ctx.minusOp.column)
            binaryOperator = ASTArithmeticOperator. \
                ASTArithmeticOperator.makeASTArithmeticOperator(_isMinusOp=True, _sourcePosition=sourcePos)
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
            raise PyNESTMLUnknownExpressionTypeException('(NESTML.ASTBuilder) Type of expression not recognized.')

    # Visit a parse tree produced by PyNESTMLParser#simpleExpression.
    def visitSimpleExpression(self, ctx):
        functionCall = (self.visit(ctx.functionCall()) if ctx.functionCall() is not None else None)
        name = (str(ctx.NAME()) if ctx.NAME() is not None else None)
        booleanLiteral = ((True if str(
            ctx.BOOLEAN_LITERAL()) == r'[T|t]rue' else False) if ctx.BOOLEAN_LITERAL() is not None else None)
        numericLiteral = (float(str(ctx.NUMERIC_LITERAL()))
                          if ctx.NUMERIC_LITERAL() is not None else None)
        isInf = (True if ctx.isInf is not None else False)
        variable = (self.visit(ctx.variable()) if ctx.variable() is not None else None)
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
        differentialOrder = (len(ctx.differentialOrder()) if ctx.differentialOrder() is not None else 0)
        return ASTVariable.ASTVariable.makeASTVariable(_name=str(ctx.NAME()),
                                                       _differentialOrder=differentialOrder)

    # Visit a parse tree produced by PyNESTMLParser#functionCall.
    def visitFunctionCall(self, ctx):
        name = (str(ctx.calleeName.text))
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
        "In order to preserve the order we use the getNext() method to get the next element\
         according to the source position."
        elems = list()
        if ctx.equation() is not None:
            for eq in ctx.equation():
                elems.append(eq)
        if ctx.shape() is not None:
            for shape in ctx.shape():
                elems.append(shape)
        if ctx.odeFunction() is not None:
            for fun in ctx.odeFunction():
                elems.append(fun)
        ordered = list()
        while len(elems) > 0:
            elem = self.getNext(elems)
            ordered.append(self.visit(elem))
            elems.remove(elem)
        return ASTOdeDeclaration.ASTOdeDeclaration.makeASTOdeDeclaration(_elements=ordered)

    # Visit a parse tree produced by PyNESTMLParser#odeFunction.
    def visitOdeFunction(self, ctx):
        isRecordable = (True if ctx.recordable is not None else False)
        variableName = (str(ctx.variableName.text) if ctx.variableName is not None else None)
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
        differentialOrder = len(ctx.differentialOrder()) if ctx.differentialOrder is not None else 0
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
        expression = self.visit(ctx.rhs) if ctx.rhs is not None else None
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
        variable = str(ctx.NAME()) if ctx.NAME() is not None else None
        From = self.visit(ctx.vrom) if ctx.vrom is not None else None
        to = self.visit(ctx.to) if ctx.to is not None else None
        step = self.visit(ctx.step) if ctx.step is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        return ASTFOR_Stmt.ASTFOR_Stmt.makeASTFOR_Stmt(_variable=variable, _from=From, _to=to, _step=step, _block=block)

    # Visit a parse tree produced by PyNESTMLParser#while_Stmt.
    def visitWhile_Stmt(self, ctx):
        cond = self.visit(ctx.expression()) if ctx.expression() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        return ASTWHILE_Stmt.ASTWHILE_Stmt.makeASTWHILE_Stmt(_condition=cond, _block=block)

    # Visit a parse tree produced by PyNESTMLParser#signedNumericLiteral.
    def visitSignedNumericLiteral(self, ctx):
        isNeg = True if ctx.negative is not None else False
        value = float(ctx.NUMERIC_LITERAL()) if ctx.NUMERIC_LITERAL() is not None else 0
        if isNeg:
            return -value
        else:
            return value

    # Visit a parse tree produced by PyNESTMLParser#neuron.
    def visitNeuron(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        body = self.visit(ctx.body()) if ctx.body() is not None else None
        return ASTNeuron.ASTNeuron.makeASTNeuron(_name=name, _body=body)

    # Visit a parse tree produced by PyNESTMLParser#body.
    def visitBody(self, ctx):
        "Here, in order to ensure that the correct order of elements is kept, we use a method which inspects \
        a list of elements and returns the one with the smallest source line."
        body_elements = list()
        # visit all var_block children
        if ctx.var_Block() is not None:
            for child in ctx.var_Block():
                body_elements.append(child)
        if ctx.dynamics() is not None:
            for child in ctx.dynamics():
                body_elements.append(child)
        if ctx.equations() is not None:
            for child in ctx.equations():
                body_elements.append(child)
        if ctx.inputBuffer() is not None:
            for child in ctx.inputBuffer():
                body_elements.append(child)
        if ctx.outputBuffer() is not None:
            for child in ctx.outputBuffer():
                body_elements.append(child)
        if ctx.function() is not None:
            for child in ctx.function():
                body_elements.append(child)
        elements = list()
        while len(body_elements) > 0:
            elem = self.getNext(body_elements)
            elements.append(self.visit(elem))
            body_elements.remove(elem)
        return ASTBody.ASTBody.makeASTBody(_bodyElements=elements)

    # Visit a parse tree produced by PyNESTMLParser#var_Block.
    def visitVar_Block(self, ctx):
        declarations = list()
        if ctx.declaration() is not None:
            for child in ctx.declaration():
                declarations.append(self.visit(child))
        blockType = ctx.blockType.text  # the text field stores the exact name of the token, e.g., state
        if blockType == 'state':
            return ASTVar_Block.ASTVar_Block.makeASTVar_Block(_isInternals=False, _isParameters=False, _isState=True,
                                                              _declarations=declarations)
        elif blockType == 'parameters':
            return ASTVar_Block.ASTVar_Block.makeASTVar_Block(_isInternals=False, _isParameters=True, _isState=False,
                                                              _declarations=declarations)
        elif blockType == 'internals':
            return ASTVar_Block.ASTVar_Block.makeASTVar_Block(_isInternals=True, _isParameters=False, _isState=False,
                                                              _declarations=declarations)
        else:
            raise PyNESTMLUnknownBodyTypeException(
                '(NESTML.ASTBuilder) Unspecified type (=%s) of var-block.' % str(ctx.blockType))
            # Visit a parse tree produced by PyNESTMLParser#dynamics.

    def visitDynamics(self, ctx):
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        return ASTDynamics.ASTDynamics.makeASTDynamics(_block=block)

    # Visit a parse tree produced by PyNESTMLParser#equations.
    def visitEquations(self, ctx):
        odeDecl = self.visit(ctx.odeDeclaration()) if ctx.odeDeclaration() is not None else None
        return ASTEquations.ASTEquations.makeASTEquations(_block=odeDecl)

    # Visit a parse tree produced by PyNESTMLParser#inputBuffer.
    def visitInputBuffer(self, ctx):
        inputLines = list()
        if ctx.inputLine() is not None:
            for line in ctx.inputLine():
                inputLines.append(self.visit(line))
        return ASTInput.ASTInput.makeASTInput(_inputDefinitions=inputLines)

    # Visit a parse tree produced by PyNESTMLParser#inputLine.
    def visitInputLine(self, ctx):
        name = str(ctx.name.text) if ctx.name is not None else None
        sizeParameter = str(ctx.sizeParameter) if ctx.sizeParameter is not None else None
        inputTypes = list()
        if ctx.inputType() is not None:
            for Type in ctx.inputType():
                inputTypes.append(self.visit(Type))
        isCurrent = True if ctx.isCurrent is not None else False
        isSpike = True if ctx.isSpike is not None else False
        return ASTInputLine.ASTInputLine.makeASTInputLine(_name=name, _sizeParameter=sizeParameter,
                                                          _inputTypes=inputTypes, _isCurrent=isCurrent,
                                                          _isSpike=isSpike)

    # Visit a parse tree produced by PyNESTMLParser#inputType.
    def visitInputType(self, ctx):
        isInhibitory = True if ctx.isInhibitory is not None else False
        isExcitatory = True if ctx.isExcitatory is not None else False
        return ASTInputType.ASTInputType.makeASTInputType(_isInhibitory=isInhibitory, _isExcitatory=isExcitatory)

    # Visit a parse tree produced by PyNESTMLParser#outputBuffer.
    def visitOutputBuffer(self, ctx):
        if ctx.isSpike is not None:
            return ASTOutput.ASTOutput.makeASTOutput(_type='spike')
        elif ctx.isCurrent is not None:
            return ASTOutput.ASTOutput.makeASTOutput(_type='current')
        else:
            raise PyNESTMLUnknownOutputBufferType('(NESTML.ASTBuilder) Type of output buffer not recognized.')

    # Visit a parse tree produced by PyNESTMLParser#function.
    def visitFunction(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        parameters = self.visit(ctx.parameters()) if ctx.parameters() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        returnType = self.visit(ctx.returnType) if ctx.returnType is not None else None
        return ASTFunction.ASTFunction.makeASTFunction(_name=name, _parameters=parameters, _block=block,
                                                       _returnType=returnType)

    # Visit a parse tree produced by PyNESTMLParser#parameters.
    def visitParameters(self, ctx):
        parameters = list()
        if ctx.parameter() is not None:
            if type(ctx.parameter()) is list:
                for par in ctx.parameter():
                    parameters.append(self.visit(par))
            else:
                parameters.append(self.visit(ctx.parameter()))
        return ASTParameters.ASTParameters.makeASTParameters(_parameterList=parameters)

    # Visit a parse tree produced by PyNESTMLParser#parameter.
    def visitParameter(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        dataType = self.visit(ctx.datatype()) if ctx.datatype() is not None else None
        return ASTParameter.ASTParameter.makeASTParameter(_name=name, _dataType=dataType)

    def getNext(self, _elements=list()):
        """
        This method is used to get the next element according to its source position.
        :type _elements: a list of elements
        :return: the next element
        :rtype: object
        """
        currentFirst = None
        for elem in _elements:
            if currentFirst is None or currentFirst.start.line > elem.start.line:
                currentFirst = elem
        return currentFirst


class PyNESTMLUnknownBodyTypeException(Exception):
    pass


class PyNESTMLUnknownExpressionTypeException(Exception):
    pass


class PyNESTMLUnknownOutputBufferType(Exception):
    pass
