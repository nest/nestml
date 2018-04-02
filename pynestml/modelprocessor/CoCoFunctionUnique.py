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
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


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
        checked_funcs_names = list()
        for func in _neuron.get_functions():
            if func.get_name() not in checked_funcs_names:
                symbols = func.get_scope().resolveToAllSymbols(func.get_name(), SymbolKind.FUNCTION)
                if isinstance(symbols, list) and len(symbols) > 1:
                    checked = list()
                    for funcA in symbols:
                        for funcB in symbols:
                            if funcA is not funcB and funcB not in checked:
                                if funcA.is_predefined:
                                    code, message = Messages.getFunctionRedeclared(funcA.get_symbol_name(), True)
                                    Logger.logMessage(_errorPosition=funcB.get_referenced_object().get_source_position(),
                                                      _logLevel=LOGGING_LEVEL.ERROR,
                                                      _message=message, _code=code)
                                elif funcB.is_predefined:
                                    code, message = Messages.getFunctionRedeclared(funcA.get_symbol_name(), True)
                                    Logger.logMessage(_errorPosition=funcA.get_referenced_object().get_source_position(),
                                                      _logLevel=LOGGING_LEVEL.ERROR,
                                                      _message=message, _code=code)
                                else:
                                    code, message = Messages.getFunctionRedeclared(funcA.get_symbol_name(), False)
                                    Logger.logMessage(_errorPosition=funcB.get_referenced_object().get_source_position(),
                                                      _logLevel=LOGGING_LEVEL.ERROR,
                                                      _message=message, _code=code)
                        checked.append(funcA)
            checked_funcs_names.append(func.get_name())
        return
