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
            rhsTypeEither = _declaration.getExpression().getTypeEither()
            if rhsTypeEither.isError():
                self.__dropMissingTypeError(_declaration)
                return
            rhsType = rhsTypeEither.getValue()
            if not lhsType.equals(rhsTypeEither.getValue()):
                if rhsType.differsOnlyInMagnitudeOrIsEqualTo(lhsType):
                    return
                if rhsType.isCastableTo(lhsType):
                    code, message = Messages.getImplicitCastRhsToLhs(_declaration.getExpression(),
                                                                     _declaration.getVariables()[0],
                                                                     rhsTypeEither.getValue(), lhsType)
                    Logger.logMessage(_errorPosition=_declaration.getSourcePosition(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(_rhsExpression=_declaration.getExpression(),
                                                                    _lhsExpression=_declaration.getVariables()[0],
                                                                    _rhsType=rhsTypeEither.getValue(),
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
        if _assignment.isDirectAssignment():  # case a = b is simple
            self.handleSimpleAssignment(_assignment)
        else:
            self.handleComplexAssignment(_assignment)  # e.g. a *= b
        # todo we have to consider that different magnitudes can still be combined
        return

    def handleComplexAssignment(self, _assignment):
        implicitRhsExpr = _assignment.deconstructCompoundAssignment()
        lhsVariableSymbol = _assignment.resolveLhsVariableSymbol()
        rhsTypeSymbolEither = implicitRhsExpr.getTypeEither()

        if rhsTypeSymbolEither.isError():
            self.__dropMissingTypeError(_assignment)
            return

        rhsTypeSymbol = rhsTypeSymbolEither.getValue()

        if self.__typesDoNotMatch(lhsVariableSymbol, rhsTypeSymbolEither):
            self.tryToRecoverOrError(_assignment, implicitRhsExpr, lhsVariableSymbol, rhsTypeSymbol,
                                     rhsTypeSymbolEither)
        return

    def tryToRecoverOrError(self, _assignment, implicitRhsExpr, lhsVariableSymbol, rhsTypeSymbol, rhsTypeSymbolEither):
        if rhsTypeSymbol.differsOnlyInMagnitudeOrIsEqualTo(lhsVariableSymbol.getTypeSymbol()):
            # TODO: Implement
            pass
        elif rhsTypeSymbol.isCastableTo(lhsVariableSymbol.getTypeSymbol()):
            self.__dropImplicitCastWarning(_assignment, implicitRhsExpr, lhsVariableSymbol, rhsTypeSymbolEither)
        else:
            self.__dropIncompatibleTypesError(_assignment, implicitRhsExpr, lhsVariableSymbol, rhsTypeSymbolEither)

    @staticmethod
    def __dropIncompatibleTypesError(_assignment, implicitRhsExpr, lhsVariableSymbol, rhsTypeSymbolEither):
        code, message = Messages.getDifferentTypeRhsLhs(implicitRhsExpr,
                                                        _assignment.getVariable(),
                                                        rhsTypeSymbolEither.getValue(),
                                                        lhsVariableSymbol.getTypeSymbol())
        Logger.logMessage(_errorPosition=_assignment.getSourcePosition(),
                          _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)

    @staticmethod
    def __dropImplicitCastWarning(_assignment, implicitRhsExpr, lhsVariableSymbol, rhsTypeSymbolEither):
        code, message = Messages.getImplicitCastRhsToLhs(implicitRhsExpr,
                                                         _assignment.getVariable(),
                                                         rhsTypeSymbolEither.getValue(),
                                                         lhsVariableSymbol.getTypeSymbol())
        Logger.logMessage(_errorPosition=_assignment.getSourcePosition(),
                          _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)

    @staticmethod
    def __dropMissingTypeError(_assignment):
        code, message = Messages.getTypeCouldNotBeDerived(_assignment.getExpression())
        Logger.logMessage(_neuron=None, _code=code, _message=message,
                          _errorPosition=_assignment.getExpression().getSourcePosition(),
                          _logLevel=LOGGING_LEVEL.ERROR)

    @staticmethod
    def __typesDoNotMatch(lhsVariableSymbol, rhsTypeSymbolEither):
        return not lhsVariableSymbol.getTypeSymbol().equals(rhsTypeSymbolEither.getValue())

    def handleSimpleAssignment(self, _assignment):
        from pynestml.nestml.ErrorStrings import ErrorStrings
        from pynestml.nestml.Symbol import SymbolKind
        from pynestml.nestml.Either import Either
        lhsVariableSymbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                                   SymbolKind.VARIABLE)
        rhsTypeSymbolEither = _assignment.getExpression().getTypeEither()
        if rhsTypeSymbolEither.isError():
            self.__dropMissingTypeError(_assignment)
            return
        rhsTypeSymbol = rhsTypeSymbolEither.getValue()
        if lhsVariableSymbol is not None \
                and self.__typesDoNotMatch(lhsVariableSymbol, rhsTypeSymbolEither):
            if rhsTypeSymbol.differsOnlyInMagnitudeOrIsEqualTo(lhsVariableSymbol.getTypeSymbol()):
                # we convert the rhs unit to the magnitude of the lhs unit.
                _assignment.getExpression().setImplicitConversionFactor(
                    ASTUtils.getConversionFactor(lhsVariableSymbol, _assignment.getExpression()))
                _assignment.getExpression().setTypeEither(Either.value(lhsVariableSymbol.getTypeSymbol()))
                # warn implicit conversion
                errorMsg = ErrorStrings.messageImplicitMagnitudeConversion(self, _assignment)
                Logger.logMessage(_code=MessageCode.IMPLICIT_CAST,
                                  _errorPosition=_assignment.getSourcePosition(),
                                  _message=errorMsg, _logLevel=LOGGING_LEVEL.WARNING)
            elif rhsTypeSymbol.isCastableTo(lhsVariableSymbol.getTypeSymbol()):
                self.__dropImplicitCastWarning(_assignment, _assignment.getExpr(), lhsVariableSymbol,
                                               rhsTypeSymbolEither)
            else:
                self.__dropIncompatibleTypesError(_assignment, _assignment.getExpression(), lhsVariableSymbol,
                                                  rhsTypeSymbolEither)
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
