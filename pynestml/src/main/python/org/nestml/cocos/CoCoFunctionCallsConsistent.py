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
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.nestml.visitor.ASTHigherOrderVisitor import ASTHigherOrderVisitor


class CoCoFunctionCallsConsistent(CoCo):
    """
    This coco ensures that for all function calls in the handed over neuron, the corresponding function is 
    defined and the types of arguments in the function call correspond to the one in the function symbol.
    Not allowed:
        maximum integer = max(1,2,3)
    """
    __neuronName = None

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionCallsConsistent) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__neuronName = _neuron.getName()
        ASTHigherOrderVisitor.visitNeuron(_neuron, cls.__checkCoco)
        return

    @classmethod
    def __checkCoco(cls, _ast=None):
        """
        For a given node of type function call it checks the coco.
        :param _ast: a single ast.
        :type _ast: AST_
        """
        from pynestml.src.main.python.org.nestml.ast.ASTFunctionCall import ASTFunctionCall
        if isinstance(_ast, ASTFunctionCall):
            # now, for all expressions, check for all function calls, the corresponding function is declared.
            # TODO: here we have to consider the type of the arguments
            symbols = _ast.getScope().resolveToSymbol(_ast.getName(), SymbolKind.FUNCTION)
            # first check if the function has been declared
            if symbols is None:
                Logger.logMessage('[' + cls.__neuronName + '.nestml] Function %s at %s is not declared!'
                                  % (_ast.getName(), _ast.getSourcePosition().printSourcePosition()),
                                  LOGGING_LEVEL.ERROR)
            # now check if the number of arguments is the same as in the symbol
            if len(_ast.getArgs()) != len(symbols.getParameterTypes()):
                Logger.logMessage(
                    '[' + cls.__neuronName + '.nestml] Wrong number of arguments in function-call %s at %s! '
                                             'Expected %s, found %s.'
                    % (_ast.getName(), _ast.getSourcePosition().printSourcePosition(),
                       len(symbols.getParameterTypes()), len(_ast.getArgs())), LOGGING_LEVEL.ERROR)
            # Todo: here we have to ensure correct typing of elements.
            # TODO: @philip treader
            # finally check if the call is correctly typed
            for arg in _ast.getArgs():
                if None is not None:
                    Logger.logMessage(
                        '[' + cls.__neuronName + '.nestml] Argument of function-call %s at %s is wrongly typed! '
                                                 'Expected %s, found %s!'
                        % (_ast.getName(), _ast.getSourcePosition().printSourcePosition(), 'TODO', 'TODO'),
                        LOGGING_LEVEL.ERROR)
        return
