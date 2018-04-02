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
    This visitor checks that all rhs correspond to the expected type.
    """

    def visit_declaration(self, node=None):
        """
        Visits a single declaration and asserts that type of lhs is equal to type of rhs.
        :param node: a single declaration.
        :type node: ASTDeclaration
        """
        if node.has_expression():
            lhsType = node.get_data_type().get_type_symbol()
            rhsType = node.get_expression().get_type_either()
            if rhsType.isError():
                code, message = Messages.getTypeCouldNotBeDerived(node.get_expression())
                Logger.logMessage(_neuron=None, _code=code, _message=message,
                                  _errorPosition=node.get_expression().get_source_position(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
            elif not lhsType.equals(rhsType.getValue()):
                if ASTUtils.differs_in_magnitude(rhsType.getValue(), lhsType):
                    return
                if ASTUtils.is_castable_to(rhsType.getValue(), lhsType):
                    code, message = Messages.getImplicitCastRhsToLhs(node.get_expression(),
                                                                     node.get_variables()[0],
                                                                     rhsType.getValue(), lhsType)
                    Logger.logMessage(_errorPosition=node.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(_rhsExpression=node.get_expression(),
                                                                    _lhsExpression=node.get_variables()[0],
                                                                    _rhsType=rhsType.getValue(),
                                                                    _lhsType=lhsType)
                    Logger.logMessage(_errorPosition=node.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visit_assignment(self, node=None):
        """
        Visits a single rhs and assures that type(lhs) == type(rhs).
        :param node: a single node.
        :type assignment: ASTAssignment
        """
        from pynestml.modelprocessor.Symbol import SymbolKind
        from pynestml.utils.ASTUtils import ASTUtils
        if node.is_direct_assignment:  # case a = b is simple
            lhsSymbolType = node.get_scope().resolveToSymbol(node.get_variable().get_complete_name(),
                                                             SymbolKind.VARIABLE)
            rhsSymbolType = node.get_expression().get_type_either()
            if rhsSymbolType.isError():
                code, message = Messages.getTypeCouldNotBeDerived(node.get_expression())
                Logger.logMessage(_neuron=None, _code=code, _message=message,
                                  _errorPosition=node.get_expression().get_source_position(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
            elif lhsSymbolType is not None and not lhsSymbolType.get_type_symbol().equals(rhsSymbolType.getValue()):
                if ASTUtils.differs_in_magnitude(rhsSymbolType.getValue(), lhsSymbolType.get_type_symbol()):
                    return
                elif ASTUtils.is_castable_to(rhsSymbolType.getValue(), lhsSymbolType.get_type_symbol()):
                    code, message = Messages.getImplicitCastRhsToLhs(node.getExpr(),
                                                                     node.get_variable(),
                                                                     rhsSymbolType.getValue(),
                                                                     lhsSymbolType.get_type_symbol())
                    Logger.logMessage(_errorPosition=node.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(node.get_expression(),
                                                                    node.get_variable(),
                                                                    rhsSymbolType.getValue(),
                                                                    lhsSymbolType.get_type_symbol())
                    Logger.logMessage(_errorPosition=node.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        else:
            expr = ASTUtils.deconstructAssignment(lhs=node.get_variable(),
                                                  is_plus=node.is_compound_sum,
                                                  is_minus=node.is_compound_minus,
                                                  is_times=node.is_compound_product,
                                                  is_divide=node.is_compound_quotient,
                                                  _rhs=node.get_expression())
            lhsSymbolType = node.get_scope().resolveToSymbol(node.get_variable().get_complete_name(),
                                                             SymbolKind.VARIABLE)
            rhsSymbolType = expr.get_type_either()
            if rhsSymbolType.isError():
                code, message = Messages.getTypeCouldNotBeDerived(node.get_expression())
                Logger.logMessage(_neuron=None, _code=code, _message=message,
                                  _errorPosition=node.get_expression().get_source_position(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
            elif lhsSymbolType is not None and not lhsSymbolType.get_type_symbol().equals(rhsSymbolType.getValue()):
                if ASTUtils.differs_in_magnitude(rhsSymbolType.getValue(), lhsSymbolType.get_type_symbol()):
                    return
                elif ASTUtils.is_castable_to(rhsSymbolType.getValue(), lhsSymbolType.get_type_symbol()):
                    code, message = Messages.getImplicitCastRhsToLhs(expr,
                                                                     node.get_variable(),
                                                                     rhsSymbolType.getValue(),
                                                                     lhsSymbolType.get_type_symbol())
                    Logger.logMessage(_errorPosition=node.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(expr,
                                                                    node.get_variable(),
                                                                    rhsSymbolType.getValue(),
                                                                    lhsSymbolType.get_type_symbol())
                    Logger.logMessage(_errorPosition=node.get_source_position(),
                                      _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        # todo we have to consider that different magnitudes can still be combined
        return

    def visit_if_clause(self, node=None):
        """
        Visits a single if clause and checks that its condition is boolean.
        :param node: a single elif clause.
        :type node: ASTIfClause
        """
        condType = node.get_condition().get_type_either()
        if condType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_condition())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_condition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(), condType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_condition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visit_elif_clause(self, node=None):
        """
        Visits a single elif clause and checks that its condition is boolean.
        :param node: a single elif clause.
        :type node: ASTElifClause
        """
        condType = node.get_condition().get_type_either()
        if condType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_condition())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_condition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(), condType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_condition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visit_while_stmt(self, node=None):
        """
        Visits a single while stmt and checks that its condition is of boolean type.
        :param node: a single while stmt
        :type node: ASTWhileStmt
        """
        condType = node.get_condition().get_type_either()
        if condType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_condition())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_condition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not condType.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(), condType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_condition().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return

    def visit_for_stmt(self, node=None):
        """
        Visits a single for stmt and checks that all it parts are correctly defined.
        :param node: a single for stmt
        :type node: ASTForStmt
        """
        # check that the from stmt is an integer or real
        fromType = node.get_start_from().get_type_either()
        if fromType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_start_from())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_start_from().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not (fromType.getValue().equals(PredefinedTypes.getIntegerType()) or
                      fromType.getValue().equals(PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(), fromType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_start_from().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        # check that the to stmt is an integer or real
        toType = node.get_end_at().get_type_either()
        if toType.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_end_at())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_end_at().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        elif not (toType.getValue().equals(PredefinedTypes.getIntegerType()) or
                      toType.getValue().equals(PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(), toType.getValue())
            Logger.logMessage(_neuron=None, _code=code, _message=message,
                              _errorPosition=node.get_end_at().get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
