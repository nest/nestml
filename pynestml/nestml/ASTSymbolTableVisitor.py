#
# ASTSymbolTableVisitor.py
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
from pynestml.nestml.Scope import Scope, ScopeType
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Either import Either
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.nestml.FunctionSymbol import FunctionSymbol
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.VariableSymbol import VariableSymbol, BlockType
from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
from pynestml.nestml.PredefinedVariables import PredefinedVariables
from pynestml.nestml.CoCosManager import CoCosManager


class SymbolTableASTVisitor(NESTMLVisitor):
    """
    This class is used to create a symbol table from a handed over AST.
    
    Attributes:
        __currentBlockType This variable is used to store information regarding which block with declarations is 
                            currently visited. It is used to update the BlockType of variable symbols to the correct
                            element.
        __globalScope      Stores the current global scope as required to resolve symbols.                    
    """
    __currentBlockType = None
    __globalScope = None

    @classmethod
    def updateSymbolTable(cls, _astNeuron=None):
        """
        Creates for the handed over ast the corresponding symbol table.
        :param _astNeuron: a AST neuron object as used to create the symbol table
        :type _astNeuron: ASTNeuron
        :return: a new symbol table
        :rtype: SymbolTable
        """
        Logger.setCurrentNeuron(_astNeuron)
        Logger.logMessage('Start building symbol table...', LOGGING_LEVEL.INFO)
        SymbolTableASTVisitor.visitNeuron(_astNeuron)
        Logger.setCurrentNeuron(None)
        return

    @classmethod
    def visitNeuron(cls, _neuron=None):
        """
        Private method: Used to visit a single neuron and create the corresponding global as well as local scopes.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        from pynestml.nestml.ASTNeuron import ASTNeuron
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of neuron provided (%s)!' % type(_neuron)
        scope = Scope(_scopeType=ScopeType.GLOBAL, _sourcePosition=_neuron.getSourcePosition())
        # store current global scope, it is required for resolving of symbols
        cls.__globalScope = scope
        _neuron.updateScope(scope)
        _neuron.getBody().updateScope(scope)
        # now first, we add all predefined elements to the scope
        variables = PredefinedVariables.getVariables()
        functions = PredefinedFunctions.getFunctionSymbols()
        for symbol in variables.keys():
            _neuron.getScope().addSymbol(variables[symbol])
        for symbol in functions.keys():
            _neuron.getScope().addSymbol(functions[symbol])
        # now create the actual scope
        cls.visitBody(_neuron.getBody())
        # before following checks occur, we need to ensure several simple properties
        CoCosManager.postSymbolTableBuilderChecks(_neuron)
        # the following part is done in order to mark conductance based buffers as such.
        if _neuron.getInputBlocks() is not None and _neuron.getEquationsBlocks() is not None:
            # this case should be prevented, since several input blocks result in  a incorrect model
            if isinstance(_neuron.getInputBlocks(), list):
                buffers = (buffer for bufferA in _neuron.getInputBlocks() for buffer in bufferA.getInputLines())
            else:
                buffers = (buffer for buffer in _neuron.getInputBlocks().getInputLines())
            from pynestml.nestml.ASTOdeShape import ASTOdeShape
            odeDeclarations = (decl for decl in _neuron.getEquationsBlocks().getDeclarations() if
                               not isinstance(decl, ASTOdeShape))
            cls.markConductanceBasedBuffers(_inputLines=buffers, _odeDeclarations=odeDeclarations)
        # now update the equations
        if _neuron.getEquationsBlocks() is not None:
            equationBlock = _neuron.getEquationsBlocks()
            cls.assignOdeToVariables(equationBlock)
        CoCosManager.postOdeSpecificationChecks(_neuron)
        return

    @classmethod
    def visitBody(cls, _body=None):
        """
        Private method: Used to visit a single neuron body and create the corresponding scope.
        :param _body: a single body element.
        :type _body: ASTBody
        """
        from pynestml.nestml.ASTBlockWithVariables import ASTBlockWithVariables
        from pynestml.nestml.ASTUpdateBlock import ASTUpdateBlock
        from pynestml.nestml.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.nestml.ASTInputBlock import ASTInputBlock
        from pynestml.nestml.ASTOutputBlock import ASTOutputBlock
        from pynestml.nestml.ASTFunction import ASTFunction
        for bodyElement in _body.getBodyElements():
            bodyElement.updateScope(_body.getScope())
            if isinstance(bodyElement, ASTBlockWithVariables):
                cls.visitBlockWithVariables(bodyElement)
            elif isinstance(bodyElement, ASTUpdateBlock):
                cls.visitUpdateBlock(bodyElement)
            elif isinstance(bodyElement, ASTEquationsBlock):
                cls.visitEquationsBlock(bodyElement)
            elif isinstance(bodyElement, ASTInputBlock):
                cls.visitInputBlock(bodyElement)
            elif isinstance(bodyElement, ASTOutputBlock):
                cls.visitOutputBlock(bodyElement)
            elif isinstance(bodyElement, ASTFunction):
                cls.visitFunctionBlock(bodyElement)
        return

    @classmethod
    def visitFunctionBlock(cls, _block=None):
        """
        Private method: Used to visit a single function block and create the corresponding scope.
        :param _block: a function block object.
        :type _block: ASTFunction
        """
        from pynestml.nestml.ASTFunction import ASTFunction
        from pynestml.nestml.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        assert (_block is not None and isinstance(_block, ASTFunction)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of function block provided (%s)!' % type(_block)
        cls.__currentBlockType = BlockType.LOCAL  # before entering, update the current block type
        symbol = FunctionSymbol(_scope=_block.getScope(), _elementReference=_block, _paramTypes=list(),
                                _name=_block.getName(), _isPredefined=False)
        _block.getScope().addSymbol(symbol)
        scope = Scope(_scopeType=ScopeType.FUNCTION, _enclosingScope=_block.getScope(),
                      _sourcePosition=_block.getSourcePosition())
        _block.getScope().addScope(scope)
        for arg in _block.getParameters():
            # first visit the data type to ensure that variable symbol can receive a combined data type
            arg.getDataType().updateScope(scope)
            cls.visitDataType(arg.getDataType())
            # given the fact that the name is not directly equivalent to the one as stated in the model,
            # we have to get it by the sub-visitor
            typeName = ASTUnitTypeVisitor.visitDatatype(arg.getDataType())
            # first collect the types for the parameters of the function symbol
            symbol.addParameterType(PredefinedTypes.getTypeIfExists(typeName))
            # update the scope of the arg
            arg.updateScope(scope)
            # create the corresponding variable symbol representing the parameter
            varSymbol = VariableSymbol(_elementReference=arg, _scope=scope, _name=arg.getName(),
                                       _blockType=BlockType.LOCAL, _isPredefined=False, _isFunction=False,
                                       _isRecordable=False,
                                       _typeSymbol=PredefinedTypes.getTypeIfExists(typeName))
            scope.addSymbol(varSymbol)
        if _block.hasReturnType():
            _block.getReturnType().updateScope(scope)
            cls.visitDataType(_block.getReturnType())
            symbol.setReturnType(
                PredefinedTypes.getTypeIfExists(ASTUnitTypeVisitor.visitDatatype(_block.getReturnType())))
        else:
            symbol.setReturnType(PredefinedTypes.getVoidType())
        _block.getBlock().updateScope(scope)
        cls.visitBlock(_block.getBlock())
        cls.__currentBlockType = None  # before leaving update the type
        return

    @classmethod
    def visitUpdateBlock(cls, _block=None):
        """
        Private method: Used to visit a single update block and create the corresponding scope.
        :param _block: an update block object.
        :type _block: ASTDynamics
        """
        from pynestml.nestml.ASTUpdateBlock import ASTUpdateBlock
        assert (_block is not None and isinstance(_block, ASTUpdateBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of update-block provided (%s)!' % type(_block)
        cls.__currentBlockType = BlockType.LOCAL
        scope = Scope(_scopeType=ScopeType.UPDATE, _enclosingScope=_block.getScope(),
                      _sourcePosition=_block.getSourcePosition())
        _block.getScope().addScope(scope)
        _block.getBlock().updateScope(scope)
        cls.visitBlock(_block.getBlock())
        cls.__currentBlockType = BlockType.LOCAL
        return

    @classmethod
    def visitBlock(cls, _block=None):
        """
        Private method: Used to visit a single block of statements, create and update the corresponding scope.
        :param _block: a block object.
        :type _block: ASTBlock
        """
        from pynestml.nestml.ASTBlock import ASTBlock
        from pynestml.nestml.ASTSmallStmt import ASTSmallStmt
        from pynestml.nestml.ASTCompoundStmt import ASTCompoundStmt
        assert (_block is not None and isinstance(_block, ASTBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of block provided %s!' % type(_block)
        for stmt in _block.getStmts():
            if isinstance(stmt, ASTSmallStmt):
                stmt.updateScope(_block.getScope())
                cls.visitSmallStmt(stmt)
            elif isinstance(stmt, ASTCompoundStmt):
                stmt.updateScope(_block.getScope())
                cls.visitCompoundStmt(stmt)
        return

    @classmethod
    def visitSmallStmt(cls, _stmt=None):
        """
        Private method: Used to visit a single small statement and create the corresponding sub-scope.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStatement
        """
        from pynestml.nestml.ASTSmallStmt import ASTSmallStmt
        assert (_stmt is not None and isinstance(_stmt, ASTSmallStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of small statement provided (%s)!' % type(_stmt)
        if _stmt.isDeclaration():
            _stmt.getDeclaration().updateScope(_stmt.getScope())
            cls.visitDeclaration(_stmt.getDeclaration())
        elif _stmt.isAssignment():
            _stmt.getAssignment().updateScope(_stmt.getScope())
            cls.visitAssignment(_stmt.getAssignment())
        elif _stmt.isFunctionCall():
            _stmt.getFunctionCall().updateScope(_stmt.getScope())
            cls.visitFunctionCall(_stmt.getFunctionCall())
        elif _stmt.isReturnStmt():
            _stmt.getReturnStmt().updateScope(_stmt.getScope())
            cls.visitReturnStmt(_stmt.getReturnStmt())
        return

    @classmethod
    def visitCompoundStmt(cls, _stmt=None):
        """
        Private method: Used to visit a single compound statement and create the corresponding sub-scope.
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStatement
        """
        from pynestml.nestml.ASTCompoundStmt import ASTCompoundStmt
        assert (_stmt is not None and isinstance(_stmt, ASTCompoundStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of compound statement provided (%s)!' % type(_stmt)
        if _stmt.isIfStmt():
            _stmt.getIfStmt().updateScope(_stmt.getScope())
            cls.visitIfStmt(_stmt.getIfStmt())
        elif _stmt.isWhileStmt():
            _stmt.getWhileStmt().updateScope(_stmt.getScope())
            cls.visitWhileStmt(_stmt.getWhileStmt())
        else:
            _stmt.getForStmt().updateScope(_stmt.getScope())
            cls.visitForStmt(_stmt.getForStmt())
        return

    @classmethod
    def visitAssignment(cls, _assignment=None):
        """
        Private method: Used to visit a single assignment and update the its corresponding scope.
        :param _assignment: an assignment object.
        :type _assignment: ASTAssignment
        :return: no return value, since neither scope nor symbol is created
        :rtype: void
        """
        from pynestml.nestml.ASTAssignment import ASTAssignment
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of assignment provided (%s)!' % type(_assignment)
        _assignment.getVariable().updateScope(_assignment.getScope())
        cls.visitVariable(_assignment.getVariable())
        _assignment.getExpression().updateScope(_assignment.getScope())
        cls.visitExpression(_assignment.getExpression())
        return

    @classmethod
    def visitFunctionCall(cls, _functionCall=None):
        """
        Private method: Used to visit a single function call and update its corresponding scope.
        :param _functionCall: a function call object.
        :type _functionCall: ASTFunctionCall
        :return: no return value, since neither scope nor symbol is created
        :rtype: void
        """
        from pynestml.nestml.ASTFunctionCall import ASTFunctionCall
        assert (_functionCall is not None and isinstance(_functionCall, ASTFunctionCall)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of function call provided (%s)!' % type(_functionCall)
        for arg in _functionCall.getArgs():
            arg.updateScope(_functionCall.getScope())
            cls.visitExpression(arg)
        return

    @classmethod
    def visitDeclaration(cls, _declaration=None):
        """
        Private method: Used to visit a single declaration, update its scope and return the corresponding set of
        symbols
        :param _declaration: a declaration object.
        :type _declaration: ASTDeclaration
        :return: the scope is update without a return value.
        :rtype: void
        """
        from pynestml.nestml.ASTDeclaration import ASTDeclaration
        from pynestml.nestml.VariableSymbol import VariableSymbol, BlockType
        from pynestml.nestml.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        assert (_declaration is not None and isinstance(_declaration, ASTDeclaration)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong typ of declaration provided (%s)!' % type(_declaration)

        expression = _declaration.getExpr() if _declaration.hasExpression() else None
        typeName = ASTUnitTypeVisitor.visitDatatype(_declaration.getDataType())
        # all declarations in the state block are recordable
        isRecordable = _declaration.isRecordable() or \
                       cls.__currentBlockType == BlockType.STATE or cls.__currentBlockType == BlockType.INITIAL_VALUES
        initValue = _declaration.getExpr() if cls.__currentBlockType == BlockType.INITIAL_VALUES else None
        vectorParameter = _declaration.getSizeParameter()
        for var in _declaration.getVariables():  # for all variables declared create a new symbol
            var.updateScope(_declaration.getScope())
            typeSymbol = PredefinedTypes.getTypeIfExists(typeName)
            _declaration.getScope().addSymbol(VariableSymbol(_elementReference=_declaration,
                                                             _scope=_declaration.getScope(),
                                                             _name=var.getCompleteName(),
                                                             _blockType=cls.__currentBlockType,
                                                             _declaringExpression=expression, _isPredefined=False,
                                                             _isFunction=_declaration.isFunction(),
                                                             _isRecordable=isRecordable,
                                                             _typeSymbol=typeSymbol,
                                                             _initialValue=initValue,
                                                             _vectorParameter=vectorParameter
                                                             ))

            var.setTypeSymbol(Either.value(typeSymbol))
            cls.visitVariable(var)
        _declaration.getDataType().updateScope(_declaration.getScope())
        cls.visitDataType(_declaration.getDataType())
        if _declaration.hasExpression():
            _declaration.getExpr().updateScope(_declaration.getScope())
            cls.visitExpression(_declaration.getExpr())
        if _declaration.hasInvariant():
            _declaration.getInvariant().updateScope(_declaration.getScope())
            cls.visitExpression(_declaration.getInvariant())
        return

    @classmethod
    def visitReturnStmt(cls, _returnStmt=None):
        """
        Private method: Used to visit a single return statement and update its scope.
        :param _returnStmt: a return statement object.
        :type _returnStmt: ASTReturnStmt
        """
        from pynestml.nestml.ASTReturnStmt import ASTReturnStmt
        assert (_returnStmt is not None and isinstance(_returnStmt, ASTReturnStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of return statement provided (%s)!' % type(_returnStmt)
        if _returnStmt.hasExpr():
            _returnStmt.getExpr().updateScope(_returnStmt.getScope())
            cls.visitExpression(_returnStmt.getExpr())
        return

    @classmethod
    def visitIfStmt(cls, _ifStmt=None):
        """
        Private method: Used to visit a single if-statement, update its scope and create the corresponding sub-scope.
        :param _ifStmt: an if-statement object.
        :type _ifStmt: ASTIfStmt
        """
        from pynestml.nestml.ASTIfStmt import ASTIfStmt
        assert (_ifStmt is not None and isinstance(_ifStmt, ASTIfStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of if-statement provided (%s)!' % type(_ifStmt)
        _ifStmt.getIfClause().updateScope(_ifStmt.getScope())
        cls.visitIfClause(_ifStmt.getIfClause())
        for elIf in _ifStmt.getElifClauses():
            elIf.updateScope(_ifStmt.getScope())
            cls.visitElifClause(elIf)
        if _ifStmt.hasElseClause():
            _ifStmt.getElseClause().updateScope(_ifStmt.getScope())
            cls.visitElseClause(_ifStmt.getElseClause())
        return

    @classmethod
    def visitIfClause(cls, _ifClause=None):
        """
        Private method: Used to visit a single if-clause, update its scope and create the corresponding sub-scope.
        :param _ifClause: an if clause.
        :type _ifClause: ASTIfClause
        """
        from pynestml.nestml.ASTIfClause import ASTIfClause
        assert (_ifClause is not None and isinstance(_ifClause, ASTIfClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of if-clause provided (%s)!' % type(_ifClause)
        _ifClause.getCondition().updateScope(_ifClause.getScope())
        cls.visitExpression(_ifClause.getCondition())
        _ifClause.getBlock().updateScope(_ifClause.getScope())
        cls.visitBlock(_ifClause.getBlock())
        return

    @classmethod
    def visitElifClause(cls, _elifClause=None):
        """
        Private method: Used to visit a single elif-clause, update its scope and create the corresponding sub-scope.
        :param _elifClause: an elif clause.
        :type _elifClause: ASTElifClause
        """
        from pynestml.nestml.ASTElifClause import ASTElifClause
        assert (_elifClause is not None and isinstance(_elifClause, ASTElifClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of elif-clause provided (%s)!' % type(_elifClause)
        _elifClause.getCondition().updateScope(_elifClause.getScope())
        cls.visitExpression(_elifClause.getCondition())
        _elifClause.getBlock().updateScope(_elifClause.getScope())
        cls.visitBlock(_elifClause.getBlock())
        return

    @classmethod
    def visitElseClause(cls, _elseClause=None):
        """
        Private method: Used to visit a single else-clause, update its scope and create the corresponding sub-scope.
        :param _elseClause: an else clause.
        :type _elseClause: ASTElseClause
        """
        from pynestml.nestml.ASTElseClause import ASTElseClause
        assert (_elseClause is not None and isinstance(_elseClause, ASTElseClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of else-clause provided (%s)!' % type(_elseClause)
        _elseClause.getBlock().updateScope(_elseClause.getScope())
        cls.visitBlock(_elseClause.getBlock())
        return

    @classmethod
    def visitForStmt(cls, _forStmt=None):
        """
        Private method: Used to visit a single for-stmt, update its scope and create the corresponding sub-scope.
        :param _forStmt: a for-statement.
        :type _forStmt: ASTForStmt
        """
        from pynestml.nestml.ASTForStmt import ASTForStmt
        assert (_forStmt is not None and isinstance(_forStmt, ASTForStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of for-statement provided (%s)!' % type(_forStmt)
        _forStmt.getFrom().updateScope(_forStmt.getScope())
        cls.visitExpression(_forStmt.getFrom())
        _forStmt.getTo().updateScope(_forStmt.getScope())
        cls.visitExpression(_forStmt.getTo())
        _forStmt.getBlock().updateScope(_forStmt.getScope())
        cls.visitBlock(_forStmt.getBlock())
        return

    @classmethod
    def visitWhileStmt(cls, _whileStmt=None):
        """
        Private method: Used to visit a single while-stmt, update its scope and create the corresponding sub-scope.
        :param _whileStmt: a while-statement.
        :type _whileStmt: ASTWhileStmt
        """
        from pynestml.nestml.ASTWhileStmt import ASTWhileStmt
        assert (_whileStmt is not None and isinstance(_whileStmt, ASTWhileStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of while-statement provided (%s)!' % type(_whileStmt)
        _whileStmt.getCondition().updateScope(_whileStmt.getScope())
        cls.visitExpression(_whileStmt.getCondition())
        _whileStmt.getBlock().updateScope(_whileStmt.getScope())
        cls.visitBlock(_whileStmt.getBlock())
        return

    @classmethod
    def visitDataType(cls, _dataType=None):
        """
        Private method: Used to visit a single data-type and update its scope.
        :param _dataType: a data-type.
        :type _dataType: ASTDataType
        """
        from pynestml.nestml.ASTDatatype import ASTDatatype
        assert (_dataType is not None and isinstance(_dataType, ASTDatatype)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of data-type provided (%s)!' % type(_dataType)
        if _dataType.isUnitType():
            _dataType.getUnitType().updateScope(_dataType.getScope())
            return cls.visitUnitType(_dataType.getUnitType())
        # besides updating the scope no operations are required, since no type symbols are added to the scope.
        return

    @classmethod
    def visitUnitType(cls, _unitType=None):
        """
        Private method: Used to visit a single unit-type and update its scope.
        :param _unitType: a unit type.
        :type _unitType: ASTUnitType
        """
        from pynestml.nestml.ASTUnitType import ASTUnitType
        assert (_unitType is not None and isinstance(_unitType, ASTUnitType)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of unit-typ provided (%s)!' % type(_unitType)
        if _unitType.isPowerExpression():
            _unitType.getBase().updateScope(_unitType.getScope())
            cls.visitUnitType(_unitType.getBase())
        elif _unitType.isEncapsulated():
            _unitType.getCompoundUnit().updateScope(_unitType.getScope())
            cls.visitUnitType(_unitType.getCompoundUnit())
        elif _unitType.isDiv() or _unitType.isTimes():
            if isinstance(_unitType.getLhs(), ASTUnitType):  # lhs can be a numeric Or a unit-type
                _unitType.getLhs().updateScope(_unitType.getScope())
                cls.visitUnitType(_unitType.getLhs())
            _unitType.getRhs().updateScope(_unitType.getScope())
            cls.visitUnitType(_unitType.getRhs())
        return

    @classmethod
    def visitExpression(cls, _expr=None):
        """
        Private method: Used to visit a single expression and update its scope.
        :param _expr: an expression.
        :type _expr: ASTExpression
        """
        from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression
        from pynestml.nestml.ASTExpression import ASTExpression
        from pynestml.nestml.ASTBitOperator import ASTBitOperator
        from pynestml.nestml.ASTLogicalOperator import ASTLogicalOperator
        from pynestml.nestml.ASTComparisonOperator import ASTComparisonOperator
        if isinstance(_expr, ASTSimpleExpression):
            return cls.visitSimpleExpression(_expr)
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of expression provided (%s)!' % type(_expr)
        if _expr.isLogicalNot():
            _expr.getExpression().updateScope(_expr.getScope())
            cls.visitExpression(_expr.getExpression())
        elif _expr.isEncapsulated():
            _expr.getExpression().updateScope(_expr.getScope())
            cls.visitExpression(_expr.getExpression())
        elif _expr.isUnaryOperator():
            _expr.getUnaryOperator().updateScope(_expr.getScope())
            cls.visitUnaryOperator(_expr.getUnaryOperator())
            _expr.getExpression().updateScope(_expr.getScope())
            cls.visitExpression(_expr.getExpression())
        elif _expr.isCompoundExpression():
            _expr.getLhs().updateScope(_expr.getScope())
            cls.visitExpression(_expr.getLhs())
            _expr.getBinaryOperator().updateScope(_expr.getScope())
            if isinstance(_expr.getBinaryOperator(), ASTBitOperator):
                cls.visitBitOperator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTComparisonOperator):
                cls.visitComparisonOperator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTLogicalOperator):
                cls.visitLogicalOperator(_expr.getBinaryOperator())
            else:
                cls.visitArithmeticOperator(_expr.getBinaryOperator())
            _expr.getRhs().updateScope(_expr.getScope())
            cls.visitExpression(_expr.getRhs())
        if _expr.isTernaryOperator():
            _expr.getCondition().updateScope(_expr.getScope())
            cls.visitExpression(_expr.getCondition())
            _expr.getIfTrue().updateScope(_expr.getScope())
            cls.visitExpression(_expr.getIfTrue())
            _expr.getIfNot().updateScope(_expr.getScope())
            cls.visitExpression(_expr.getIfNot())
        return

    @classmethod
    def visitSimpleExpression(cls, _expr=None):
        """
        Private method: Used to visit a single simple expression and update its scope.
        :param _expr: a simple expression.
        :type _expr: ASTSimpleExpression
        """
        from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression
        assert (_expr is not None and isinstance(_expr, ASTSimpleExpression)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of simple expression provided (%s)!' % type(_expr)
        if _expr.isFunctionCall():
            _expr.getFunctionCall().updateScope(_expr.getScope())
            cls.visitFunctionCall(_expr.getFunctionCall())
        elif _expr.isVariable() or _expr.hasUnit():
            _expr.getVariable().updateScope(_expr.getScope())
            cls.visitVariable(_expr.getVariable())
        return

    @classmethod
    def visitUnaryOperator(cls, _unaryOp=None):
        """
        Private method: Used to visit a single unary operator and update its scope.
        :param _unaryOp: a single unary operator.
        :type _unaryOp: ASTUnaryOperator
        """
        from pynestml.nestml.ASTUnaryOperator import ASTUnaryOperator
        assert (_unaryOp is not None and isinstance(_unaryOp, ASTUnaryOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of unary operator provided (%s)!' % type(_unaryOp)
        return

    @classmethod
    def visitBitOperator(cls, _bitOp=None):
        """
        Private method: Used to visit a single unary operator and update its scope.
        :param _bitOp: a single bit operator.
        :type _bitOp: ASTBitOperator
        """
        from pynestml.nestml.ASTBitOperator import ASTBitOperator
        assert (_bitOp is not None and isinstance(_bitOp, ASTBitOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of bit operator provided (%s)!' % type(_bitOp)
        return

    @classmethod
    def visitComparisonOperator(cls, _comparisonOp=None):
        """
        Private method: Used to visit a single comparison operator and update its scope.
        :param _comparisonOp: a single comparison operator.
        :type _comparisonOp: ASTComparisonOperator
        """
        from pynestml.nestml.ASTComparisonOperator import ASTComparisonOperator
        assert (_comparisonOp is not None and isinstance(_comparisonOp, ASTComparisonOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of comparison operator provided (%s)!' % type(
                _comparisonOp)
        return

    @classmethod
    def visitLogicalOperator(cls, _logicalOp=None):
        """
        Private method: Used to visit a single logical operator and update its scope.
        :param _logicalOp: a single logical operator.
        :type _logicalOp: ASTLogicalOperator
        """
        from pynestml.nestml.ASTLogicalOperator import ASTLogicalOperator
        assert (_logicalOp is not None and isinstance(_logicalOp, ASTLogicalOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of logical operator provided (%s)!' % type(_logicalOp)
        return

    @classmethod
    def visitVariable(cls, _variable=None):
        """
        Private method: Used to visit a single variable and update its scope.
        :param _variable: a single variable.
        :type _variable: ASTVariable
        """
        from pynestml.nestml.ASTVariable import ASTVariable
        assert (_variable is not None and isinstance(_variable, ASTVariable)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of variable provided (%s)!' % type(_variable)
        return

    @classmethod
    def visitOdeFunction(cls, _odeFunction=None):
        """
        Private method: Used to visit a single ode-function, create the corresponding symbol and update the scope.
        :param _odeFunction: a single ode-function.
        :type _odeFunction: ASTOdeFunction
        """
        from pynestml.nestml.ASTOdeFunction import ASTOdeFunction
        from pynestml.nestml.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        from pynestml.nestml.VariableSymbol import BlockType
        assert (_odeFunction is not None and isinstance(_odeFunction, ASTOdeFunction)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-function provided (%s)!' % type(_odeFunction)
        typeSymbol = PredefinedTypes.getTypeIfExists(ASTUnitTypeVisitor.visitDatatype(_odeFunction.getDataType()))
        symbol = VariableSymbol(_elementReference=_odeFunction, _scope=_odeFunction.getScope(),
                                _name=_odeFunction.getVariableName(),
                                _blockType=BlockType.EQUATION,
                                _declaringExpression=_odeFunction.getExpression(),
                                _isPredefined=False, _isFunction=True,
                                _isRecordable=_odeFunction.isRecordable(),
                                _typeSymbol=typeSymbol)
        _odeFunction.getScope().addSymbol(symbol)
        _odeFunction.getDataType().updateScope(_odeFunction.getScope())
        cls.visitDataType(_odeFunction.getDataType())
        _odeFunction.getExpression().updateScope(_odeFunction.getScope())
        cls.visitExpression(_odeFunction.getExpression())
        return

    @classmethod
    def visitOdeShape(cls, _odeShape=None):
        """
        Private method: Used to visit a single ode-shape, create the corresponding symbol and update the scope.
        :param _odeShape: a single ode-shape.
        :type _odeShape: ASTOdeShape
        """
        from pynestml.nestml.ASTOdeShape import ASTOdeShape
        from pynestml.nestml.VariableSymbol import VariableSymbol, BlockType
        assert (_odeShape is not None and isinstance(_odeShape, ASTOdeShape)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-shape provided (%s)!' % type(_odeShape)
        symbol = VariableSymbol(_elementReference=_odeShape, _scope=_odeShape.getScope(),
                                _name=_odeShape.getVariable().getName(),
                                _blockType=BlockType.SHAPE,
                                _declaringExpression=_odeShape.getExpression(),
                                _isPredefined=False, _isFunction=False,
                                _isRecordable=True,
                                _typeSymbol=PredefinedTypes.getRealType())
        _odeShape.getScope().addSymbol(symbol)
        _odeShape.getVariable().updateScope(_odeShape.getScope())
        cls.visitVariable(_odeShape.getVariable())
        _odeShape.getExpression().updateScope(_odeShape.getScope())
        cls.visitExpression(_odeShape.getExpression())
        return

    @classmethod
    def visitOdeEquation(cls, _equation=None):
        """
        Private method: Used to visit a single ode-equation and update the corresponding scope.
        :param _equation: a single ode-equation.
        :type _equation: ASTOdeEquation
        """
        from pynestml.nestml.ASTOdeEquation import ASTOdeEquation
        assert (_equation is not None and isinstance(_equation, ASTOdeEquation)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-equation provided (%s)!' % type(_equation)
        _equation.getLhs().updateScope(_equation.getScope())
        cls.visitVariable(_equation.getLhs())
        _equation.getRhs().updateScope(_equation.getScope())
        cls.visitExpression(_equation.getRhs())
        return

    @classmethod
    def visitBlockWithVariables(cls, _block=None):
        """
        Private method: Used to visit a single block of variables and update its scope.
        :param _block: a block with declared variables.
        :type _block: ASTBlockWithVariables
        """
        from pynestml.nestml.ASTBlockWithVariables import ASTBlockWithVariables
        from pynestml.nestml.VariableSymbol import BlockType
        assert (_block is not None and isinstance(_block, ASTBlockWithVariables)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of block with variables provided (%s)!' % type(_block)
        cls.__currentBlockType = BlockType.STATE if _block.isState() else \
            BlockType.INTERNALS if _block.isInternals() else BlockType.PARAMETERS if _block.isParameters() else \
                BlockType.INITIAL_VALUES
        for decl in _block.getDeclarations():
            decl.updateScope(_block.getScope())
            cls.visitDeclaration(decl)
        cls.__currentBlockType = None
        return

    @classmethod
    def visitEquationsBlock(cls, _block=None):
        """
        Private method: Used to visit a single equations block and update its scope.
        :param _block: a single equations block.
        :type _block: ASTEquationsBlock
        """
        from pynestml.nestml.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.nestml.ASTOdeFunction import ASTOdeFunction
        from pynestml.nestml.ASTOdeShape import ASTOdeShape
        assert (_block is not None and isinstance(_block, ASTEquationsBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of equations block provided (%s)!' % type(_block)
        for decl in _block.getDeclarations():
            decl.updateScope(_block.getScope())
            if isinstance(decl, ASTOdeFunction):
                cls.visitOdeFunction(decl)
            elif isinstance(decl, ASTOdeShape):
                cls.visitOdeShape(decl)
            else:
                cls.visitOdeEquation(decl)
        return

    @classmethod
    def visitInputBlock(cls, _block=None):
        """
        Private method: Used to visit a single input block and update its scope.
        :param _block: a single input block.
        :type _block: ASTInputBlock
        """
        from pynestml.nestml.ASTInputBlock import ASTInputBlock
        assert (_block is not None and isinstance(_block, ASTInputBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-block provided (%s)!' % type(_block)
        for line in _block.getInputLines():
            line.updateScope(_block.getScope())
            cls.visitInputLine(line)
        return

    @classmethod
    def visitOutputBlock(cls, _block=None):
        """
        Private method: Used to visit a single output block and visit its scope.
        :param _block: a single output block.
        :type _block: ASTOutputBlock
        """
        from pynestml.nestml.ASTOutputBlock import ASTOutputBlock
        assert (_block is not None and isinstance(_block, ASTOutputBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of output-block provided (%s)!' % type(_block)
        return

    @classmethod
    def visitInputLine(cls, _line=None):
        """
        Private method: Used to visit a single input line, create the corresponding symbol and update the scope.
        :param _line: a single input line.
        :type _line: ASTInputLine
        """
        from pynestml.nestml.ASTInputLine import ASTInputLine
        from pynestml.nestml.VariableSymbol import BlockType
        assert (_line is not None and isinstance(_line, ASTInputLine)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-line provided (%s)!' % type(_line)
        from pynestml.nestml.VariableSymbol import VariableSymbol
        bufferType = BlockType.INPUT_BUFFER_SPIKE if _line.isSpike() else BlockType.INPUT_BUFFER_CURRENT
        if _line.isSpike() and _line.hasDatatype():
            _line.getDatatype().updateScope(_line.getScope())
            cls.visitDataType(_line.getDatatype())
            typeSymbol = _line.getDatatype().getTypeSymbol()
        elif _line.isSpike():
            Logger.logMessage('No spike buffer type declared, nS as unit assumed!', LOGGING_LEVEL.WARNING)
            typeSymbol = PredefinedTypes.getTypeIfExists('nS')
        else:
            typeSymbol = PredefinedTypes.getTypeIfExists('pA')
        typeSymbol.setBuffer(True)  # set it as a buffer
        symbol = VariableSymbol(_elementReference=_line, _scope=_line.getScope(), _name=_line.getName(),
                                _blockType=bufferType, _vectorParameter=_line.getIndexParameter(),
                                _isPredefined=False, _isFunction=False, _isRecordable=False,
                                _typeSymbol=typeSymbol)
        _line.getScope().addSymbol(symbol)
        for inputType in _line.getInputTypes():
            cls.visitInputType(inputType)
            inputType.updateScope(_line.getScope())
        return

    @classmethod
    def visitInputType(cls, _type=None):
        """
        Private method: Used to visit a single input type and update its scope.
        :param _type: a single input-type.
        :type _type: ASTInputType
        """
        from pynestml.nestml.ASTInputType import ASTInputType
        assert (_type is not None and isinstance(_type, ASTInputType)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-type provided (%s)!' % type(_type)
        return

    @classmethod
    def visitArithmeticOperator(cls, _arithmeticOp=None):
        """
        Private method: Used to visit a single arithmetic operator and update its scope.
        :param _arithmeticOp: a single arithmetic operator.
        :type _arithmeticOp: ASTArithmeticOperator
        """
        from pynestml.nestml.ASTArithmeticOperator import ASTArithmeticOperator
        assert (_arithmeticOp is not None and isinstance(_arithmeticOp, ASTArithmeticOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of arithmetic operator provided (%s)!' % type(
                _arithmeticOp)
        return

    @classmethod
    def markConductanceBasedBuffers(cls, _odeDeclarations=None, _inputLines=None):
        """
        Inspects all handed over buffer definitions and updates them to conductance based if they occur as part of
        a cond_sum expression.
        :param _odeDeclarations: a set of ode declarations.
        :type _odeDeclarations: ASTOdeEquation,ASTOdeFunction
        :param _inputLines: a set of input buffers.
        :type _inputLines: ASTInputLine
        """
        from pynestml.nestml.ASTOdeEquation import ASTOdeEquation
        from pynestml.nestml.Symbol import SymbolKind
        # check for each defined buffer
        for buffer in _inputLines:
            # we only check it for spike buffers
            if buffer.isSpike():
                # and each function call in each declaration if it occurs as the second arg of a cond_sum
                for decl in _odeDeclarations:
                    if isinstance(decl, ASTOdeEquation):
                        expression = decl.getRhs()
                    else:
                        expression = decl.getExpression()
                    for func in expression.getFunctions():
                        if func.getName() == 'cond_sum' and func.hasArgs() and func.getArgs()[
                            1].printAST() == buffer.getName():
                            symbol = cls.__globalScope.resolveToAllSymbols(buffer.getName(), SymbolKind.VARIABLE)
                            symbol.setConductanceBased(True)
                            Logger.logMessage('Buffer ' + buffer.getName() + ' set to conductance based!',
                                              LOGGING_LEVEL.INFO)

        return

    @classmethod
    def assignOdeToVariables(cls, _odeBlock=None):
        """
        Adds for each variable symbol the corresponding ode declaration if present.
        :param _odeBlock: a single block of ode declarations.
        :type _odeBlock: ASTEquations
        """
        from pynestml.nestml.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.nestml.ASTOdeEquation import ASTOdeEquation
        assert (_odeBlock is not None and isinstance(_odeBlock, ASTEquationsBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of equations block provided (%s)!' % type(_odeBlock)
        for decl in _odeBlock.getDeclarations():
            if isinstance(decl, ASTOdeEquation):
                cls.addOdeToVariable(decl)
        return

    @classmethod
    def addOdeToVariable(cls, _odeEquation=None):
        """
        Resolves to the corresponding symbol and updates the corresponding ode-declaration. In the case that
        :param _odeEquation: a single ode-equation
        :type _odeEquation: ASTOdeEquation
        """
        from pynestml.nestml.ASTOdeEquation import ASTOdeEquation
        from pynestml.nestml.Symbol import SymbolKind
        assert (_odeEquation is not None and isinstance(_odeEquation, ASTOdeEquation)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of equation provided (%s)!' % type(_odeEquation)
        # the definition of a differential equations is defined by stating the derivation, thus derive the actual order
        diffOrder = _odeEquation.getLhs().getDifferentialOrder() - 1
        # we check if the corresponding symbol already exists, e.g. V_m' has already been declared
        existingSymbol = cls.__globalScope.resolveToSymbol(_odeEquation.getLhs().getName() + '\'' * diffOrder,
                                                           SymbolKind.VARIABLE)
        if existingSymbol is not None:
            existingSymbol.setOdeDefinition(_odeEquation.getRhs())
            Logger.logMessage('Ode of %s updated.' % _odeEquation.getLhs().getName(),
                              LOGGING_LEVEL.INFO)
        else:
            # create a new symbol, however, this should never happen since only exiting symbols shall be updated
            # if an existing symbol does not exists, we derive the base symbol, e.g. V_m
            baseSymbol = cls.__globalScope.resolveToAllSymbols(_odeEquation.getLhs().getName(), SymbolKind.VARIABLE)
            if baseSymbol is not None:
                newSymbol = VariableSymbol(_elementReference=_odeEquation, _scope=cls.__globalScope,
                                           _name=_odeEquation.getLhs().getName() + '\'' * diffOrder,
                                           _blockType=BlockType.EQUATION,
                                           _declaringExpression=_odeEquation.getRhs(),
                                           _isPredefined=False, _isFunction=False, _isRecordable=False,
                                           _typeSymbol=PredefinedTypes.
                                           getTypeIfExists(baseSymbol.getType().getValue().printSymbol()))  # todo
                cls.__globalScope.addSymbol(newSymbol)
                Logger.logMessage('Ode declaration added to %s.' % _odeEquation.getLhs().getName(),
                                  LOGGING_LEVEL.INFO)
            else:
                Logger.logMessage('No corresponding variable of %s found.' % _odeEquation.getLhs().getName(),
                                  LOGGING_LEVEL.ERROR)
        return
