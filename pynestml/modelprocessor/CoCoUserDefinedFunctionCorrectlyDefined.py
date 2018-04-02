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

from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.TypeSymbol import TypeSymbol
from pynestml.modelprocessor.ASTStmt import ASTStmt
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
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
    def checkCoCo(cls, _neuron=None):
        """
        Checks the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionCallsConsistent) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__neuronName = _neuron.get_name()
        for userDefinedFunction in _neuron.get_functions():
            cls.__processedFunction = userDefinedFunction
            symbol = userDefinedFunction.get_scope().resolveToSymbol(userDefinedFunction.get_name(), SymbolKind.FUNCTION)
            # first ensure that the block contains at least one statement
            if symbol is not None and len(userDefinedFunction.get_block().get_stmts()) > 0:
                # now check that the last statement is a return
                cls.__checkReturnRecursively(symbol.get_return_type(), userDefinedFunction.get_block().get_stmts(), False)
            # now if it does not have a statement, but uses a return type, it is an error
            elif symbol is not None and userDefinedFunction.has_return_type() and \
                    not symbol.get_return_type().equals(PredefinedTypes.getVoidType()):
                code, message = Messages.getNoReturn()
                Logger.logMessage(_neuron=_neuron, _code=code, _message=message,
                                  _errorPosition=userDefinedFunction.get_source_position(), _logLevel=LOGGING_LEVEL.ERROR)
        return

    @classmethod
    def __checkReturnRecursively(cls, _typeSymbol=None, _stmts=None, _retDefined=False):
        """
        For a handed over statement, it checks if the statement is a return statement and if it is typed according
        to the handed over type symbol.
        :param _typeSymbol: a single type symbol
        :type _typeSymbol: TypeSymbol
        :param _stmts: a list of statements, either simple or compound
        :type _stmts: list(ASTSmallStmt,ASTCompoundStmt)
        :param _retDefined: indicates whether a ret has already beef defined after this block of stmt, thus is not
                    necessary. Implies that the return has been defined in the higher level block
        :type _retDefined: bool
        """
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
        assert (_typeSymbol is not None and isinstance(_typeSymbol, TypeSymbol)), \
            '(PyNestML.CoCo.FunctionCorrectlyDefined) No or wrong type of type symbol provided (%s)!' % type(
                _typeSymbol)
        assert (isinstance(_retDefined, bool)), \
            '(PyNestML.CoCo.FunctionCorrectlyDefined) Return defined provided incorrectly (%s)!' % type(_retDefined)
        # in order to ensure that in the sub-blocks, a return is not necessary, we check if the last one in this
        # block is a return statement, thus it is not required to have a return in the sub-blocks, but optional
        lastStatement = _stmts[len(_stmts) - 1]
        retDefined = False or _retDefined
        if (len(_stmts) > 0 and isinstance(lastStatement, ASTStmt)
                and lastStatement.is_small_stmt()
                and lastStatement.small_stmt.is_return_stmt()):
            retDefined = True
        # now check that returns are there if necessary and correctly typed
        for c_stmt in _stmts:
            if c_stmt.is_small_stmt():
                stmt = c_stmt.small_stmt
            else:
                stmt = c_stmt.compound_stmt

            # if it is a small statement, check if it is a return statement
            if isinstance(stmt, ASTSmallStmt) and stmt.is_return_stmt():
                # first check if the return is the last one in this block of statements
                if _stmts.index(c_stmt) != (len(_stmts) - 1):
                    code, message = Messages.getNotLastStatement('Return')
                    Logger.logMessage(_errorPosition=stmt.get_source_position(),
                                      _code=code, _message=message,
                                      _logLevel=LOGGING_LEVEL.WARNING)
                # now check that it corresponds to the declared type
                if stmt.get_return_stmt().has_expression() and _typeSymbol is PredefinedTypes.getVoidType():
                    code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getVoidType(),
                                                                          stmt.get_return_stmt().get_expression().
                                                                          get_type_either().getValue())
                    Logger.logMessage(_errorPosition=stmt.get_source_position(),
                                      _message=message, _code=code, _logLevel=LOGGING_LEVEL.ERROR)
                # if it is not void check if the type corresponds to the one stated
                if not stmt.get_return_stmt().has_expression() and not _typeSymbol.equals(PredefinedTypes.getVoidType()):
                    code, message = Messages.getTypeDifferentFromExpected(PredefinedTypes.getVoidType(),
                                                                          _typeSymbol)
                    Logger.logMessage(_errorPosition=stmt.get_source_position(),
                                      _message=message, _code=code, _logLevel=LOGGING_LEVEL.ERROR)
                if stmt.get_return_stmt().has_expression():
                    typeOfReturn = stmt.get_return_stmt().get_expression().get_type_either()
                    if typeOfReturn.isError():
                        code, message = Messages.getTypeCouldNotBeDerived(cls.__processedFunction.get_name())
                        Logger.logMessage(_errorPosition=stmt.get_source_position(),
                                          _code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
                    elif not typeOfReturn.getValue().equals(_typeSymbol):
                        code, message = Messages.getTypeDifferentFromExpected(typeOfReturn.getValue(),
                                                                              _typeSymbol)
                        Logger.logMessage(_errorPosition=stmt.get_source_position(),
                                          _message=message, _code=code, _logLevel=LOGGING_LEVEL.ERROR)
            elif isinstance(stmt, ASTCompoundStmt):
                # otherwise it is a compound stmt, thus check recursively
                if stmt.isIfStmt():
                    cls.__checkReturnRecursively(_typeSymbol, stmt.getIfStmt().getIfClause().get_block().get_stmts(),
                                                 retDefined)
                    for elifs in stmt.getIfStmt().getElifClauses():
                        cls.__checkReturnRecursively(_typeSymbol, elifs.get_block().getStmt(), retDefined)
                    if stmt.getIfStmt().hasElseClause():
                        cls.__checkReturnRecursively(_typeSymbol,
                                                     stmt.getIfStmt().getElseClause().get_block().get_stmts(), retDefined)
                elif stmt.isWhileStmt():
                    cls.__checkReturnRecursively(_typeSymbol, stmt.getWhileStmt().get_block().get_stmts(), retDefined)
                elif stmt.isForStmt():
                    cls.__checkReturnRecursively(_typeSymbol, stmt.getForStmt().get_block().get_stmts(), retDefined)
            # now, if a return statement has not been defined in the corresponding higher level block, we have
            # to ensure that it is defined here
            elif not _retDefined and _stmts.index(c_stmt) == (len(_stmts) - 1):
                if not (isinstance(stmt, ASTSmallStmt) and stmt.is_return_stmt()):
                    code, message = Messages.getNoReturn()
                    Logger.logMessage(_errorPosition=stmt.get_source_position(), _logLevel=LOGGING_LEVEL.ERROR,
                                      _code=code, _message=message)
        return
