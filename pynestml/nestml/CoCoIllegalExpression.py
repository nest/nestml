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
from pynestml.utils.Messages import Messages, MessageCode
from pynestml.nestml.CoCo import CoCo
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.PredefinedTypes import PredefinedTypes


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
            rhsType = _declaration.getExpression().getTypeEither()
            if rhsType.isError():
                code, message = Messages.getTypeCouldNotBeDerived(_declaration.getExpression())
                Logger.logMessage(_neuron=None, _code=code, _message=message,
                                  _errorPosition=_declaration.getExpression().getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
            elif not lhsType.equals(rhsType.getValue()):
                if ASTUtils.differsInMagnitude(rhsType.getValue(),lhsType):
                    return
                if ASTUtils.isCastableTo(rhsType.getValue(), lhsType):
                    code, message = Messages.getImplicitCastRhsToLhs(_declaration.getExpression(),
                                                                     _declaration.getVariables()[0],
                                                                     rhsType.getValue(), lhsType)
                    Logger.logMessage(_errorPosition=_declaration.getSourcePosition(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(_rhsExpression=_declaration.getExpression(),
                                                                    _lhsExpression=_declaration.getVariables()[0],
                                                                    _rhsType=rhsType.getValue(),
                                                                    _lhsType=lhsType)
                    Logger.logMessage(_errorPosition=_declaration.getSourcePosition(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visitAssignment(self, _assignment=None):
        """
        Visits a single expression and assures that type(lhs) == type(rhs).
        :param _assignment: a single assignment.
        :type _assignment: ASTAssignment
        """
        from pynestml.nestml.Symbol import SymbolKind
        from pynestml.utils.ASTUtils import ASTUtils
        from pynestml.nestml.Either import Either
        from pynestml.nestml.ErrorStrings import ErrorStrings
        if _assignment.isDirectAssignment():  # case a = b is simple
            lhsVariableSymbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                                   SymbolKind.VARIABLE)
            rhsTypeSymbolEither = _assignment.getExpression().getTypeEither()
            if rhsTypeSymbolEither.isError():
                code, message = Messages.getTypeCouldNotBeDerived(_assignment.getExpression())
                Logger.logMessage(_neuron=None, _code=code, _message=message,
                                  _errorPosition=_assignment.getExpression().getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
            elif lhsVariableSymbol is not None and not lhsVariableSymbol.getTypeSymbol().equals(rhsTypeSymbolEither.getValue()):
                if ASTUtils.differsInMagnitude(rhsTypeSymbolEither.getValue(),lhsVariableSymbol.getTypeSymbol()):
                    # we convert the rhs unit to the magnitude of the lhs unit.

                    _assignment.getExpression().setImplicitVersion(ASTUtils.getConversionExpression(lhsVariableSymbol, _assignment.getExpression()))
                    _assignment.getExpression().setTypeEither(Either.value(lhsVariableSymbol.getTypeSymbol()))
                    # warn implicit conversion
                    errorMsg = ErrorStrings.messageImplicitMagnitudeConversion(self, _assignment)
                    Logger.logMessage(_code=MessageCode.IMPLICIT_CAST,
                                      _errorPosition=_assignment.getSourcePosition(),
                                      _message=errorMsg, _logLevel=LOGGING_LEVEL.WARNING)
                    return
                elif ASTUtils.isCastableTo(rhsTypeSymbolEither.getValue(), lhsVariableSymbol.getTypeSymbol()):
                    code, message = Messages.getImplicitCastRhsToLhs(_assignment.getExpr(),
                                                                     _assignment.getVariable(),
                                                                     rhsTypeSymbolEither.getValue(),
                                                                     lhsVariableSymbol.getTypeSymbol())
                    Logger.logMessage(_errorPosition=_assignment.getSourcePosition(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(_assignment.getExpression(),
                                                                    _assignment.getVariable(),
                                                                    rhsTypeSymbolEither.getValue(),
                                                                    lhsVariableSymbol.getTypeSymbol())
                    Logger.logMessage(_errorPosition=_assignment.getSourcePosition(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        else:
            expr = ASTUtils.deconstructAssignment(_lhs=_assignment.getVariable(),
                                                  _isPlus=_assignment.isCompoundSum(),
                                                  _isMinus=_assignment.isCompoundMinus(),
                                                  _isTimes=_assignment.isCompoundProduct(),
                                                  _isDivide=_assignment.isCompoundQuotient(),
                                                  _rhs=_assignment.getExpression())
            lhsVariableSymbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                                   SymbolKind.VARIABLE)
            rhsTypeSymbolEither = expr.getTypeEither()
            if rhsTypeSymbolEither.isError():
                code, message = Messages.getTypeCouldNotBeDerived(_assignment.getExpression())
                Logger.logMessage(_neuron=None, _code=code, _message=message,
                                  _errorPosition=_assignment.getExpression().getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
            elif lhsVariableSymbol is not None and not lhsVariableSymbol.getTypeSymbol().equals(rhsTypeSymbolEither.getValue()):
                if ASTUtils.differsInMagnitude(rhsTypeSymbolEither.getValue(), lhsVariableSymbol.getTypeSymbol()):
                    return
                elif ASTUtils.isCastableTo(rhsTypeSymbolEither.getValue(), lhsVariableSymbol.getTypeSymbol()):
                    code, message = Messages.getImplicitCastRhsToLhs(expr,
                                                                     _assignment.getVariable(),
                                                                     rhsTypeSymbolEither.getValue(),
                                                                     lhsVariableSymbol.getTypeSymbol())
                    Logger.logMessage(_errorPosition=_assignment.getSourcePosition(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(expr,
                                                                    _assignment.getVariable(),
                                                                    rhsTypeSymbolEither.getValue(),
                                                                    lhsVariableSymbol.getTypeSymbol())
                    Logger.logMessage(_errorPosition=_assignment.getSourcePosition(),
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
                              _errorPosition=_ifClause.getCondition().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(), condType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_ifClause.getCondition().getSourcePosition(),
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
                              _errorPosition=_elifClause.getCondition().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(), condType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_elifClause.getCondition().getSourcePosition(),
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
                              _errorPosition=_whileStmt.getCondition().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(), condType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_whileStmt.getCondition().getSourcePosition(),
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
                              _errorPosition=_forStmt.getFrom().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not (fromType.getValue().equals(PredefinedTypes.getIntegerType()) or
                      fromType.getValue().equals(PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(), fromType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_forStmt.getFrom().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        # check that the to stmt is an integer or real
        toType = _forStmt.getTo().getTypeEither()
        if toType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_forStmt.getTo())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_forStmt.getTo().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not (toType.getValue().equals(PredefinedTypes.getIntegerType()) or
                      toType.getValue().equals(PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(), toType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=_forStmt.getTo().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
