# -*- coding: utf-8 -*-
#
# assign_implicit_conversion_factors_visitor.py
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

from typing import Sequence, Union

from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.template_type_symbol import TemplateTypeSymbol
from pynestml.symbols.variadic_type_symbol import VariadicTypeSymbol
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.logging_helper import LoggingHelper
from pynestml.utils.messages import Messages
from pynestml.utils.type_caster import TypeCaster
from pynestml.visitors.ast_visitor import ASTVisitor


class AssignImplicitConversionFactorsVisitor(ASTVisitor):
    r"""
    Assign implicit conversion factors in expressions.
    """

    def visit_model(self, model: ASTModel):
        self.__assign_return_types(model)

    def visit_declaration(self, node):
        """
        Visits a single declaration and asserts that type of lhs is equal to type of rhs.
        :param node: a single declaration.
        :type node: ASTDeclaration
        """
        assert isinstance(node, ASTDeclaration)
        if node.has_expression():
            if node.get_expression().get_source_position().equals(ASTSourceLocation.get_added_source_position()):
                # no type checks are executed for added nodes, since we assume correctness
                return
            lhs_type = node.get_data_type().get_type_symbol()
            rhs_type = node.get_expression().type
            if isinstance(rhs_type, ErrorTypeSymbol):
                LoggingHelper.drop_missing_type_error(node)
                return
            if self.__types_do_not_match(lhs_type, rhs_type):
                TypeCaster.try_to_recover_or_error(lhs_type, rhs_type, node.get_expression(),
                                                   set_implicit_conversion_factor_on_lhs=True)

    def visit_inline_expression(self, node):
        """
        Visits a single inline expression and asserts that type of lhs is equal to type of rhs.
        """
        assert isinstance(node, ASTInlineExpression)
        lhs_type = node.get_data_type().get_type_symbol()
        rhs_type = node.get_expression().type
        if isinstance(rhs_type, ErrorTypeSymbol):
            LoggingHelper.drop_missing_type_error(node)
            return

        if self.__types_do_not_match(lhs_type, rhs_type):
            TypeCaster.try_to_recover_or_error(lhs_type, rhs_type, node.get_expression(),
                                               set_implicit_conversion_factor_on_lhs=True)

    def visit_assignment(self, node):
        """
        Visits a single expression and assures that type(lhs) == type(rhs).
        :param node: a single assignment.
        :type node: ASTAssignment
        """
        from pynestml.meta_model.ast_assignment import ASTAssignment
        assert isinstance(node, ASTAssignment)

        if node.get_source_position().equals(ASTSourceLocation.get_added_source_position()):
            # no type checks are executed for added nodes, since we assume correctness
            return
        if node.is_direct_assignment:  # case a = b is simple
            self.handle_simple_assignment(node)
        else:
            self.handle_compound_assignment(node)  # e.g. a *= b

    def handle_compound_assignment(self, node):
        rhs_expr = node.get_expression()
        lhs_variable_symbol = node.get_variable().resolve_in_own_scope()
        rhs_type_symbol = rhs_expr.type

        if lhs_variable_symbol is None:
            code, message = Messages.get_equation_var_not_in_state_block(node.get_variable().get_complete_name())
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
            return

        if isinstance(rhs_type_symbol, ErrorTypeSymbol):
            LoggingHelper.drop_missing_type_error(node)
            return

        lhs_type_symbol = lhs_variable_symbol.get_type_symbol()

        if node.is_compound_product:
            if self.__types_do_not_match(lhs_type_symbol, lhs_type_symbol * rhs_type_symbol):
                TypeCaster.try_to_recover_or_error(lhs_type_symbol, lhs_type_symbol * rhs_type_symbol,
                                                   node.get_expression(),
                                                   set_implicit_conversion_factor_on_lhs=True)
                return
            return

        if node.is_compound_quotient:
            if self.__types_do_not_match(lhs_type_symbol, lhs_type_symbol / rhs_type_symbol):
                TypeCaster.try_to_recover_or_error(lhs_type_symbol, lhs_type_symbol / rhs_type_symbol,
                                                   node.get_expression(),
                                                   set_implicit_conversion_factor_on_lhs=True)
                return
            return

        assert node.is_compound_sum or node.is_compound_minus
        if self.__types_do_not_match(lhs_type_symbol, rhs_type_symbol):
            TypeCaster.try_to_recover_or_error(lhs_type_symbol, rhs_type_symbol,
                                               node.get_expression(),
                                               set_implicit_conversion_factor_on_lhs=True)

    @staticmethod
    def __types_do_not_match(lhs_type_symbol, rhs_type_symbol):
        if lhs_type_symbol is None:
            return True

        return not lhs_type_symbol.equals(rhs_type_symbol)

    def handle_simple_assignment(self, node):
        from pynestml.symbols.symbol import SymbolKind
        lhs_variable_symbol = node.get_scope().resolve_to_symbol(node.get_variable().get_complete_name(),
                                                                 SymbolKind.VARIABLE)

        rhs_type_symbol = node.get_expression().type
        if isinstance(rhs_type_symbol, ErrorTypeSymbol):
            LoggingHelper.drop_missing_type_error(node)
            return

        if lhs_variable_symbol is not None and self.__types_do_not_match(lhs_variable_symbol.get_type_symbol(),
                                                                         rhs_type_symbol):
            TypeCaster.try_to_recover_or_error(lhs_variable_symbol.get_type_symbol(), rhs_type_symbol,
                                               node.get_expression(),
                                               set_implicit_conversion_factor_on_lhs=True)

    def visit_function_call(self, node):
        """
        Check consistency for a single function call: check if the called function has been declared, whether the number and types of arguments correspond to the declaration, etc.

        :param node: a single function call.
        :type node: ASTFunctionCall
        """
        func_name = node.get_name()

        if func_name == 'convolve':
            return

        symbol = node.get_scope().resolve_to_symbol(node.get_name(), SymbolKind.FUNCTION)

        if symbol is None and ASTUtils.is_function_delay_variable(node):
            return

        # first check if the function has been declared
        if symbol is None:
            code, message = Messages.get_function_not_declared(node.get_name())
            Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                               code=code, message=message)
            return

        # check if the number of arguments is the same as in the symbol; accept anything for variadic types
        is_variadic: bool = len(symbol.get_parameter_types()) == 1 and isinstance(symbol.get_parameter_types()[0], VariadicTypeSymbol)
        if (not is_variadic) and len(node.get_args()) != len(symbol.get_parameter_types()):
            code, message = Messages.get_wrong_number_of_args(str(node), len(symbol.get_parameter_types()),
                                                              len(node.get_args()))
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                               error_position=node.get_source_position())
            return

        # finally check if the call is correctly typed
        expected_types = symbol.get_parameter_types()
        actual_args = node.get_args()
        actual_types = [arg.type for arg in actual_args]
        for actual_arg, actual_type, expected_type in zip(actual_args, actual_types, expected_types):
            if isinstance(actual_type, ErrorTypeSymbol):
                code, message = Messages.get_type_could_not_be_derived(actual_arg)
                Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                                   error_position=actual_arg.get_source_position())
                return

            if isinstance(expected_type, VariadicTypeSymbol):
                # variadic type symbol accepts anything
                return

            if not actual_type.equals(expected_type) and not isinstance(expected_type, TemplateTypeSymbol):
                TypeCaster.try_to_recover_or_error(expected_type, actual_type, actual_arg,
                                                   set_implicit_conversion_factor_on_lhs=True)

    def __assign_return_types(self, _node):
        for userDefinedFunction in _node.get_functions():
            symbol = userDefinedFunction.get_scope().resolve_to_symbol(userDefinedFunction.get_name(),
                                                                       SymbolKind.FUNCTION)
            # first ensure that the block contains at least one statement
            if symbol is not None and len(userDefinedFunction.get_stmts_body().get_stmts()) > 0:
                # now check that the last statement is a return
                self.__check_return_recursively(userDefinedFunction,
                                                symbol.get_return_type(),
                                                userDefinedFunction.get_stmts_body().get_stmts(),
                                                False)
            # now if it does not have a statement, but uses a return type, it is an error
            elif symbol is not None and userDefinedFunction.has_return_type() and \
                    not symbol.get_return_type().equals(PredefinedTypes.get_void_type()):
                code, message = Messages.get_no_return()
                Logger.log_message(node=_node, code=code, message=message,
                                   error_position=userDefinedFunction.get_source_position(),
                                   log_level=LoggingLevel.ERROR)

    def __check_return_recursively(self, processed_function, type_symbol=None, stmts=None, ret_defined: bool = False) -> None:
        """
        For a handed over statement, it checks if the statement is a return statement and if it is typed according to the handed over type symbol.
        :param type_symbol: a single type symbol
        :type type_symbol: type_symbol
        :param stmts: a list of statements, either simple or compound
        :type stmts: list(ASTSmallStmt,ASTCompoundStmt)
        :param ret_defined: indicates whether a ret has already been defined after this block of stmt, thus is not
                    necessary. Implies that the return has been defined in the higher level block
        """
        # in order to ensure that in the sub-blocks, a return is not necessary, we check if the last one in this
        # block is a return statement, thus it is not required to have a return in the sub-blocks, but optional
        last_statement = stmts[len(stmts) - 1]
        ret_defined = False or ret_defined
        if (len(stmts) > 0 and isinstance(last_statement, ASTStmt)
                and last_statement.is_small_stmt()
                and last_statement.small_stmt.is_return_stmt()):
            ret_defined = True

        # now check that returns are there if necessary and correctly typed
        for c_stmt in stmts:
            if c_stmt.is_small_stmt():
                stmt = c_stmt.small_stmt
            else:
                stmt = c_stmt.compound_stmt

            # if it is a small statement, check if it is a return statement
            if isinstance(stmt, ASTSmallStmt) and stmt.is_return_stmt():
                # first check if the return is the last one in this block of statements
                if stmts.index(c_stmt) != (len(stmts) - 1):
                    code, message = Messages.get_not_last_statement('Return')
                    Logger.log_message(error_position=stmt.get_source_position(),
                                       code=code, message=message,
                                       log_level=LoggingLevel.WARNING)

                # now check that it corresponds to the declared type
                if stmt.get_return_stmt().has_expression() and type_symbol is PredefinedTypes.get_void_type():
                    code, message = Messages.get_type_different_from_expected(PredefinedTypes.get_void_type(),
                                                                              stmt.get_return_stmt().get_expression().type)
                    Logger.log_message(error_position=stmt.get_source_position(),
                                       message=message, code=code, log_level=LoggingLevel.ERROR)

                # if it is not void check if the type corresponds to the one stated
                if not stmt.get_return_stmt().has_expression() and \
                        not type_symbol.equals(PredefinedTypes.get_void_type()):
                    code, message = Messages.get_type_different_from_expected(PredefinedTypes.get_void_type(),
                                                                              type_symbol)
                    Logger.log_message(error_position=stmt.get_source_position(),
                                       message=message, code=code, log_level=LoggingLevel.ERROR)

                if stmt.get_return_stmt().has_expression():
                    type_of_return = stmt.get_return_stmt().get_expression().type
                    if isinstance(type_of_return, ErrorTypeSymbol):
                        code, message = Messages.get_type_could_not_be_derived(processed_function.get_name())
                        Logger.log_message(error_position=stmt.get_source_position(),
                                           code=code, message=message, log_level=LoggingLevel.ERROR)
                    elif not type_of_return.equals(type_symbol):
                        TypeCaster.try_to_recover_or_error(type_symbol, type_of_return,
                                                           stmt.get_return_stmt().get_expression(),
                                                           set_implicit_conversion_factor_on_lhs=True)
            elif isinstance(stmt, ASTCompoundStmt):
                # otherwise it is a compound stmt, thus check recursively
                if stmt.is_if_stmt():
                    self.__check_return_recursively(processed_function,
                                                    type_symbol,
                                                    stmt.get_if_stmt().get_if_clause().get_stmts_body().get_stmts(),
                                                    ret_defined)
                    for else_ifs in stmt.get_if_stmt().get_elif_clauses():
                        self.__check_return_recursively(processed_function,
                                                        type_symbol, else_ifs.get_stmts_body().get_stmts(), ret_defined)
                    if stmt.get_if_stmt().has_else_clause():
                        self.__check_return_recursively(processed_function,
                                                        type_symbol,
                                                        stmt.get_if_stmt().get_else_clause().get_stmts_body().get_stmts(),
                                                        ret_defined)
                elif stmt.is_while_stmt():
                    self.__check_return_recursively(processed_function,
                                                    type_symbol, stmt.get_while_stmt().get_stmts_body().get_stmts(),
                                                    ret_defined)
                elif stmt.is_for_stmt():
                    self.__check_return_recursively(processed_function,
                                                    type_symbol, stmt.get_for_stmt().get_stmts_body().get_stmts(),
                                                    ret_defined)
            # now, if a return statement has not been defined in the corresponding higher level block, we have to ensure that it is defined here
            elif not ret_defined and stmts.index(c_stmt) == (len(stmts) - 1):
                if not (isinstance(stmt, ASTSmallStmt) and stmt.is_return_stmt()):
                    code, message = Messages.get_no_return()
                    Logger.log_message(error_position=stmt.get_source_position(), log_level=LoggingLevel.ERROR,
                                       code=code, message=message)
