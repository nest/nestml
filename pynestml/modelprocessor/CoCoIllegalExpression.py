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
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes

from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages


class CoCoIllegalExpression(CoCo):
    """
    This coco checks that all expressions are correctly typed.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(node)
        node.accept(CorrectExpressionVisitor())
        return


class CorrectExpressionVisitor(ASTVisitor):
    """
    This visitor checks that all rhs correspond to the expected type.
    """

    def visit_declaration(self, node):
        """
        Visits a single declaration and asserts that type of lhs is equal to type of rhs.
        :param node: a single declaration.
        :type node: ASTDeclaration
        """
        if node.has_expression():
            lhs_type = node.get_data_type().get_type_symbol()
            rhs_type = node.get_expression().get_type_either()
            if rhs_type.isError():
                code, message = Messages.getTypeCouldNotBeDerived(node.get_expression())
                Logger.log_message(neuron=None, code=code, message=message,
                                   error_position=node.get_expression().get_source_position(),
                                   log_level=LoggingLevel.ERROR)
            elif not lhs_type.equals(rhs_type.getValue()):
                if ASTUtils.differs_in_magnitude(rhs_type.getValue(), lhs_type):
                    return
                if ASTUtils.is_castable_to(rhs_type.getValue(), lhs_type):
                    code, message = Messages.getImplicitCastRhsToLhs(node.get_expression(),
                                                                     node.get_variables()[0],
                                                                     rhs_type.getValue(), lhs_type)
                    Logger.log_message(error_position=node.get_source_position(),
                                       code=code, message=message, log_level=LoggingLevel.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(_rhsExpression=node.get_expression(),
                                                                    _lhsExpression=node.get_variables()[0],
                                                                    _rhsType=rhs_type.getValue(),
                                                                    _lhsType=lhs_type)
                    Logger.log_message(error_position=node.get_source_position(),
                                       code=code, message=message, log_level=LoggingLevel.ERROR)
        return

    def visit_assignment(self, node):
        """
        Visits a single rhs and assures that type(lhs) == type(rhs).
        :param node: a single node.
        :type node: ASTAssignment
        """
        from pynestml.modelprocessor.Symbol import SymbolKind
        from pynestml.utils.ASTUtils import ASTUtils
        if node.is_direct_assignment:  # case a = b is simple
            lhs_symbol_type = node.get_scope().resolveToSymbol(node.get_variable().get_complete_name(),
                                                               SymbolKind.VARIABLE)
            rhs_symbol_type = node.get_expression().get_type_either()
            if rhs_symbol_type.isError():
                code, message = Messages.getTypeCouldNotBeDerived(node.get_expression())
                Logger.log_message(neuron=None, code=code, message=message,
                                   error_position=node.get_expression().get_source_position(),
                                   log_level=LoggingLevel.ERROR)
            elif lhs_symbol_type is not None and not lhs_symbol_type.get_type_symbol().equals(
                    rhs_symbol_type.getValue()):
                if ASTUtils.differs_in_magnitude(rhs_symbol_type.getValue(), lhs_symbol_type.get_type_symbol()):
                    return
                elif ASTUtils.is_castable_to(rhs_symbol_type.getValue(), lhs_symbol_type.get_type_symbol()):
                    code, message = Messages.getImplicitCastRhsToLhs(node.getExpr(),
                                                                     node.get_variable(),
                                                                     rhs_symbol_type.getValue(),
                                                                     lhs_symbol_type.get_type_symbol())
                    Logger.log_message(error_position=node.get_source_position(),
                                       code=code, message=message, log_level=LoggingLevel.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(node.get_expression(),
                                                                    node.get_variable(),
                                                                    rhs_symbol_type.getValue(),
                                                                    lhs_symbol_type.get_type_symbol())
                    Logger.log_message(error_position=node.get_source_position(),
                                       code=code, message=message, log_level=LoggingLevel.ERROR)
        else:
            expr = ASTUtils.deconstructAssignment(lhs=node.get_variable(),
                                                  is_plus=node.is_compound_sum,
                                                  is_minus=node.is_compound_minus,
                                                  is_times=node.is_compound_product,
                                                  is_divide=node.is_compound_quotient,
                                                  _rhs=node.get_expression())
            lhs_symbol_type = node.get_scope().resolveToSymbol(node.get_variable().get_complete_name(),
                                                               SymbolKind.VARIABLE)
            rhs_symbol_type = expr.get_type_either()
            if rhs_symbol_type.isError():
                code, message = Messages.getTypeCouldNotBeDerived(node.get_expression())
                Logger.log_message(neuron=None, code=code, message=message,
                                   error_position=node.get_expression().get_source_position(),
                                   log_level=LoggingLevel.ERROR)
            elif lhs_symbol_type is not None and not lhs_symbol_type.get_type_symbol().equals(
                    rhs_symbol_type.getValue()):
                if ASTUtils.differs_in_magnitude(rhs_symbol_type.getValue(), lhs_symbol_type.get_type_symbol()):
                    return
                elif ASTUtils.is_castable_to(rhs_symbol_type.getValue(), lhs_symbol_type.get_type_symbol()):
                    code, message = Messages.getImplicitCastRhsToLhs(expr,
                                                                     node.get_variable(),
                                                                     rhs_symbol_type.getValue(),
                                                                     lhs_symbol_type.get_type_symbol())
                    Logger.log_message(error_position=node.get_source_position(),
                                       code=code, message=message, log_level=LoggingLevel.WARNING)
                else:
                    code, message = Messages.getDifferentTypeRhsLhs(expr,
                                                                    node.get_variable(),
                                                                    rhs_symbol_type.getValue(),
                                                                    lhs_symbol_type.get_type_symbol())
                    Logger.log_message(error_position=node.get_source_position(),
                                       code=code, message=message, log_level=LoggingLevel.ERROR)
        # todo we have to consider that different magnitudes can still be combined
        return

    def visit_if_clause(self, node):
        """
        Visits a single if clause and checks that its condition is boolean.
        :param node: a single elif clause.
        :type node: ASTIfClause
        """
        cond_type = node.get_condition().get_type_either()
        if cond_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_condition())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not cond_type.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(),
                                                                  cond_type.getValue())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        return

    def visit_elif_clause(self, node):
        """
        Visits a single elif clause and checks that its condition is boolean.
        :param node: a single elif clause.
        :type node: ASTElifClause
        """
        cond_type = node.get_condition().get_type_either()
        if cond_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_condition())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not cond_type.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(),
                                                                  cond_type.getValue())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        return

    def visit_while_stmt(self, node):
        """
        Visits a single while stmt and checks that its condition is of boolean type.
        :param node: a single while stmt
        :type node: ASTWhileStmt
        """
        cond_type = node.get_condition().get_type_either()
        if cond_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_condition())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not cond_type.getValue().equals(PredefinedTypes.getBooleanType()):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getBooleanType(),
                                                                  cond_type.getValue())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        return

    def visit_for_stmt(self, node):
        """
        Visits a single for stmt and checks that all it parts are correctly defined.
        :param node: a single for stmt
        :type node: ASTForStmt
        """
        # check that the from stmt is an integer or real
        from_type = node.get_start_from().get_type_either()
        if from_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_start_from())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_start_from().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not (from_type.getValue().equals(PredefinedTypes.getIntegerType()) or
                  from_type.getValue().equals(PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(),
                                                                  from_type.getValue())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_start_from().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        # check that the to stmt is an integer or real
        to_type = node.get_end_at().get_type_either()
        if to_type.isError():
            code, message = Messages.getTypeCouldNotBeDerived(node.get_end_at())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_end_at().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not (to_type.getValue().equals(PredefinedTypes.getIntegerType()) or
                  to_type.getValue().equals(PredefinedTypes.getRealType())):
            code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getIntegerType(), to_type.getValue())
            Logger.log_message(neuron=None, code=code, message=message,
                               error_position=node.get_end_at().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        return
