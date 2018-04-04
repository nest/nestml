#
# CoCoUserDefinedFunctionCorrectlyDefined.py
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

from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTStmt import ASTStmt
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.TypeSymbol import TypeSymbol
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages


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
        __processedFunction (ASTFunction): A reference to the currently processed function.
    """
    __processedFunction = None

    @classmethod
    def check_co_co(cls, node=None):
        """
        Checks the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionCallsConsistent) No or wrong type of neuron provided (%s)!' % type(node)
        cls.__neuronName = node.get_name()
        for userDefinedFunction in node.get_functions():
            cls.__processedFunction = userDefinedFunction
            symbol = userDefinedFunction.get_scope().resolve_to_symbol(userDefinedFunction.get_name(),
                                                                       SymbolKind.FUNCTION)
            # first ensure that the block contains at least one statement
            if symbol is not None and len(userDefinedFunction.get_block().get_stmts()) > 0:
                # now check that the last statement is a return
                cls.__check_return_recursively(symbol.get_return_type(), userDefinedFunction.get_block().get_stmts(),
                                               False)
            # now if it does not have a statement, but uses a return type, it is an error
            elif symbol is not None and userDefinedFunction.has_return_type() and \
                    not symbol.get_return_type().equals(PredefinedTypes.get_void_type()):
                code, message = Messages.getNoReturn()
                Logger.log_message(neuron=node, code=code, message=message,
                                   error_position=userDefinedFunction.get_source_position(),
                                   log_level=LoggingLevel.ERROR)
        return

    @classmethod
    def __check_return_recursively(cls, type_symbol=None, stmts=None, ret_defined=False):
        """
        For a handed over statement, it checks if the statement is a return statement and if it is typed according
        to the handed over type symbol.
        :param type_symbol: a single type symbol
        :type type_symbol: TypeSymbol
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
                    code, message = Messages.getNotLastStatement('Return')
                    Logger.log_message(error_position=stmt.get_source_position(),
                                       code=code, message=message,
                                       log_level=LoggingLevel.WARNING)
                # now check that it corresponds to the declared type
                if stmt.get_return_stmt().has_expression() and type_symbol is PredefinedTypes.get_void_type():
                    code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.get_void_type(),
                                                                          stmt.get_return_stmt().get_expression().
                                                                          get_type_either().get_value())
                    Logger.log_message(error_position=stmt.get_source_position(),
                                       message=message, code=code, log_level=LoggingLevel.ERROR)
                # if it is not void check if the type corresponds to the one stated
                if not stmt.get_return_stmt().has_expression() and not type_symbol.equals(
                        PredefinedTypes.get_void_type()):
                    code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.get_void_type(),
                                                                          type_symbol)
                    Logger.log_message(error_position=stmt.get_source_position(),
                                       message=message, code=code, log_level=LoggingLevel.ERROR)
                if stmt.get_return_stmt().has_expression():
                    type_of_return = stmt.get_return_stmt().get_expression().get_type_either()
                    if type_of_return.is_error():
                        code, message = Messages.getTypeCouldNotBeDerived(cls.__processedFunction.get_name())
                        Logger.log_message(error_position=stmt.get_source_position(),
                                           code=code, message=message, log_level=LoggingLevel.ERROR)
                    elif not type_of_return.get_value().equals(type_symbol):
                        code, message = Messages.getTypeDifferentFromExpected(type_of_return.get_value(),
                                                                              type_symbol)
                        Logger.log_message(error_position=stmt.get_source_position(),
                                           message=message, code=code, log_level=LoggingLevel.ERROR)
            elif isinstance(stmt, ASTCompoundStmt):
                # otherwise it is a compound stmt, thus check recursively
                if stmt.isIfStmt():
                    cls.__check_return_recursively(type_symbol, stmt.getIfStmt().getIfClause().get_block().get_stmts(),
                                                   ret_defined)
                    for elifs in stmt.getIfStmt().getElifClauses():
                        cls.__check_return_recursively(type_symbol, elifs.get_block().getStmt(), ret_defined)
                    if stmt.getIfStmt().hasElseClause():
                        cls.__check_return_recursively(type_symbol,
                                                       stmt.getIfStmt().getElseClause().get_block().get_stmts(),
                                                       ret_defined)
                elif stmt.isWhileStmt():
                    cls.__check_return_recursively(type_symbol, stmt.getWhileStmt().get_block().get_stmts(), ret_defined)
                elif stmt.isForStmt():
                    cls.__check_return_recursively(type_symbol, stmt.getForStmt().get_block().get_stmts(), ret_defined)
            # now, if a return statement has not been defined in the corresponding higher level block, we have
            # to ensure that it is defined here
            elif not ret_defined and stmts.index(c_stmt) == (len(stmts) - 1):
                if not (isinstance(stmt, ASTSmallStmt) and stmt.is_return_stmt()):
                    code, message = Messages.getNoReturn()
                    Logger.log_message(error_position=stmt.get_source_position(), log_level=LoggingLevel.ERROR,
                                       code=code, message=message)
        return
