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
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Messages import Messages
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes


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


class CorrectExpressionVisitor(ASTVisitor):
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
            rhsType = _declaration.getExpression().getTypeEither()
            if rhsType.isError():
                code, message = Messages.getTypeCouldNotBeDerived(_declaration.getExpression())
                Logger.logMessage(_neuron=None, _code=code, _message=message,
                                  _errorPosition=_declaration.getExpression().get_source_position(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
            elif not lhsType.equals(rhsType.getValue()):
                if ASTUtils.differsInMagnitude(rhsType.getValue(),lhsType):
                    return
                if ASTUtils.isCastableTo(rhsType.getValue(), lhsType):
                    code, message = Messages.getImplicitCastRhsToLhs(_declaration.getExpression(),
                                                                     _declaration.getVariables()[0],
                                                                     rhsType.getValue(), lhsType)
                    Logger.logMessage(_errorPosition=_declaration.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(_rhsExpression=_declaration.getExpression(),
                                                                    _lhsExpression=_declaration.getVariables()[0],
                                                                    _rhsType=rhsType.getValue(),
                                                                    _lhsType=lhsType)
                    Logger.logMessage(_errorPosition=_declaration.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visitAssignment(self, _assignment=None):
        """
        Visits a single expression and assures that type(lhs) == type(rhs).
        :param _assignment: a single assignment.
        :type _assignment: ASTAssignment
        """
        from pynestml.modelprocessor.Symbol import SymbolKind
        from pynestml.utils.ASTUtils import ASTUtils
        if _assignment.isDirectAssignment():  # case a = b is simple
            lhsSymbolType = _assignment.get_scope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                                    SymbolKind.VARIABLE)
            rhsSymbolType = _assignment.getExpression().getTypeEither()
            if rhsSymbolType.isError():
                code, message = Messages.getTypeCouldNotBeDerived(_assignment.getExpression())
                Logger.logMessage(_neuron=None, _code=code, _message=message,
                                  _errorPosition=_assignment.getExpression().get_source_position(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
            elif lhsSymbolType is not None and not lhsSymbolType.getTypeSymbol().equals(rhsSymbolType.getValue()):
                if ASTUtils.differsInMagnitude(rhsSymbolType.getValue(),lhsSymbolType.getTypeSymbol()):
                    return
                elif ASTUtils.isCastableTo(rhsSymbolType.getValue(), lhsSymbolType.getTypeSymbol()):
                    code, message = Messages.getImplicitCastRhsToLhs(_assignment.getExpr(),
                                                                     _assignment.getVariable(),
                                                                     rhsSymbolType.getValue(),
                                                                     lhsSymbolType.getTypeSymbol())
                    Logger.logMessage(_errorPosition=_assignment.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(_assignment.getExpression(),
                                                                    _assignment.getVariable(),
                                                                    rhsSymbolType.getValue(),
                                                                    lhsSymbolType.getTypeSymbol())
                    Logger.logMessage(_errorPosition=_assignment.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        else:
            expr = ASTUtils.deconstructAssignment(_lhs=_assignment.getVariable(),
                                                  _isPlus=_assignment.isCompoundSum(),
                                                  _isMinus=_assignment.isCompoundMinus(),
                                                  _isTimes=_assignment.isCompoundProduct(),
                                                  _isDivide=_assignment.isCompoundQuotient(),
                                                  _rhs=_assignment.getExpression())
            lhsSymbolType = _assignment.get_scope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                                    SymbolKind.VARIABLE)
            rhsSymbolType = expr.getTypeEither()
            if rhsSymbolType.isError():
                code, message = Messages.getTypeCouldNotBeDerived(_assignment.getExpression())
                Logger.logMessage(_neuron=None, _code=code, _message=message,
                                  _errorPosition=_assignment.getExpression().get_source_position(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
            elif lhsSymbolType is not None and not lhsSymbolType.getTypeSymbol().equals(rhsSymbolType.getValue()):
                if ASTUtils.differsInMagnitude(rhsSymbolType.getValue(), lhsSymbolType.getTypeSymbol()):
                    return
                elif ASTUtils.isCastableTo(rhsSymbolType.getValue(), lhsSymbolType.getTypeSymbol()):
                    code, message = Messages.getImplicitCastRhsToLhs(expr,
                                                                     _assignment.getVariable(),
                                                                     rhsSymbolType.getValue(),
                                                                     lhsSymbolType.getTypeSymbol())
                    Logger.logMessage(_errorPosition=_assignment.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(expr,
                                                                    _assignment.getVariable(),
                                                                    rhsSymbolType.getValue(),
                                                                    lhsSymbolType.getTypeSymbol())
                    Logger.logMessage(_errorPosition=_assignment.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        # todo we have to consider that different magnitudes can still be combined
        return

    def visitIfClause(self, _ifClause=None):
        """
        Visits a single if clause and checks that its condition is boolean.
        :param _ifClause: a single elif clause.
        :type _ifClause: ASTIfClause
        """
        condType = _ifClause.getCondition().getTypeEither()
        if condType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_ifClause.getCondition())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_ifClause.getCondition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(), condType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_ifClause.getCondition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visitElifClause(self, _elifClause=None):
        """
        Visits a single elif clause and checks that its condition is boolean.
        :param _elifClause: a single elif clause.
        :type _elifClause: ASTElifClause
        """
        condType = _elifClause.getCondition().getTypeEither()
        if condType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_elifClause.getCondition())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_elifClause.getCondition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(), condType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_elifClause.getCondition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visitWhileStmt(self, _whileStmt=None):
        """
        Visits a single while stmt and checks that its condition is of boolean type.
        :param _whileStmt: a single while stmt
        :type _whileStmt: ASTWhileStmt
        """
        condType = _whileStmt.getCondition().getTypeEither()
        if condType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_whileStmt.getCondition())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_whileStmt.getCondition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(), condType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_whileStmt.getCondition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
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
            code, message = Messages.getTypeCouldNotBeDerived(_forStmt.getFrom())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_forStmt.getFrom().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not (fromType.getValue().equals(PredefinedTypes.getIntegerType()) or
                      fromType.getValue().equals(PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(), fromType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_forStmt.getFrom().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        # check that the to stmt is an integer or real
        toType = _forStmt.getTo().getTypeEither()
        if toType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_forStmt.getTo())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_forStmt.getTo().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not (toType.getValue().equals(PredefinedTypes.getIntegerType()) or
                      toType.getValue().equals(PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(), toType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_forStmt.getTo().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
