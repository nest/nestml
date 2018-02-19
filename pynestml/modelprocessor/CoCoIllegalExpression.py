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
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages, MessageCode


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

    def visit_declaration(self, _declaration=None):
        """
        Visits a single declaration and asserts that type of lhs is equal to type of rhs.
        :param _declaration: a single declaration.
        :type _declaration: ASTDeclaration
        """
        if _declaration.hasExpression():
            lhs_type = _declaration.getDataType().getTypeSymbol()
            rhs_type_either = _declaration.getExpression().getTypeEither()
            if rhs_type_either.isError():
                self.__drop_missing_type_error(_declaration)
                return
            rhs_type = rhs_type_either.getValue()
            if not lhs_type.equals(rhs_type):
                if rhs_type.differsOnlyInMagnitudeOrIsEqualTo(lhs_type):
                    return
                if rhs_type.isCastableTo(lhs_type):
                    code, message = Messages.getImplicitCastRhsToLhs(_declaration.getExpression(),
                                                                     _declaration.getVariables()[0],
                                                                     rhs_type, lhs_type)
                    Logger.logMessage(_errorPosition=_declaration.getSourcePosition(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(_rhsExpression=_declaration.getExpression(),
                                                                    _lhsExpression=_declaration.getVariables()[0],
                                                                    _rhsType=rhs_type,
                                                                    _lhsType=lhs_type)
                    Logger.logMessage(_errorPosition=_declaration.getSourcePosition(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visit_assignment(self, _assignment=None):
        """
        Visits a single expression and assures that type(lhs) == type(rhs).
        :param _assignment: a single assignment.
        :type _assignment: ASTAssignment
        """
        if _assignment.isDirectAssignment():  # case a = b is simple
            self.handle_simple_assignment(_assignment)
        else:
            self.handle_complex_assignment(_assignment)  # e.g. a *= b
        # todo we have to consider that different magnitudes can still be combined
        return

    def handle_complex_assignment(self, _assignment):
        implicit_rhs_expr = _assignment.deconstructCompoundAssignment()
        lhs_variable_symbol = _assignment.resolveLhsVariableSymbol()
        rhs_type_symbol_either = implicit_rhs_expr.getTypeEither()

        if rhs_type_symbol_either.isError():
            self.__drop_missing_type_error(_assignment)
            return

        rhs_type_symbol = rhs_type_symbol_either.getValue()

        if self.__types_do_not_match(lhs_variable_symbol, rhs_type_symbol):
            self.try_to_recover_or_error(_assignment, implicit_rhs_expr, lhs_variable_symbol, rhs_type_symbol)
        return

    def try_to_recover_or_error(self, _assignment, implicit_rhs_expr, lhs_variable_symbol, rhs_type_symbol):
        if rhs_type_symbol.differsOnlyInMagnitudeOrIsEqualTo(lhs_variable_symbol.getTypeSymbol()):
            # TODO: Implement
            pass
        elif rhs_type_symbol.isCastableTo(lhs_variable_symbol.getTypeSymbol()):
            self.__drop_implicit_cast_warning(_assignment, implicit_rhs_expr, lhs_variable_symbol, rhs_type_symbol)
        else:
            self.__drop_incompatible_types_error(_assignment, implicit_rhs_expr, lhs_variable_symbol, rhs_type_symbol)

    @staticmethod
    def __drop_incompatible_types_error(_assignment, implicit_rhs_expr, lhs_variable_symbol, rhs_type_symbol):
        code, message = Messages.getDifferentTypeRhsLhs(implicit_rhs_expr,
                                                        _assignment.getVariable(),
                                                        rhs_type_symbol,
                                                        lhs_variable_symbol.getTypeSymbol())
        Logger.logMessage(_errorPosition=_assignment.getSourcePosition(),
                          _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)

    @staticmethod
    def __drop_implicit_cast_warning(_assignment, implicit_rhs_expr, lhs_variable_symbol, rhs_type_symbol):
        code, message = Messages.getImplicitCastRhsToLhs(implicit_rhs_expr,
                                                         _assignment.getVariable(),
                                                         rhs_type_symbol,
                                                         lhs_variable_symbol.getTypeSymbol())
        Logger.logMessage(_errorPosition=_assignment.getSourcePosition(),
                          _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)

    @staticmethod
    def __drop_missing_type_error(_assignment):
        code, message = Messages.getTypeCouldNotBeDerived(_assignment.getExpression())
        Logger.logMessage(_code=code, _message=message, _errorPosition=_assignment.getExpression().getSourcePosition(),
                          _logLevel=LOGGING_LEVEL.ERROR)

    @staticmethod
    def __types_do_not_match(lhs_variable_symbol, rhs_type_symbol):
        return not lhs_variable_symbol.getTypeSymbol().equals(rhs_type_symbol)

    def handle_simple_assignment(self, _assignment):
        from pynestml.modelprocessor.ErrorStrings import ErrorStrings
        from pynestml.modelprocessor.Symbol import SymbolKind
        from pynestml.modelprocessor.Either import Either
        lhs_variable_symbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                                     SymbolKind.VARIABLE)
        rhs_type_symbol_either = _assignment.getExpression().getTypeEither()
        if rhs_type_symbol_either.isError():
            self.__drop_missing_type_error(_assignment)
            return
        rhs_type_symbol = rhs_type_symbol_either.getValue()
        if lhs_variable_symbol is not None \
                and self.__types_do_not_match(lhs_variable_symbol, rhs_type_symbol):
            if rhs_type_symbol.differsOnlyInMagnitudeOrIsEqualTo(lhs_variable_symbol.getTypeSymbol()):
                # we convert the rhs unit to the magnitude of the lhs unit.
                _assignment.getExpression().setImplicitConversionFactor(
                    ASTUtils.getConversionFactor(lhs_variable_symbol, _assignment.getExpression()))
                _assignment.getExpression().setTypeEither(Either.value(lhs_variable_symbol.getTypeSymbol()))
                # warn implicit conversion
                error_msg = ErrorStrings.messageImplicitMagnitudeConversion(self, _assignment)
                Logger.logMessage(_code=MessageCode.IMPLICIT_CAST,
                                  _errorPosition=_assignment.getSourcePosition(),
                                  _message=error_msg, _logLevel=LOGGING_LEVEL.WARNING)
            elif rhs_type_symbol.isCastableTo(lhs_variable_symbol.getTypeSymbol()):
                self.__drop_implicit_cast_warning(_assignment, _assignment.getExpr(), lhs_variable_symbol,
                                                  rhs_type_symbol)
            else:
                self.__drop_incompatible_types_error(_assignment, _assignment.getExpression(), lhs_variable_symbol,
                                                     rhs_type_symbol)
        return

    def visit_if_clause(self, _if_clause=None):
        """
        Visits a single if clause and checks that its condition is boolean.
        :param _if_clause: a single elif clause.
        :type _if_clause: ASTIfClause
        """
        cond_type = _if_clause.getCondition().getTypeEither()
        if cond_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_if_clause.getCondition())
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=_if_clause.getCondition().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not cond_type.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(),
                                                                  cond_type.getValue())
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=_if_clause.getCondition().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visit_elif_clause(self, _elif_clause=None):
        """
        Visits a single elif clause and checks that its condition is boolean.
        :param _elif_clause: a single elif clause.
        :type _elif_clause: ASTElifClause
        """
        cond_type = _elif_clause.getCondition().getTypeEither()
        if cond_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_elif_clause.getCondition())
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=_elif_clause.getCondition().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not cond_type.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(),
                                                                  cond_type.getValue())
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=_elif_clause.getCondition().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visit_while_stmt(self, _while_stmt=None):
        """
        Visits a single while stmt and checks that its condition is of boolean type.
        :param _while_stmt: a single while stmt
        :type _while_stmt: ASTWhileStmt
        """
        cond_type = _while_stmt.getCondition().getTypeEither()
        if cond_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_while_stmt.getCondition())
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=_while_stmt.getCondition().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not cond_type.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(),
                                                                  cond_type.getValue())
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=_while_stmt.getCondition().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visit_for_stmt(self, _for_stmt=None):
        """
        Visits a single for stmt and checks that all it parts are correctly defined.
        :param _for_stmt: a single for stmt
        :type _for_stmt: ASTForStmt
        """
        # check that the from stmt is an integer or real
        from_type = _for_stmt.getFrom().getTypeEither()
        if from_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_for_stmt.getFrom())
            Logger.logMessage(_code=code, _message=message, _errorPosition=_for_stmt.getFrom().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not (from_type.getValue().equals(PredefinedTypes.getIntegerType())
                  or from_type.getValue().equals(
                PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(),
                                                                  from_type.getValue())
            Logger.logMessage(_code=code, _message=message, _errorPosition=_for_stmt.getFrom().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        # check that the to stmt is an integer or real
        to_type = _for_stmt.getTo().getTypeEither()
        if to_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(_for_stmt.getTo())
            Logger.logMessage(_code=code, _message=message, _errorPosition=_for_stmt.getTo().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not (to_type.getValue().equals(PredefinedTypes.getIntegerType())
                  or to_type.getValue().equals(PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(), to_type.getValue())
            Logger.logMessage(_code=code, _message=message, _errorPosition=_for_stmt.getTo().getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
