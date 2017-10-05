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
from pynestml.nestml.CoCo import CoCo
from pynestml.nestml.Symbol import SymbolKind
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor


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


class FunctionCallConsistencyVisitor(NESTMLVisitor):
    """
    This visitor ensures that all function calls are consistent.
    """

    def visitFunctionCall(self, _functionCall=None):
        """
        Checks the coco.
        :param _functionCall: a single function call.
        :type _functionCall: ASTFunctionCall
        """
        funcName = _functionCall.getName()
        if funcName == 'convolve' or funcName == 'cond_sum' or funcName == 'curr_sum':
            return
        # now, for all expressions, check for all function calls, the corresponding function is declared.
        symbol = _functionCall.getScope().resolveToSymbol(_functionCall.getName(), SymbolKind.FUNCTION)
        # first check if the function has been declared
        if symbol is None:
            Logger.logMessage(
                'Function %s at %s is not declared!'
                % (_functionCall.getName(), _functionCall.getSourcePosition().printSourcePosition()),
                LOGGING_LEVEL.ERROR)
        # now check if the number of arguments is the same as in the symbol
        if symbol is not None and len(_functionCall.getArgs()) != len(symbol.getParameterTypes()):
            Logger.logMessage(
                'Wrong number of arguments in function-call %s at %s! Expected %s, found %s.'
                % (_functionCall.getName(), _functionCall.getSourcePosition().printSourcePosition(),
                   len(symbol.getParameterTypes()), len(_functionCall.getArgs())), LOGGING_LEVEL.ERROR)
        # finally check if the call is correctly typed
        elif symbol is not None:
            expectedTypes = symbol.getParameterTypes()
            actualTypes = _functionCall.getArgs()
            for i in range(0, len(actualTypes)):
                expectedType = expectedTypes[i]
                actualType = actualTypes[i].getTypeEither()
                if actualType.isError():
                    Logger.logMessage(
                        'Type of argument %s of function-call %s at %s not recognized! '
                        % (actualTypes[i].printAST(),
                           _functionCall.getName(),
                           _functionCall.getSourcePosition().printSourcePosition()),
                        LOGGING_LEVEL.ERROR)
                elif not actualType.getValue().equals(expectedType):
                    if ASTUtils.isCastableTo(actualType.getValue(), expectedType):
                        Logger.logMessage(
                            str(i + 1) + '. argument of function-call %s at %s is wrongly typed! '
                                         'Implicit cast from %s to %s!'
                            % (_functionCall.getName(), _functionCall.getSourcePosition().printSourcePosition(),
                               actualType.getValue().printSymbol(),
                               expectedType.printSymbol()),
                            LOGGING_LEVEL.WARNING)
                    else:
                        Logger.logMessage(
                            str(i + 1) + '. argument of function-call %s at %s is wrongly typed! '
                                         'Expected %s, found %s!'
                            % (_functionCall.getName(), _functionCall.getSourcePosition().printSourcePosition(),
                               expectedType.printSymbol(),
                               actualType.getValue().printSymbol()),
                            LOGGING_LEVEL.ERROR)

        return
