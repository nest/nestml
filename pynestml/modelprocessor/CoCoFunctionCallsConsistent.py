#
# CoCoAllFunctionsDeclared.py
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
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Messages import Messages
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTVisitor import ASTVisitor


class CoCoFunctionCallsConsistent(CoCo):
    """
    This coco ensures that for all function calls in the handed over neuron, the corresponding function is 
    defined and the types of arguments in the function call correspond to the one in the function symbol.
    Not allowed:
        maximum integer = max(1,2,3)
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionCallsConsistent) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(FunctionCallConsistencyVisitor())
        return


class FunctionCallConsistencyVisitor(ASTVisitor):
    """
    This visitor ensures that all function calls are consistent.
    """

    def visit_function_call(self, _ast=None):
        """
        Checks the coco.
        :param _ast: a single function call.
        :type _ast: ASTFunctionCall
        """
        func_name = _ast.get_name()
        if func_name == 'convolve' or func_name == 'cond_sum' or func_name == 'curr_sum':
            return
        # now, for all expressions, check for all function calls, the corresponding function is declared.
        symbol = _ast.get_scope().resolveToSymbol(_ast.get_name(), SymbolKind.FUNCTION)
        # first check if the function has been declared
        if symbol is None:
            code, message = Messages.getFunctionNotDeclared(_ast.get_name())
            Logger.logMessage(_errorPosition=_ast.get_source_position(), _logLevel=LOGGING_LEVEL.ERROR,
                              _code=code, _message=message)
        # now check if the number of arguments is the same as in the symbol
        if symbol is not None and len(_ast.get_args()) != len(symbol.get_parameter_types()):
            code, message = Messages.getWrongNumberOfArgs(str(_ast), len(symbol.get_parameter_types()),
                                                          len(_ast.get_args()))
            Logger.logMessage(_code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR,
                              _errorPosition=_ast.get_source_position())
        # finally check if the call is correctly typed
        elif symbol is not None:
            expected_types = symbol.get_parameter_types()
            actual_types = _ast.get_args()
            for i in range(0, len(actual_types)):
                expected_type = expected_types[i]
                actual_type = actual_types[i].get_type_either()
                if actual_type.isError():
                    code, message = Messages.getTypeCouldNotBeDerived(actual_types[i])
                    Logger.logMessage(_code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR,
                                      _errorPosition=actual_types[i].get_source_position())
                elif not actual_type.getValue().equals(expected_type):
                    if ASTUtils.is_castable_to(actual_type.getValue(), expected_type):
                        code, message = Messages.getFunctionCallImplicitCast(_argNr=i + 1, _functionCall=_ast,
                                                                             _expectedType=expected_type,
                                                                             _gotType=actual_type, _castable=True)

                        Logger.logMessage(_errorPosition=_ast.get_args()[i].get_source_position(),
                                          _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
                    else:
                        code, message = Messages.getFunctionCallImplicitCast(_argNr=i + 1, _functionCall=_ast,
                                                                             _expectedType=expected_type,
                                                                             _gotType=actual_type, _castable=False)

                        Logger.logMessage(_errorPosition=_ast.get_args()[i].get_source_position(),
                                          _code=code, _message=message, _logLevel=LOGGING_LEVEL.WARNING)
        return
