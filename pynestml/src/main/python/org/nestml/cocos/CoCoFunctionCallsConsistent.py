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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo
from pynestml.src.main.python.org.nestml.visitor.ASTExpressionCollectorVisitor import ASTExpressionCollectorVisitor
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron


class CoCoFunctionCallsConsistent(CoCo):
    """
    This coco ensures that for all function calls in the handed over neuron, the corresponding function is 
    defined and the types of arguments in the function call correspond to the one in the function symbol.
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
        # now, for all expressions, check for all function calls, the corresponding function is declared.
        # TODO: here we have to consider the type of the arguments
        expressions = ASTExpressionCollectorVisitor.collectExpressionsInNeuron(_neuron)
        for expr in expressions:
            for func in expr.getFunctions():
                symbols = func.getScope().resolveToAllSymbols(func.getName(), SymbolKind.FUNCTION)
                # first check if the function has been declared
                if symbols is None:
                    Logger.logMessage('[' + _neuron.getName() + '.nestml] Function %s at %s is not declared!'
                                      % (func.getName(), func.getSourcePosition().printSourcePosition()),
                                      LOGGING_LEVEL.ERROR)
                # now check if the number of arguments is the same as in the symbol
                if len(func.getArgs()) != len(symbols.getParameterTypes()):
                    Logger.logMessage(
                        '[' + _neuron.getName() + '.nestml] Wrong number of arguments in function-call %s at %s! '
                                                  'Expected %s, found %s.'
                        % (func.getName(), func.getSourcePosition().printSourcePosition(),
                           len(symbols.getParameterTypes()), len(func.getArgs())), LOGGING_LEVEL.ERROR)
                # Todo: here we have to ensure correct typing of elements.
                # TODO: @philip treader
                # finally check if the call is correctly typed
                for arg in func.getArgs():
                    if None is not None:
                        Logger.logMessage(
                            '[' + _neuron.getName() + '.nestml] Argument of function-call %s at %s is wrongly typed! '
                                                      'Expected %s, found %s.'
                            % (func.getName(), func.getSourcePosition().printSourcePosition(), 'TODO', 'TODO'),
                            LOGGING_LEVEL.ERROR)
