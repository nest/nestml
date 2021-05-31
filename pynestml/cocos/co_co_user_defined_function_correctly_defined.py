# -*- coding: utf-8 -*-
#
# co_co_user_defined_function_correctly_defined.py
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
from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.cocos.co_co import CoCo
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.utils.type_caster import TypeCaster


class CoCoUserDefinedFunctionCorrectlyDefined(CoCo):
    """
    This coco ensures that all user defined functions, which are defined with a type, have a return statement
    and the type of the return statement is consistent with the declaration.
    Allowed:
        function foo(...) bool:
            return True
        end
    Not allowed:
        function foo(...) bool:
            return
        end
    Attributes:
        __processedFunction (ast_function): A reference to the currently processed function.
    """
    processed_function = None

    @classmethod
    def check_co_co(cls, _neuron=None):
        """
        Checks the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionCallsConsistent) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__neuronName = _neuron.get_name()
        for userDefinedFunction in _neuron.get_functions():
            cls.processed_function = userDefinedFunction
            symbol = userDefinedFunction.get_scope().resolve_to_symbol(userDefinedFunction.get_name(),
                                                                       SymbolKind.FUNCTION)
            # first ensure that the block contains at least one statement
            if symbol is not None and len(userDefinedFunction.get_block().get_stmts()) > 0:
                # now check that the last statement is a return
                cls.__check_return_recursively(symbol.get_return_type(),
                                               userDefinedFunction.get_block().get_stmts(), False)
            # now if it does not have a statement, but uses a return type, it is an error
            elif symbol is not None and userDefinedFunction.has_return_type() and \
                    not symbol.get_return_type().equals(PredefinedTypes.get_void_type()):
                code, message = Messages.get_no_return()
                Logger.log_message(node=_neuron, code=code, message=message,
                                   error_position=userDefinedFunction.get_source_position(),
                                   log_level=LoggingLevel.ERROR)
        return

    @classmethod
    def __check_return_recursively(cls, type_symbol=None, stmts=None, ret_defined=False):
        """
        For a handed over statement, it checks if the statement is a return statement and if it is typed according
        to the handed over type symbol.
        :param type_symbol: a single type symbol
        :type type_symbol: type_symbol
        :param stmts: a list of statements, either simple or compound
        :type stmts: list(ASTSmallStmt,ASTCompoundStmt)
        :param ret_defined: indicates whether a ret has already beef defined after this block of stmt, thus is not
                    necessary. Implies that the return has been defined in the higher level block
        :type ret_defined: bool
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
                        code, message = Messages.get_type_could_not_be_derived(cls.processed_function.get_name())
                        Logger.log_message(error_position=stmt.get_source_position(),
                                           code=code, message=message, log_level=LoggingLevel.ERROR)
                    elif not type_of_return.equals(type_symbol):
                        TypeCaster.try_to_recover_or_error(type_symbol, type_of_return,
                                                           stmt.get_return_stmt().get_expression())
            elif isinstance(stmt, ASTCompoundStmt):
                # otherwise it is a compound stmt, thus check recursively
                if stmt.is_if_stmt():
                    cls.__check_return_recursively(type_symbol,
                                                   stmt.get_if_stmt().get_if_clause().get_block().get_stmts(),
                                                   ret_defined)
                    for else_ifs in stmt.get_if_stmt().get_elif_clauses():
                        cls.__check_return_recursively(type_symbol, else_ifs.get_block().get_stmt(), ret_defined)
                    if stmt.get_if_stmt().has_else_clause():
                        cls.__check_return_recursively(type_symbol,
                                                       stmt.get_if_stmt().get_else_clause().get_block().get_stmts(),
                                                       ret_defined)
                elif stmt.is_while_stmt():
                    cls.__check_return_recursively(type_symbol, stmt.get_while_stmt().get_block().get_stmts(),
                                                   ret_defined)
                elif stmt.is_for_stmt():
                    cls.__check_return_recursively(type_symbol, stmt.get_for_stmt().get_block().get_stmts(),
                                                   ret_defined)
            # now, if a return statement has not been defined in the corresponding higher level block, we have
            # to ensure that it is defined here
            elif not ret_defined and stmts.index(c_stmt) == (len(stmts) - 1):
                if not (isinstance(stmt, ASTSmallStmt) and stmt.is_return_stmt()):
                    code, message = Messages.get_no_return()
                    Logger.log_message(error_position=stmt.get_source_position(), log_level=LoggingLevel.ERROR,
                                       code=code, message=message)
        return
