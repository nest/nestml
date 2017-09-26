#
# ASTBuilderVisitor.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


import re
from antlr4 import *
# import all ASTClasses
from pynestml.src.main.python.org.nestml.ast import *
from pynestml.src.main.python.org.nestml.ast.ASTOutputBlock import SignalType
from pynestml.src.main.python.org.nestml.cocos.CoCosManager import CoCosManager


class ASTBuilderVisitor(ParseTreeVisitor):
    """
    This class is used to create an internal representation of the model by means of an abstract syntax tree.
    """

    # Visit a parse tree produced by PyNESTMLParser#nestmlCompilationUnit.
    def visitNestmlCompilationUnit(self, ctx):
        neurons = list()
        sourcePosition = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                                   _startColumn=ctx.start.column,
                                                                                   _endLine=ctx.stop.line,
                                                                                   _endColumn=ctx.stop.column)
        for child in ctx.neuron():
            neurons.append(self.visit(child))
        compilationUnit = ASTNESTMLCompilationUnit.ASTNESTMLCompilationUnit. \
            makeASTNESTMLCompilationUnit(_listOfNeurons=neurons, _sourcePosition=sourcePosition)
        # first ensure certain properties of the neuron
        CoCosManager.checkNeuronNamesUnique(compilationUnit)
        return compilationUnit

    # Visit a parse tree produced by PyNESTMLParser#datatype.
    def visitDatatype(self, ctx):
        isInt = (True if ctx.isInt is not None else False)
        isReal = (True if ctx.isReal is not None else False)
        isString = (True if ctx.isString is not None else False)
        isBool = (True if ctx.isBool is not None else False)
        isVoid = (True if ctx.isVoid is not None else False)
        unit = self.visit(ctx.unitType()) if ctx.unitType() is not None else None
        sourcePosition = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                                   _startColumn=ctx.start.column,
                                                                                   _endLine=ctx.stop.line,
                                                                                   _endColumn=ctx.stop.column)
        ret = ASTDatatype.ASTDatatype.makeASTDatatype(_isInteger=isInt, _isBoolean=isBool,
                                                      _isReal=isReal, _isString=isString, _isVoid=isVoid,
                                                      _isUnitType=unit, _sourcePosition=sourcePosition)
        from pynestml.src.main.python.org.nestml.visitor.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        ASTUnitTypeVisitor.visitDatatype(ret)
        return ret

    # Visit a parse tree produced by PyNESTMLParser#unitType.
    def visitUnitType(self, ctx):
        leftParenthesis = True if ctx.leftParentheses is not None else False
        compoundUnit = self.visit(ctx.compoundUnit) if ctx.compoundUnit is not None else None
        rightParenthesis = True if ctx.rightParentheses is not None else False
        base = self.visit(ctx.base) if ctx.base is not None else None
        isPow = True if ctx.powOp is not None else False
        exponent = int(str(ctx.exponent.text)) if ctx.exponent is not None else None
        if ctx.unitlessLiteral is not None:
            lhs = int(str(ctx.unitlessLiteral.text))
        else:
            lhs = self.visit(ctx.left) if ctx.left is not None else None
        isTimes = True if ctx.timesOp is not None else False
        isDiv = True if ctx.divOp is not None else False
        rhs = self.visit(ctx.right) if ctx.right is not None else None
        unit = str(ctx.unit.text) if ctx.unit is not None else None
        sourcePosition = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                                   _startColumn=ctx.start.column,
                                                                                   _endLine=ctx.stop.line,
                                                                                   _endColumn=ctx.stop.column)
        return ASTUnitType.ASTUnitType.makeASTUnitType(_leftParentheses=leftParenthesis, _compoundUnit=compoundUnit,
                                                       _rightParentheses=rightParenthesis, _base=base, _isPow=isPow,
                                                       _exponent=exponent, _lhs=lhs, _rhs=rhs, _isDiv=isDiv,
                                                       _isTimes=isTimes, _unit=unit, _sourcePosition=sourcePosition)

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
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        if expression is not None:
            return ASTExpression.ASTExpression.makeExpression(_hasLeftParentheses=hasLeftParentheses,
                                                              _hasRightParentheses=hasRightParentheses,
                                                              _isLogicalNot=isLogicalNot,
                                                              _unaryOperator=unaryOperator,
                                                              _expression=expression, _sourcePosition=sourcePos)
        elif (lhs is not None) and (rhs is not None) and (binaryOperator is not None):
            return ASTExpression.ASTExpression.makeCompoundExpression(_lhs=lhs, _binaryOperator=binaryOperator,
                                                                      _rhs=rhs, _sourcePosition=sourcePos)
        elif (condition is not None) and (ifTrue is not None) and (ifNot is not None):
            return ASTExpression.ASTExpression.makeTernaryExpression(_condition=condition, _ifTrue=ifTrue,
                                                                     _ifNot=ifNot, _sourcePosition=sourcePos)
        else:
            raise PyNESTMLUnknownExpressionTypeException('(NESTML.ASTBuilder) Type of expression not recognized.')

    # Visit a parse tree produced by PyNESTMLParser#simpleExpression.
    def visitSimpleExpression(self, ctx):
        functionCall = (self.visit(ctx.functionCall()) if ctx.functionCall() is not None else None)
        booleanLiteral = ((True if re.match(r'[Tt]rue', str(ctx.BOOLEAN_LITERAL())) else False)
                          if ctx.BOOLEAN_LITERAL() is not None else None)
        if ctx.INTEGER() is not None:
            numericLiteral = int(str(ctx.INTEGER()))
        elif ctx.FLOAT() is not None:
            numericLiteral = float(str(ctx.FLOAT()))
        else:
            numericLiteral = None
        isInf = (True if ctx.isInf is not None else False)
        variable = (self.visit(ctx.variable()) if ctx.variable() is not None else None)
        string = (str(ctx.string.text) if ctx.string is not None else None)
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTSimpleExpression.ASTSimpleExpression.makeASTSimpleExpression(_functionCall=functionCall,
                                                                               _booleanLiteral=booleanLiteral,
                                                                               _numericLiteral=numericLiteral,
                                                                               _isInf=isInf, _variable=variable,
                                                                               _string=string,
                                                                               _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#unaryOperator.
    def visitUnaryOperator(self, ctx):
        isUnaryPlus = (True if ctx.unaryPlus is not None else False)
        isUnaryMinus = (True if ctx.unaryMinus is not None else False)
        isUnaryTilde = (True if ctx.unaryTilde is not None else False)
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTUnaryOperator.ASTUnaryOperator.makeASTUnaryOperator(_isUnaryPlus=isUnaryPlus,
                                                                      _isUnaryMinus=isUnaryMinus,
                                                                      _isUnaryTilde=isUnaryTilde,
                                                                      _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#bitOperator.
    def visitBitOperator(self, ctx):
        isBitAnd = (True if ctx.bitAnd is not None else False)
        isBitXor = (True if ctx.bitXor is not None else False)
        isBitOr = (True if ctx.bitOr is not None else False)
        isBitShiftLeft = (True if ctx.bitShiftLeft is not None else False)
        isBitShiftRight = (True if ctx.bitShiftRight is not None else False)
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTBitOperator.ASTBitOperator.makeASTBitOperator(_isBitAnd=isBitAnd, _isBitXor=isBitXor,
                                                                _isBitOr=isBitOr,
                                                                _isBitShiftLeft=isBitShiftLeft,
                                                                _isBitShiftRight=isBitShiftRight,
                                                                _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#comparisonOperator.
    def visitComparisonOperator(self, ctx):
        isLt = (True if ctx.lt is not None else False)
        isLe = (True if ctx.le is not None else False)
        isEq = (True if ctx.eq is not None else False)
        isNe = (True if ctx.ne is not None else False)
        isNe2 = (True if ctx.ne2 is not None else False)
        isGe = (True if ctx.ge is not None else False)
        isGt = (True if ctx.gt is not None else False)
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTComparisonOperator.ASTComparisonOperator.makeASTComparisonOperator(_isLt=isLt, _isLe=isLe,
                                                                                     _isEq=isEq, _isNe=isNe,
                                                                                     _isNe2=isNe2,
                                                                                     _isGe=isGe, _isGt=isGt,
                                                                                     _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#logicalOperator.
    def visitLogicalOperator(self, ctx):
        isLogicalAnd = (True if ctx.logicalAnd is not None else False)
        isLogicalOr = (True if ctx.logicalOr is not None else False)
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTLogicalOperator.ASTLogicalOperator.makeASTLogicalOperator(_isLogicalAnd=isLogicalAnd,
                                                                            _isLogicalOr=isLogicalOr,
                                                                            _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#variable.
    def visitVariable(self, ctx):
        differentialOrder = (len(ctx.differentialOrder()) if ctx.differentialOrder() is not None else 0)
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTVariable.ASTVariable.makeASTVariable(_name=str(ctx.NAME()),
                                                       _differentialOrder=differentialOrder, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#functionCall.
    def visitFunctionCall(self, ctx):
        name = (str(ctx.calleeName.text))
        args = list()
        if type(ctx.expression()) == list:
            for arg in ctx.expression():
                args.append(self.visit(arg))
        elif ctx.expression() is not None:
            args.append(self.visit(ctx.expression()))
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTFunctionCall.ASTFunctionCall.makeASTFunctionCall(_calleeName=name, _args=args,
                                                                   _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#odeFunction.
    def visitOdeFunction(self, ctx):
        isRecordable = (True if ctx.recordable is not None else False)
        variableName = (str(ctx.variableName.text) if ctx.variableName is not None else None)
        dataType = (self.visit(ctx.datatype()) if ctx.datatype() is not None else None)
        expression = (self.visit(ctx.expression()) if ctx.expression() is not None else None)
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTOdeFunction.ASTOdeFunction.makeASTOdeFunction(_isRecordable=isRecordable, _variableName=variableName,
                                                                _dataType=dataType,
                                                                _expression=expression, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#equation.
    def visitOdeEquation(self, ctx):
        lhs = self.visit(ctx.lhs) if ctx.lhs is not None else None
        rhs = self.visit(ctx.rhs) if ctx.rhs is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTOdeEquation.ASTOdeEquation.makeASTOdeEquation(_lhs=lhs, _rhs=rhs, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#shape.
    def visitOdeShape(self, ctx):
        lhs = self.visit(ctx.lhs) if ctx.lhs is not None else None
        rhs = self.visit(ctx.rhs) if ctx.rhs is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTOdeShape.ASTOdeShape.makeASTOdeShape(_lhs=lhs, _rhs=rhs, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#block.
    def visitBlock(self, ctx):
        stmts = list()
        if ctx.stmt() is not None:
            for stmt in ctx.stmt():
                stmts.append(self.visit(stmt))
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTBlock.ASTBlock.makeASTBlock(_stmts=stmts, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#compound_Stmt.
    def visitCompoundStmt(self, ctx):
        ifStmt = self.visit(ctx.ifStmt()) if ctx.ifStmt() is not None else None
        whileStmt = self.visit(ctx.whileStmt()) if ctx.whileStmt() is not None else None
        forStmt = self.visit(ctx.forStmt()) if ctx.forStmt() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTCompoundStmt.ASTCompoundStmt.makeASTCompoundStmt(_ifStmt=ifStmt, _whileStmt=whileStmt,
                                                                   _forStmt=forStmt, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#small_Stmt.
    def visitSmallStmt(self, ctx):
        assignment = self.visit(ctx.assignment()) if ctx.assignment() is not None else None
        functionCall = self.visit(ctx.functionCall()) if ctx.functionCall() is not None else None
        declaration = self.visit(ctx.declaration()) if ctx.declaration() is not None else None
        returnStmt = self.visit(ctx.returnStmt()) if ctx.returnStmt() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTSmallStmt.ASTSmallStmt.makeASTSmallStmt(_assignment=assignment, _functionCall=functionCall,
                                                          _declaration=declaration, _returnStmt=returnStmt,
                                                          _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#assignment.
    def visitAssignment(self, ctx):
        lhs = self.visit(ctx.lhsVariable) if ctx.lhsVariable is not None else None
        isDirectAssignment = True if ctx.directAssignment is not None else False
        isCompoundSum = True if ctx.compoundSum is not None else False
        isCompoundMinus = True if ctx.compoundMinus is not None else False
        isCompoundProduct = True if ctx.compoundProduct is not None else False
        isCompoundQuotient = True if ctx.compoundQuotient is not None else False
        expression = self.visit(ctx.expression()) if ctx.expression() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTAssignment.ASTAssignment.makeASTAssignment(_lhs=lhs, _isDirectAssignment=isDirectAssignment,
                                                             _isCompoundSum=isCompoundSum,
                                                             _isCompoundMinus=isCompoundMinus,
                                                             _isCompoundProduct=isCompoundProduct,
                                                             _isCompoundQuotient=isCompoundQuotient,
                                                             _expression=expression, _sourcePosition=sourcePos)

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
        invariant = self.visit(ctx.invariant) if ctx.invariant is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTDeclaration.ASTDeclaration.makeASTDeclaration(_isRecordable=isRecordable, _isFunction=isFunction,
                                                                _variables=variables, _dataType=dataType,
                                                                _sizeParameter=sizeParam,
                                                                _expression=expression,
                                                                _invariant=invariant, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#returnStmt.
    def visitReturnStmt(self, ctx):
        retExpression = self.visit(ctx.expression()) if ctx.expression() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTReturnStmt.ASTReturnStmt.makeASTReturnStmt(_expression=retExpression, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#ifStmt.
    def visitIfStmt(self, ctx):
        ifClause = self.visit(ctx.ifClause()) if ctx.ifClause() is not None else None
        elifClauses = list()
        if ctx.elifClause() is not None:
            for clause in ctx.elifClause():
                elifClauses.append(self.visit(clause))
        elseClause = self.visit(ctx.elseClause()) if ctx.elseClause() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTIfStmt.ASTIfStmt.makeASTIfStmt(_ifClause=ifClause, _elifClauses=elifClauses,
                                                 _elseClause=elseClause, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#ifClause.
    def visitIfClause(self, ctx):
        condition = self.visit(ctx.expression()) if ctx.expression() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTIfClause.ASTIfClause.makeASTIfClause(_condition=condition, _block=block, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#elifClause.
    def visitElifClause(self, ctx):
        condition = self.visit(ctx.expression()) if ctx.expression() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTElifClause.ASTElifClause.makeASTElifClause(_condition=condition, _block=block,
                                                             _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#elseClause.
    def visitElseClause(self, ctx):
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTElseClause.ASTElseClause.makeASTElseClause(_block=block, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#forStmt.
    def visitForStmt(self, ctx):
        variable = str(ctx.NAME()) if ctx.NAME() is not None else None
        From = self.visit(ctx.vrom) if ctx.vrom is not None else None
        to = self.visit(ctx.to) if ctx.to is not None else None
        step = self.visit(ctx.step) if ctx.step is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTForStmt.ASTForStmt.makeASTForStmt(_variable=variable, _from=From, _to=to, _step=step,
                                                    _block=block, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#whileStmt.
    def visitWhileStmt(self, ctx):
        cond = self.visit(ctx.expression()) if ctx.expression() is not None else None
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTWhileStmt.ASTWhileStmt.makeASTWhileStmt(_condition=cond, _block=block, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#signedNumericLiteral.
    def visitSignedNumericLiteral(self, ctx):
        isNeg = True if ctx.negative is not None else False
        if ctx.INTEGER() is not None:
            value = int(str(ctx.INTEGER()))
        else:
            value = float(str(ctx.FLOAT()))
        if isNeg:
            return -value
        else:
            return value

    # Visit a parse tree produced by PyNESTMLParser#neuron.
    def visitNeuron(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        body = self.visit(ctx.body()) if ctx.body() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        # after we have constructed the ast of the neuron, we can ensure some basic properties which should always hold
        # we have to check if each type of block is defined at most once (except for function), and that input,output
        # and update are defined once
        from pynestml.src.main.python.org.nestml.cocos.CoCoEachBlockUniqueAndDefined import \
            CoCoEachBlockUniqueAndDefined
        neuron = ASTNeuron.ASTNeuron.makeASTNeuron(_name=name, _body=body, _sourcePosition=sourcePos)
        CoCoEachBlockUniqueAndDefined.checkCoCo(_neuron=neuron)
        # now the ast seems to be correct, return it
        return neuron

    # Visit a parse tree produced by PyNESTMLParser#body.
    def visitBody(self, ctx):
        "Here, in order to ensure that the correct order of elements is kept, we use a method which inspects \
        a list of elements and returns the one with the smallest source line."
        body_elements = list()
        # visit all var_block children
        if ctx.blockWithVariables() is not None:
            for child in ctx.blockWithVariables():
                body_elements.append(child)
        if ctx.updateBlock() is not None:
            for child in ctx.updateBlock():
                body_elements.append(child)
        if ctx.equationsBlock() is not None:
            for child in ctx.equationsBlock():
                body_elements.append(child)
        if ctx.inputBlock() is not None:
            for child in ctx.inputBlock():
                body_elements.append(child)
        if ctx.outputBlock() is not None:
            for child in ctx.outputBlock():
                body_elements.append(child)
        if ctx.function() is not None:
            for child in ctx.function():
                body_elements.append(child)
        elements = list()
        while len(body_elements) > 0:
            elem = self.getNext(body_elements)
            elements.append(self.visit(elem))
            body_elements.remove(elem)
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTBody.ASTBody.makeASTBody(_bodyElements=elements, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#blockWithVariables.
    def visitBlockWithVariables(self, ctx):
        declarations = list()
        if ctx.declaration() is not None:
            for child in ctx.declaration():
                declarations.append(self.visit(child))
        blockType = ctx.blockType.text  # the text field stores the exact name of the token, e.g., state
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        if blockType == 'state':
            return ASTBlockWithVariables.ASTBlockWithVariables.makeASTBlockWithVariables(
                _isInternals=False, _isParameters=False, _isState=True, _isInitialValues=False,
                _declarations=declarations, _sourcePosition=sourcePos)
        elif blockType == 'parameters':
            return ASTBlockWithVariables.ASTBlockWithVariables.makeASTBlockWithVariables(
                _isInternals=False, _isParameters=True, _isState=False, _isInitialValues=False,
                _declarations=declarations, _sourcePosition=sourcePos)
        elif blockType == 'internals':
            return ASTBlockWithVariables.ASTBlockWithVariables.makeASTBlockWithVariables(
                _isInternals=True, _isParameters=False, _isState=False, _isInitialValues=False,
                _declarations=declarations, _sourcePosition=sourcePos)
        elif blockType == 'initial_values':
            return ASTBlockWithVariables.ASTBlockWithVariables.makeASTBlockWithVariables(
                _isInternals=False, _isParameters=False, _isState=False, _isInitialValues=True,
                _declarations=declarations, _sourcePosition=sourcePos)

        else:
            raise PyNESTMLUnknownBodyTypeException(
                '(NESTML.ASTBuilder) Unspecified type (=%s) of var-block.' % str(ctx.blockType))
            # Visit a parse tree produced by PyNESTMLParser#dynamics.

    def visitUpdateBlock(self, ctx):
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTUpdateBlock.ASTUpdateBlock.makeASTUpdateBlock(_block=block, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#equations.
    def visitEquationsBlock(self, ctx):
        elems = list()
        if ctx.odeEquation() is not None:
            for eq in ctx.odeEquation():
                elems.append(eq)
        if ctx.odeShape() is not None:
            for shape in ctx.odeShape():
                elems.append(shape)
        if ctx.odeFunction() is not None:
            for fun in ctx.odeFunction():
                elems.append(fun)
        ordered = list()
        while len(elems) > 0:
            elem = self.getNext(elems)
            ordered.append(self.visit(elem))
            elems.remove(elem)
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTEquationsBlock.ASTEquationsBlock.makeASTEquationsBlock(_declarations=ordered,
                                                                         _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#inputBuffer.
    def visitInputBlock(self, ctx):
        inputLines = list()
        if ctx.inputLine() is not None:
            for line in ctx.inputLine():
                inputLines.append(self.visit(line))
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTInputBlock.ASTInputBlock.makeASTInputBlock(_inputDefinitions=inputLines, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#inputLine.
    def visitInputLine(self, ctx):
        name = str(ctx.name.text) if ctx.name is not None else None
        sizeParameter = str(ctx.sizeParameter.text) if ctx.sizeParameter is not None else None
        inputTypes = list()
        if ctx.inputType() is not None:
            for Type in ctx.inputType():
                inputTypes.append(self.visit(Type))
        dataType = self.visit(ctx.datatype()) if ctx.datatype() is not None else None
        if ctx.isCurrent:
            signalType = SignalType.CURRENT
        elif ctx.isSpike:
            signalType = SignalType.SPIKE
        else:
            signalType = None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTInputLine.ASTInputLine.makeASTInputLine(_name=name, _sizeParameter=sizeParameter, _dataType=dataType,
                                                          _inputTypes=inputTypes, _signalType=signalType,
                                                          _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#inputType.
    def visitInputType(self, ctx):
        isInhibitory = True if ctx.isInhibitory is not None else False
        isExcitatory = True if ctx.isExcitatory is not None else False
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTInputType.ASTInputType.makeASTInputType(_isInhibitory=isInhibitory, _isExcitatory=isExcitatory,
                                                          _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#outputBuffer.
    def visitOutputBlock(self, ctx):
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        if ctx.isSpike is not None:
            return ASTOutputBlock.ASTOutputBlock.makeASTOutputBlock(_type=ASTOutputBlock.SignalType.SPIKE,
                                                                    _sourcePosition=sourcePos)
        elif ctx.isCurrent is not None:
            return ASTOutputBlock.ASTOutputBlock.makeASTOutputBlock(_type=ASTOutputBlock.SignalType.CURRENT,
                                                                    _sourcePosition=sourcePos)
        else:
            raise PyNESTMLUnknownOutputBufferType('(NESTML.ASTBuilder) Type of output buffer not recognized.')

    # Visit a parse tree produced by PyNESTMLParser#function.
    def visitFunction(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        parameters = list()
        if type(ctx.parameter()) is list:
            for par in ctx.parameter():
                parameters.append(self.visit(par))
        elif ctx.parameters() is not None:
            parameters.append(ctx.parameter())
        block = self.visit(ctx.block()) if ctx.block() is not None else None
        returnType = self.visit(ctx.returnType) if ctx.returnType is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTFunction.ASTFunction.makeASTFunction(_name=name, _parameters=parameters, _block=block,
                                                       _returnType=returnType, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#parameter.
    def visitParameter(self, ctx):
        name = str(ctx.NAME()) if ctx.NAME() is not None else None
        dataType = self.visit(ctx.datatype()) if ctx.datatype() is not None else None
        sourcePos = ASTSourcePosition.ASTSourcePosition.makeASTSourcePosition(_startLine=ctx.start.line,
                                                                              _startColumn=ctx.start.column,
                                                                              _endLine=ctx.stop.line,
                                                                              _endColumn=ctx.stop.column)
        return ASTParameter.ASTParameter.makeASTParameter(_name=name, _dataType=dataType, _sourcePosition=sourcePos)

    # Visit a parse tree produced by PyNESTMLParser#stmt.
    def visitStmt(self, ctx):
        small = self.visit(ctx.smallStmt()) if ctx.smallStmt() is not None else None
        compound = self.visit(ctx.compoundStmt()) if ctx.compoundStmt() is not None else None
        if small is not None:
            return small
        else:
            return compound

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
