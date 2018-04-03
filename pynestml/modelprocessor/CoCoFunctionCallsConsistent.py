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
from pynestml.utils.Logger import Logger, LoggingLevel
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
    def check_co_co(cls, node=None):
        """
        Checks the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionCallsConsistent) No or wrong type of neuron provided (%s)!' % type(node)
        node.accept(FunctionCallConsistencyVisitor())
        return


class FunctionCallConsistencyVisitor(ASTVisitor):
    """
    This visitor ensures that all function calls are consistent.
    """

    def visit_function_call(self, node):
        """
        Checks the coco.
        :param node: a single function call.
        :type node: ASTFunctionCall
        """
        func_name = node.get_name()
        if func_name == 'convolve' or func_name == 'cond_sum' or func_name == 'curr_sum':
            return
        # now, for all expressions, check for all function calls, the corresponding function is declared.
        symbol = node.get_scope().resolveToSymbol(node.get_name(), SymbolKind.FUNCTION)
        # first check if the function has been declared
        if symbol is None:
            code, message = Messages.getFunctionNotDeclared(node.get_name())
            Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                               code=code, message=message)
        # now check if the number of arguments is the same as in the symbol
        if symbol is not None and len(node.get_args()) != len(symbol.get_parameter_types()):
            code, message = Messages.getWrongNumberOfArgs(str(node), len(symbol.get_parameter_types()),
                                                          len(node.get_args()))
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                               error_position=node.get_source_position())
        # finally check if the call is correctly typed
        elif symbol is not None:
            expected_types = symbol.get_parameter_types()
            actual_types = node.get_args()
            for i in range(0, len(actual_types)):
                expected_type = expected_types[i]
                actual_type = actual_types[i].get_type_either()
                if actual_type.isError():
                    code, message = Messages.getTypeCouldNotBeDerived(actual_types[i])
                    Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR,
                                       error_position=actual_types[i].get_source_position())
                elif not actual_type.getValue().equals(expected_type):
                    if ASTUtils.is_castable_to(actual_type.getValue(), expected_type):
                        code, message = Messages.getFunctionCallImplicitCast(_argNr=i + 1, _functionCall=node,
                                                                             _expectedType=expected_type,
                                                                             _gotType=actual_type, _castable=True)

                        Logger.log_message(error_position=node.get_args()[i].get_source_position(),
                                           code=code, message=message, log_level=LoggingLevel.WARNING)
                    else:
                        code, message = Messages.getFunctionCallImplicitCast(_argNr=i + 1, _functionCall=node,
                                                                             _expectedType=expected_type,
                                                                             _gotType=actual_type, _castable=False)

                        Logger.log_message(error_position=node.get_args()[i].get_source_position(),
                                           code=code, message=message, log_level=LoggingLevel.WARNING)
        return
