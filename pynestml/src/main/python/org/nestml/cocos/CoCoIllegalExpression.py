#
# CoCoIllegalExpression.py
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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes


class CoCoIllegalExpression(CoCo):
    """
    This coco checks that all expressions are correctly typed.
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(CorrectExpressionVisitor())
        return


class CorrectExpressionVisitor(NESTMLVisitor):
    """
    This visitor checks that all expression correspond to the expected type.
    """

    def visitDeclaration(self, _declaration=None):
        """
        Visits a single declaration and asserts that type of lhs is equal to type of rhs.
        :param _declaration: a single declaration.
        :type _declaration: ASTDeclaration
        """
        if _declaration.hasExpression():
            lhsType = _declaration.getDataType().getTypeSymbol()
            rhsType = _declaration.getExpr().getTypeEither()
            if rhsType.isError():
                Logger.logMessage('Type of rhs-expression "%s" at %s could not be derived!'
                                  % (_declaration.getExpr().printAST(),
                                     _declaration.getSourcePosition().printSourcePosition()),
                                  LOGGING_LEVEL.ERROR)
            elif not lhsType.equals(rhsType.getValue()):
                Logger.logMessage('Type of lhs does not correspond to expression type at %s! LHS: %s,RHS: %s.'
                                  % (_declaration.getSourcePosition().printSourcePosition(),
                                     lhsType.printSymbol(),
                                     rhsType.getValue().printSymbol()),
                                  LOGGING_LEVEL.ERROR)
        # todo we have to consider that different magnitudes can still be combined
        return

    def visitAssignment(self, _assignment=None):
        """
        Visits a single expression and assures that type(lhs) == type(rhs).
        :param _assignment: a single assignment.
        :type _assignment: ASTAssignment
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
        if _assignment.isDirectAssignment():  # case a = b is simple
            lhsSymbolType = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                                   SymbolKind.VARIABLE)
            rhsSymbolType = _assignment.getExpression().getTypeEither()
            if rhsSymbolType.isError():
                Logger.logMessage('Type of rhs-expression "%s" at %s could not be derived!'
                                  % (_assignment.getExpression().printAST(),
                                     _assignment.getSourcePosition().printSourcePosition()),
                                  LOGGING_LEVEL.ERROR)
            elif lhsSymbolType is not None and not lhsSymbolType.getTypeSymbol().equals(rhsSymbolType.getValue()):
                Logger.logMessage('Type of lhs does not correspond to expression type at %s! LHS: %s,RHS: %s.'
                                  % (_assignment.getSourcePosition().printSourcePosition(),
                                     lhsSymbolType.getTypeSymbol().printSymbol(),
                                     rhsSymbolType.getValue().printSymbol()),
                                  LOGGING_LEVEL.ERROR)
        else:
            from pynestml.src.main.python.org.utils.ASTUtils import ASTUtils
            expr = ASTUtils.deconstructAssignment(_lhs=_assignment.getVariable(),
                                                  _isPlus=_assignment.isCompoundSum(),
                                                  _isMinus=_assignment.isCompoundMinus(),
                                                  _isTimes=_assignment.isCompoundProduct(),
                                                  _isDivide=_assignment.isCompoundQuotient(),
                                                  _rhs=_assignment.getExpression())
            lhsSymbolType = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                                   SymbolKind.VARIABLE)
            rhsSymbolType = expr.getTypeEither()
            if rhsSymbolType.isError():
                Logger.logMessage('Type of rhs-expression "%s" at %s could not be derived!'
                                  % (_assignment.getExpression().printAST(),
                                     _assignment.getSourcePosition().printSourcePosition()),
                                  LOGGING_LEVEL.ERROR)
            elif lhsSymbolType is not None and not lhsSymbolType.getTypeSymbol().equals(rhsSymbolType.getValue()):
                Logger.logMessage('Type of lhs does not correspond to expression type at %s! LHS: %s,RHS: %s.'
                                  % (_assignment.getSourcePosition().printSourcePosition(),
                                     lhsSymbolType.getTypeSymbol().printSymbol(),
                                     rhsSymbolType.getValue().printSymbol()),
                                  LOGGING_LEVEL.ERROR)
        return

    def visitIfClause(self, _ifClause=None):
        """
        Visits a single if clause and checks that its condition is boolean.
        :param _ifClause: a single elif clause.
        :type _ifClause: ASTIfClause
        """
        condType = _ifClause.getCondition().getTypeEither()
        if condType.isError():
            Logger.logMessage('Type of condition-expression of if clause "%s" at %s could not be derived!'
                              % (_ifClause.getCondition().printAST(),
                                 _ifClause.getSourcePosition().printSourcePosition()),
                              LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            Logger.logMessage('Type of condition-expression of if clause "%s" at %s wrong! Expected bool, got %s!'
                              % (_ifClause.getCondition().printAST(),
                                 _ifClause.getSourcePosition().printSourcePosition(),
                                 condType.getValue().printSymbol()),
                              LOGGING_LEVEL.ERROR)
        return

    def visitElifClause(self, _elifClause=None):
        """
        Visits a single elif clause and checks that its condition is boolean.
        :param _elifClause: a single elif clause.
        :type _elifClause: ASTElifClause
        """
        condType = _elifClause.getCondition().getTypeEither()
        if condType.isError():
            Logger.logMessage('Type of condition-expression of elif clause "%s" at %s could not be derived!'
                              % (_elifClause.getCondition().printAST(),
                                 _elifClause.getSourcePosition().printSourcePosition()),
                              LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            Logger.logMessage('Type of condition-expression of elif clause "%s" at %s wrong! Expected bool, got %s!'
                              % (_elifClause.getCondition().printAST(),
                                 _elifClause.getSourcePosition().printSourcePosition(),
                                 condType.getValue().printSymbol()),
                              LOGGING_LEVEL.ERROR)
        return

    def visitWhileStmt(self, _whileStmt=None):
        """
        Visits a single while stmt and checks that its condition is of boolean type.
        :param _whileStmt: a single while stmt
        :type _whileStmt: ASTWhileStmt
        """
        condType = _whileStmt.getCondition().getTypeEither()
        if condType.isError():
            Logger.logMessage('Type of condition-expression of while statement "%s" at %s could not be derived!'
                              % (_whileStmt.getCondition().printAST(),
                                 _whileStmt.getSourcePosition().printSourcePosition()),
                              LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            Logger.logMessage('Type of condition-expression of while statement "%s" at %s wrong! Expected bool, got %s!'
                              % (_whileStmt.getCondition().printAST(),
                                 _whileStmt.getSourcePosition().printSourcePosition(),
                                 condType.getValue().printSymbol()),
                              LOGGING_LEVEL.ERROR)
        return

    def visitForStmt(self, _forStmt=None):
        """
        Visits a single for stmt and checks that all it parts are correctly defined.
        :param _forStmt: a single for stmt
        :type _forStmt: ASTForStmt
        """
        # check that the from stmt is an integer or real
        fromType = _forStmt.getFrom().getTypeEither()
        if fromType.isError():
            Logger.logMessage('Type of from-expression of for statement "%s" at %s could not be derived!'
                              % (_forStmt.getFrom().printAST(),
                                 _forStmt.getFrom().getSourcePosition().printSourcePosition()),
                              LOGGING_LEVEL.ERROR)
        elif not (fromType.getValue().equals(PredefinedTypes.getIntegerType()) or
                      fromType.getValue().equals(PredefinedTypes.getRealType())):
            Logger.logMessage('Type of to-expression of for statement "%s" at %s wrong! Expected number, got %s!'
                              % (_forStmt.getFrom().printAST(),
                                 _forStmt.getFrom().getSourcePosition().printSourcePosition(),
                                 fromType.getValue().printSymbol()),
                              LOGGING_LEVEL.ERROR)
        # check that the to stmt is an integer or real
        toType = _forStmt.getTo().getTypeEither()
        if toType.isError():
            Logger.logMessage('Type of to-expression of for statement "%s" at %s could not be derived!'
                              % (_forStmt.getTo().printAST(),
                                 _forStmt.getTo().getSourcePosition().printSourcePosition()),
                              LOGGING_LEVEL.ERROR)
        elif not (toType.getValue().equals(PredefinedTypes.getIntegerType()) or
                      toType.getValue().equals(PredefinedTypes.getRealType())):
            Logger.logMessage('Type of to-expression of for statement "%s" at %s wrong! Expected number, got %s!'
                              % (_forStmt.getTo().printAST(),
                                 _forStmt.getTo().getSourcePosition().printSourcePosition(),
                                 toType.getValue().printSymbol()),
                              LOGGING_LEVEL.ERROR)
        return
