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


class CoCoAllFunctionsDeclared(CoCo):
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
        # now, for all expressions, check for all function calls, the corresponding function is declared.
        # TODO: here we have to consider the type of the arguments
        expressions = ASTExpressionCollectorVisitor.collectExpressionsInNeuron(_neuron)
        for expr in expressions:
            for func in expr.getFunctions():  # TODO: here, sometimes a function call does not have a scope -> should not happen
                if func.getScope() is None:
                    print('bingo')

                symbols = func.getScope().resolveToAllSymbols(func.getName(), SymbolKind.FUNCTION)
                if symbols is None:
                    Logger.logAndPrintMessage(
                        '[' + _neuron.getName() + '.nestml] Function %s at %s is not declared!'
                        % (func.getName(), func.getSourcePosition().printSourcePosition()),
                        LOGGING_LEVEL.ERROR)
                    raise FunctionNotDeclared()


class FunctionNotDeclared(Exception):
    """
    This exception is thrown whenever a function call is used with a now defined function.
    """
    pass


class FunctionCallWronglyTyped(Exception):
    """
    This exception is thrown whenever a function call uses arguments of wrong type, e.g., expected integer, handed
    over string.
    """
    pass
