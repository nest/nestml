from pynestml.src.main.python.org.nestml.ast import ASTArithmeticOperator, ASTBitOperator, ASTComparisonOperator, \
    ASTLogicalOperator
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor


class ExpressionTypeVisitor(NESTMLVisitor):
    __unaryVisitor = UnaryVisitor()
    __powVisitor  = PowVisitor()
    __parenthesesVisitor = ParenthesesVisitor()
    __logicalNotVisitor = LogicalNotVisitor()
    __dotOperatorVisitor = DotOperatorVisitor()
    __lineOperatorVisitor = LineOperatorVisitor()
    __noSemantics = NoSemantics()
    __comparisonOperatorVisitor = ComparisonOperatorVisitor()
    __binaryLogicVisitor = BinaryLogicVisitor()
    __conditionVisitor = ConditionVisitor()
    __functionCallVisitor = FunctionCallVisitor()
    __booleanLiteralVisitor = BooleanLiteralVisitor()
    __numericLiteralVisitor = NumericLiteralVisitor()
    __stringLiteralVisitor = StringLiteralVisitor()
    __variableVisitor = new VariableVisitor()
    __infVisitor = InfVisitor()

    def handle(self,_node):
        self.traverse(_node)
        self.getRealSelf().visit(_node)
        self.getRealSelf().endVisit(_node)
        return


    def traverseExpression(self, _node):
        #Expr = unaryOperator term=expression
        if _node.getTerm() is not None and _node.getUnaryOperator() is not None:
            _node.getTerm().accept(self)
            self.setRealThis(self.__unaryVisitor)
            return

        #Parentheses and logicalNot
        if _node.getExpression() is not None and not _node.isSimpleExpression():
            _node.getExpression().accept(self)
            #Expr = leftParentheses='(' term=expression rightParentheses=')'
            if _node.hasLeftParentheses() and _node.hasRightParentheses():
                self.setRealSelf(self.__parenthesesVisitor)
                return
            #Expr = logicalNot='not' term=expression
            if _node.isLogicalNot():
                self.setRealSelf(self.__logicalNotVisitor)
                return

        #Rules with binary operators
        if _node.getBinaryOperator() is not None:
            binOp = _node.getBinaryOperator()
            # All these rules employ left and right side expressions.
            if _node.getLeft() is not None:
                _node.getLeft().accept(self)
            if _node.getRight() is not None:
                _node.getRight().accept(self)
            #Handle all Arithmetic Operators:
            if isinstance(binOp,ASTArithmeticOperator.ASTArithmeticOperator):
                #Expr = <assoc=right> left=expression powOp='**' right=expression
                if binOp.isPowOp():
                    self.setRealSelf(self.__powVisitor)
                    return
                # Expr = left=expression (timesOp='*' | divOp='/' | moduloOp='%') right=expression
                if binOp.isTimesOp() or binOp.isDivOp() or binOp.isModuloOp():
                    self.setRealSelf(self.__dotOperatorVisitor)
                    return
                #Expr = left=expression (plusOp='+'  | minusOp='-') right=expression
                if binOp.isPlusOp() or binOp.isMinusOp():
                    self.setRealSelf(self.__lineOperatorVisitor)
                    return
            #handle all bitOperators:
            if isinstance(binOp,ASTBitOperator.ASTBitOperator):
                #Expr = left=expression bitOperator right=expression
                self.setRealSelf(self.__noSemantics) #TODO: implement something
                return
            #handle all comparison Operators:
            if isinstance(binOp,ASTComparisonOperator.ASTComparisonOperator):
                #Expr = left=expression comparisonOperator right=expression
               self.setRealSelf(self.__comparisonOperatorVisitor)
               return
            #handle all logical Operators
            if isinstance(binOp,ASTLogicalOperator.ASTLogicalOperator):
                #Expr = left=expression logicalOperator right=expression
                self.setRealSelf(self.__binaryLogicVisitor)
                return

        #Expr = condition=expression '?' ifTrue=expression ':' ifNot=expression
        if _node.getCondition() is not None and _node.getIfTrue() is not None and _node.getIfNot() is not None:
            _node.getCondition().accept(self)
            _node.getIfTrue().accept(self)
            _node.getIfNot().accept(self)
            self.setRealSelf(self.__conditionVisitor)
            return

        # handle all simpleexpressions
        if _node.isSimpleExpression():
            #simpleExpression = functionCall
            simpEx = _node.getExpression()
            if simpEx.getFunctionCall() is not None:
                self.setRealSelf(self.__functionCallVisitor)
                return
            #simpleExpression =  variable
            if simpEx.getVariable() is not None:
                self.setRealSelf(self.__variableVisitor)
                return
            #simpleExpression = BOOLEAN_LITERAL
            if simpEx.isBooleanTrue() or simpEx.isBooleanFalse():
                self.setRealSelf(self.__booleanLiteralVisitor)
                return
            #simpleExpression = isInf='inf'
            if simpEx.isInfLiteral():
                self.setRealSelf(self.__infVisitor)
                return
            #simpleExpression = string=STRING_LITERAL
            if simpEx.isString():
                self.setRealSelf(self.__stringLiteralVisitor)
                return
            #simpleExpression =  (INTEGER|FLOAT) (variable)?
            if simpEx.getNumericLiteral() is not None or \
                    (simpEx.getNumericLiteral() is not None and simpEx.getVariable() is not None):
                self.setRealSelf(self.__numericLiteralVisitor)
                return