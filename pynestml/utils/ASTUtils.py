#
# ASTUtils.py
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
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.Symbol import SymbolKind


class ASTUtils(object):
    """
    A collection of helpful methods.
    """

    @classmethod
    def getAllNeurons(cls, _listOfCompilationUnits=list()):
        """
        For a list of compilation units, it returns a list containing all neurons defined in all compilation
        units.
        :param _listOfCompilationUnits: a list of compilation units.
        :type _listOfCompilationUnits: list(ASTNESTMLCompilationUnit)
        :return: a list of neurons
        :rtype: list(ASTNeuron)
        """
        ret = list()
        for compilationUnit in _listOfCompilationUnits:
            ret.extend(compilationUnit.getNeuronList())
        return ret

    @classmethod
    def isSmallStmt(cls, _ast=None):
        """
        Indicates whether the handed over ast is a small statement. Used in the template.
        :param _ast: a single ast object.
        :type _ast: AST_
        :return: True if small stmt, otherwise False.
        :rtype: bool
        """
        from pynestml.nestml.ASTSmallStmt import ASTSmallStmt
        return isinstance(_ast, ASTSmallStmt)

    @classmethod
    def isCompoundStmt(cls, _ast=None):
        """
        Indicates whether the handed over ast is a compound statement. Used in the template.
        :param _ast: a single ast object.
        :type _ast: AST_
        :return: True if compound stmt, otherwise False.
        :rtype: bool
        """
        from pynestml.nestml.ASTCompoundStmt import ASTCompoundStmt
        return isinstance(_ast, ASTCompoundStmt)

    @classmethod
    def printComments(cls, _ast=None):
        """
        Prints all comments belonging to this node.
        :param _ast: a single ast node.
        :type _ast: AST_
        :return: all comments in the node
        :rtype: str
        """
        return "TODO comments of ast node"

    @classmethod
    def isIntegrate(cls, _functionCall=None):
        """
        Checks if the handed over function call is a ode integration function call.
        :param _functionCall: a single function call
        :type _functionCall: ASTFunctionCall
        :return: True if ode integration call, otherwise False.
        :rtype: bool
        """
        from pynestml.nestml.ASTFunctionCall import ASTFunctionCall
        from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
        assert (_functionCall is not None and isinstance(_functionCall, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of function-call provided (%s)!' % type(_functionCall)
        return _functionCall.getName() == PredefinedFunctions.INTEGRATE_ODES

    @classmethod
    def isSpikeInput(cls, _body=None):
        """
        Checks if the handed over neuron contains a spike input buffer.
        :param _body: a single body element.
        :type _body: ASTBody
        :return: True if spike buffer is contained, otherwise false.
        :rtype: bool
        """
        from pynestml.nestml.ASTBody import ASTBody
        assert (_body is not None and isinstance(_body, ASTBody)), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of body provided (%s)!' % type(_body)
        inputs = (inputL for block in _body.getInputBlocks() for inputL in block.getInputLines())
        for inputL in inputs:
            if inputL.isSpike():
                return True
        return False

    @classmethod
    def isCurrentInput(cls, _body=None):
        """
        Checks if the handed over neuron contains a current input buffer.
        :param _body: a single body element.
        :type _body: ASTBody
        :return: True if current buffer is contained, otherwise false.
        :rtype: bool
        """
        from pynestml.nestml.ASTBody import ASTBody
        assert (_body is not None and isinstance(_body, ASTBody)), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of body provided (%s)!' % type(_body)
        inputs = (inputL for block in _body.getInputBlocks() for inputL in block.getInputLines())
        for inputL in inputs:
            if inputL.isCurrent():
                return True
        return False

    @classmethod
    def computeTypeName(cls, _dataType=None):
        """
        Computes the representation of the data type.
        :param _dataType: a single data type.
        :type _dataType: ASTDataType
        :return: the corresponding representation.
        :rtype: str
        """
        from pynestml.nestml.ASTDatatype import ASTDatatype
        assert (_dataType is not None and isinstance(_dataType, ASTDatatype)), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of data type provided (%s)!' % type(_dataType)
        if _dataType.isBoolean():
            return 'boolean'
        elif _dataType.isInteger():
            return 'integer'
        elif _dataType.isReal():
            return 'real'
        elif _dataType.isString():
            return 'string'
        elif _dataType.isVoid():
            return 'void'
        elif _dataType.isUnitType():
            # TODO
            return 'TODO'
        else:
            Logger.logMessage('Type could not be derived!', LOGGING_LEVEL.ERROR)
            return ''

    @classmethod
    def deconstructAssignment(cls, _lhs=None, _isPlus=False, _isMinus=False, _isTimes=False, _isDivide=False,
                              _rhs=None):
        """
        From lhs and rhs it constructs a new expression which corresponds to direct assignment.
        E.g.: a += b*c -> a = a + b*c
        :param _lhs: a lhs expression
        :type _lhs: ASTExpression or ASTSimpleExpression
        :param _isPlus: is plus assignment
        :type _isPlus: bool
        :param _isMinus: is minus assignment
        :type _isMinus: bool
        :param _isTimes: is times assignment
        :type _isTimes: bool
        :param _isDivide: is divide assignment
        :type _isDivide: bool
        :param _rhs: a rhs expression
        :type _rhs: ASTExpression or ASTSimpleExpression
        :return: a new direct assignment expression.
        :rtype: ASTExpression
        """
        from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression
        from pynestml.nestml.ASTExpression import ASTExpression
        from pynestml.nestml.ASTArithmeticOperator import ASTArithmeticOperator
        from pynestml.nestml.ASTVariable import ASTVariable
        from pynestml.nestml.ASTSymbolTableVisitor import SymbolTableASTVisitor
        assert (_lhs is not None and isinstance(_lhs, ASTVariable)), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of lhs variable provided (%s)!' % type(_lhs)
        assert (_rhs is not None and (isinstance(_rhs, ASTSimpleExpression) or isinstance(_rhs, ASTExpression))), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of rhs expression provided (%s)!' % type(_rhs)
        assert ((_isPlus + _isMinus + _isTimes + _isDivide) == 1), \
            '(PyNestML.CodeGeneration.Utils) Type of assignment not correctly specified!'
        if _isPlus:
            op = ASTArithmeticOperator(_isPlusOp=True)
        elif _isMinus:
            op = ASTArithmeticOperator(_isMinusOp=True)
        elif _isTimes:
            op = ASTArithmeticOperator(_isTimesOp=True)
        else:
            op = ASTArithmeticOperator(_isDivOp=True)
        varExpr = ASTSimpleExpression.makeASTSimpleExpression(_variable=_lhs)
        varExpr.updateScope(_lhs.getScope())
        op.updateScope(_lhs.getScope())
        rhsInBrackets = ASTExpression.makeExpression(_isEncapsulated=True, _expression=_rhs)
        rhsInBrackets.updateScope(_rhs.getScope())
        expr = ASTExpression.makeCompoundExpression(_lhs=varExpr, _binaryOperator=op, _rhs=rhsInBrackets)
        expr.updateScope(_lhs.getScope())
        # update the symbols
        SymbolTableASTVisitor.visitExpression(expr)
        return expr

    @classmethod
    def getAliasSymbolsFromOdes(cls, _list=list()):
        """"
        For a handed over list this
        :param _list:
        :type _list:
        :return:
        :rtype:
        """
        pass

    @classmethod
    def getAliasSymbols(cls, _ast=None):
        """
        For the handed over ast, this method collects all functions aka. aliases in it.
        :param _ast: a single ast node
        :type _ast: AST_
        :return: a list of all alias variable symbols
        :rtype: list(VariableSymbol)
        """
        assert (_ast is not None), '(PyNestML.Utils) No AST provided!'
        variableCollector = VariableCollector()
        _ast.accept(variableCollector)
        ret = list()
        for var in variableCollector.result():
            if '\'' not in var.getCompleteName():
                symbol = _ast.getScope().resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE)
                if symbol.isFunction():
                    ret.append(symbol)
        return ret

    @classmethod
    def isCastableTo(cls, _typeA=None, _typeB=None):
        """
        Indicates whether typeA can be casted to type b. E.g., in Nest, a unit is always casted down to real, thus
        a unit where unit is expected is allowed.
        :param _typeA: a single TypeSymbol
        :type _typeA: TypeSymbol
        :param _typeB: a single TypeSymbol
        :type _typeB: TypeSymbol
        :return: True if castable, otherwise False
        :rtype: bool
        """
        from pynestml.nestml.TypeSymbol import TypeSymbol
        assert (_typeA is not None and isinstance(_typeA, TypeSymbol)), \
            '(PyNestML.Utils) No or wrong type of source type provided (%s)!' % type(_typeA)
        assert (_typeB is not None and isinstance(_typeB, TypeSymbol)), \
            '(PyNestML.Utils) No or wrong type of target type provided (%s)!' % type(_typeB)
        # we can always cast from unit to real
        if _typeA.hasUnit() and _typeB.isReal():
            return True
        elif _typeA.isBoolean() and _typeB.isReal():
            return True
        elif _typeA.isReal() and _typeB.isBoolean():
            return True
        elif _typeA.isInteger() and _typeB.isReal():
            return True
        elif _typeA.isReal() and _typeB.isInteger():
            return True
        else:
            return False

    @classmethod
    def getAll(cls, _ast=None, _type=None):
        """
        Finds all ast which are part of the tree as spanned by the handed over ast. The type has to be specified.
        :param _ast: a single ast node
        :type _ast: AST_
        :param _type: the type
        :type _type: AST_
        :return: a list of all ast of the specified type
        :rtype: list(AST_)
        """
        from pynestml.nestml.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        ret = list()
        ASTHigherOrderVisitor.visit(_ast, lambda x: ret.append(x) if isinstance(x, _type) else True)
        return ret

    @classmethod
    def getVectorizedVariable(cls, _ast=None, _scope=None):
        """
        Returns all variable symbols which are contained in the scope and have a size parameter.
        :param _ast: a single ast
        :type _ast: AST_
        :param _scope: a scope object
        :type _scope: Scope
        :return: the first element with the size parameter
        :rtype: VariableSymbol
        """
        from pynestml.nestml.ASTVariable import ASTVariable
        from pynestml.nestml.Symbol import SymbolKind
        variables = (var for var in cls.getAll(_ast, ASTVariable) if
                     _scope.resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE))
        for var in variables:
            symbol = _scope.resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE)
            if symbol is not None and symbol.hasVectorParameter():
                return symbol
        return None

    @classmethod
    def getFunctionCall(cls, _ast=None, _functionName=None):
        """
        Collects for a given name all function calls in a given ast node.
        :param _ast: a single node
        :type _ast: AST_
        :param _functionName:
        :type _functionName:
        :return: a list of all function calls contained in _ast
        :rtype: list(ASTFunctionCall)
        """
        from pynestml.nestml.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        from pynestml.nestml.ASTFunctionCall import ASTFunctionCall
        ret = list()
        ASTHigherOrderVisitor.visit(_ast, lambda x: ret.append(x) \
            if isinstance(x, ASTFunctionCall) and x.getName() == _functionName else True)
        return ret

    @classmethod
    def getTupleFromSingleDictEntry(cls, _dictEntry=None):
        """
        For a given dict of length 1, this method returns a tuple consisting of (key,value)
        :param _dictEntry: a dict of length 1
        :type _dictEntry:  dict
        :return: a single tuple
        :rtype: tuple
        """
        if len(_dictEntry.keys()) == 1:
            # key() is not an actual list, thus indexing is not possible.
            for keyIter in _dictEntry.keys():
                key = keyIter
                value = _dictEntry[key]
                return key, value
        else:
            return None, None


class VariableCollector(NESTMLVisitor):
    """
    Collects all variables contained in the node or one of its sub-nodes.
    """
    __result = None

    def __init__(self):
        super(VariableCollector, self).__init__()
        self.__result = list()

    def result(self):
        """
        Returns all collected variables.
        :return: a list of variables.
        :rtype: list(ASTVariable)
        """
        return self.__result

    def visitVariable(self, _variable=None):
        """
        Visits a single node and ads it to results.
        :param _variable:
        :type _variable:
        :return:
        :rtype:
        """
        self.__result.append(_variable)
        return
