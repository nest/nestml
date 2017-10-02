#
# CoCoFunctionUnique.py
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
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron


class CoCoFunctionUnique(CoCo):
    """
    This Coco ensures that each function is defined exactly once (thus no redeclaration occurs).
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks if each function is defined uniquely.
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionUnique) No or wrong type of neuron provided (%s)!' % type(_neuron)
        checkedFuncsNames = list()
        for func in _neuron.getFunctions():
            if func.getName() not in checkedFuncsNames:
                symbols = func.getScope().resolveToAllSymbols(func.getName(), SymbolKind.FUNCTION)
                if isinstance(symbols, list) and len(symbols) > 1:
                    checked = list()
                    for funcA in symbols:
                        for funcB in symbols:
                            if funcA is not funcB and funcB not in checked:
                                if funcA.isPredefined():
                                    Logger.logMessage(
                                        'Predefined function "%s" redeclared at %s!'
                                        % (funcA.getSymbolName(), func.getSourcePosition().printSourcePosition()),
                                        LOGGING_LEVEL.ERROR)
                                elif funcB.isPredefined():
                                    Logger.logMessage(
                                        'Predefined function "%s" redeclared at %s!'
                                        % (funcB.getSymbolName(), func.getSourcePosition().printSourcePosition()),
                                        LOGGING_LEVEL.ERROR)
                                else:
                                    Logger.logMessage(
                                        'Function "%s" redeclared at %s! First declared at %s!'
                                        % (funcA.getSymbolName(),
                                           funcB.getReferencedObject().getSourcePosition().printSourcePosition(),
                                           funcA.getReferencedObject().getSourcePosition().printSourcePosition()),
                                        LOGGING_LEVEL.ERROR)
                        checked.append(funcA)
            checkedFuncsNames.append(func.getName())
        return
