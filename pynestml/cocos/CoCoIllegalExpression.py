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

from pynestml.meta_model.ASTDeclaration import ASTDeclaration
from pynestml.cocos.CoCo import CoCo
from pynestml.symbols.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.symbols.PredefinedTypes import PredefinedTypes
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.LoggingHelper import LoggingHelper
from pynestml.utils.Messages import Messages
from pynestml.utils.TypeCaster import TypeCaster
from pynestml.visitors.ASTVisitor import ASTVisitor


class CoCoIllegalExpression(CoCo):
    """
    This coco checks that all expressions are correctly typed.
    """

    @classmethod
    def check_co_co(cls, neuron):
        """
        Ensures the coco for the handed over neuron.
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """
        neuron.accept(CorrectExpressionVisitor())


class CorrectExpressionVisitor(ASTVisitor):
    """
    This visitor checks that all expression correspond to the expected type.
    """

    def visit_declaration(self, node):
        """
        Visits a single declaration and asserts that type of lhs is equal to type of rhs.
        :param node: a single declaration.
        :type node: ASTDeclaration
        """
        assert isinstance(node, ASTDeclaration)
        if node.has_expression():
            lhs_type = node.get_data_type().get_type_symbol()
            rhs_type = node.get_expression().type
            if isinstance(rhs_type, ErrorTypeSymbol):
                LoggingHelper.drop_missing_type_error(node)
                return
            if self.__types_do_not_match(lhs_type, rhs_type):
                TypeCaster.try_to_recover_or_error(lhs_type, rhs_type, node.get_expression())
        return

    def visit_assignment(self, node):
        """
        Visits a single expression and assures that type(lhs) == type(rhs).
        :param node: a single assignment.
        :type node: ASTAssignment
        """
        from pynestml.meta_model.ASTAssignment import ASTAssignment
        assert isinstance(node, ASTAssignment)
        if node.is_direct_assignment:  # case a = b is simple
            self.handle_simple_assignment(node)
        else:
            self.handle_complex_assignment(node)  # e.g. a *= b
        return

    def handle_complex_assignment(self, node):
        rhs_expr = node.get_expression()
        lhs_variable_symbol = node.resolveLhsVariableSymbol()
        rhs_type_symbol = rhs_expr.type

        if isinstance(rhs_type_symbol, ErrorTypeSymbol):
            LoggingHelper.drop_missing_type_error(node)
            return

        if self.__types_do_not_match(lhs_variable_symbol.get_type_symbol(), rhs_type_symbol):
            TypeCaster.try_to_recover_or_error(lhs_variable_symbol.get_type_symbol(), rhs_type_symbol,
                                               node.get_expression())
        return

    @staticmethod
    def __types_do_not_match(lhs_type_symbol, rhs_type_symbol):
        return not lhs_type_symbol.equals(rhs_type_symbol)

    def handle_simple_assignment(self, node):
        from pynestml.symbols.Symbol import SymbolKind
        lhs_variable_symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(),
                                                                 SymbolKind.VARIABLE)

        rhs_type_symbol = node.get_expression().type
        if isinstance(rhs_type_symbol, ErrorTypeSymbol):
            LoggingHelper.drop_missing_type_error(node)
            return

        if lhs_variable_symbol is not None and self.__types_do_not_match(lhs_variable_symbol.get_type_symbol(),
                                                                         rhs_type_symbol):
            TypeCaster.try_to_recover_or_error(lhs_variable_symbol.get_type_symbol(), rhs_type_symbol,
                                               node.get_expression())
        return

    def visit_if_clause(self, node):
        """
        Visits a single if clause and checks that its condition is boolean.
        :param node: a single elif clause.
        :type node: ASTIfClause
        """
        cond_type = node.get_condition().type
        if isinstance(cond_type, ErrorTypeSymbol):
            code, message = Messages.get_type_could_not_be_derived(node.get_condition())
            Logger.log_message(code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not cond_type.equals(PredefinedTypes.get_boolean_type()):
            code, message = Messages.get_type_different_from_expected(PredefinedTypes.get_boolean_type(),
                                                                      cond_type)
            Logger.log_message(code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        return

    def visit_elif_clause(self, node):
        """
        Visits a single elif clause and checks that its condition is boolean.
        :param node: a single elif clause.
        :type node: ASTElifClause
        """
        cond_type = node.get_condition().type
        if isinstance(cond_type, ErrorTypeSymbol):
            code, message = Messages.get_type_could_not_be_derived(node.get_condition())
            Logger.log_message(code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not cond_type.equals(PredefinedTypes.get_boolean_type()):
            code, message = Messages.get_type_different_from_expected(PredefinedTypes.get_boolean_type(),
                                                                      cond_type)
            Logger.log_message(code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        return

    def visit_while_stmt(self, node):
        """
        Visits a single while stmt and checks that its condition is of boolean type.
        :param node: a single while stmt
        :type node: ASTWhileStmt
        """
        cond_type = node.get_condition().type
        if isinstance(cond_type, ErrorTypeSymbol):
            code, message = Messages.get_type_could_not_be_derived(node.get_condition())
            Logger.log_message(code=code, message=message,
                               error_position=node.get_condition().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not cond_type.equals(PredefinedTypes.get_boolean_type()):
            code, message = Messages.get_type_different_from_expected(PredefinedTypes.get_boolean_type(),
                                                                      cond_type)
            Logger.log_message(code=code, message=message,
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
        from_type = node.get_start_from().type
        if isinstance(from_type, ErrorTypeSymbol):
            code, message = Messages.get_type_could_not_be_derived(node.get_start_from())
            Logger.log_message(code=code, message=message, error_position=node.get_start_from().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not (from_type.equals(PredefinedTypes.get_integer_type())
                  or from_type.equals(
                    PredefinedTypes.get_real_type())):
            code, message = Messages.get_type_different_from_expected(PredefinedTypes.get_integer_type(),
                                                                      from_type)
            Logger.log_message(code=code, message=message, error_position=node.get_start_from().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        # check that the to stmt is an integer or real
        to_type = node.get_end_at().type
        if isinstance(to_type, ErrorTypeSymbol):
            code, message = Messages.get_type_could_not_be_derived(node.get_end_at())
            Logger.log_message(code=code, message=message, error_position=node.get_end_at().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        elif not (to_type.equals(PredefinedTypes.get_integer_type())
                  or to_type.equals(PredefinedTypes.get_real_type())):
            code, message = Messages.get_type_different_from_expected(PredefinedTypes.get_integer_type(), to_type)
            Logger.log_message(code=code, message=message, error_position=node.get_end_at().get_source_position(),
                               log_level=LoggingLevel.ERROR)
        return
