#
# CoCoVariableOncePerScope.py
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
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages


class CoCoVariableOncePerScope(CoCo):
    """
    This coco ensures that each variables is defined at most once per scope, thus no redeclaration occurs.
    """

    @classmethod
    def check_co_co(cls, node=None):
        """
        Checks if each variable is defined at most once per scope. Obviously, this test does not check if a declaration
        is shadowed by an embedded scope.
        :param node: a single neuron
        :type node: ASTNeuron
        """
        from pynestml.modelprocessor.ASTNeuron import ASTNeuron
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.VariableOncePerScope) No or wrong type of neuron provided (%s)!' % type(node)
        cls.__checkScope(node, node.get_scope())
        return

    @classmethod
    def __checkScope(cls, _neuron=None, _scope=None):
        """
        Checks a single scope and proceeds recursively.
        :param _neuron: a single neuron object, required for correct printing of messages.
        :type _neuron: ASTNeuron
        :param _scope: a single scope to check.
        :type _scope: Scope
        """
        from pynestml.modelprocessor.ASTNeuron import ASTNeuron
        from pynestml.modelprocessor.Scope import Scope
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.VariableOncePerScope) No or wrong type of neuron provided (%s)!' % type(_neuron)
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.CoCo.VariableOncePerScope) No or wrong type of scope provided (%s)!' % type(_scope)
        checked = list()
        for sym1 in _scope.getSymbolsInThisScope():
            for sym2 in _scope.getSymbolsInThisScope():
                if sym1 is not sym2 and sym1.get_symbol_name() == sym2.get_symbol_name() and \
                                sym1.get_symbol_kind() == sym2.get_symbol_kind() and \
                                sym1.get_symbol_kind() == SymbolKind.VARIABLE and \
                                sym2 not in checked:
                    if sym1.is_predefined():
                        code, message = Messages.getVariableRedeclared(sym1.get_symbol_name(), True)
                        Logger.log_message(error_position=sym2.get_referenced_object().get_source_position(),
                                           neuron=_neuron, log_level=LoggingLevel.ERROR, code=code, message=message)
                    elif sym2.is_predefined():
                        code, message = Messages.getVariableRedeclared(sym1.get_symbol_name(), True)
                        Logger.log_message(error_position=sym1.get_referenced_object().get_source_position(),
                                           neuron=_neuron, log_level=LoggingLevel.ERROR, code=code, message=message)
                    elif sym1.get_referenced_object().get_source_position().before(
                            sym2.get_referenced_object().get_source_position()):
                        code, message = Messages.getVariableRedeclared(sym1.get_symbol_name(), False)
                        Logger.log_message(error_position=sym2.get_referenced_object().get_source_position(),
                                           neuron=_neuron, log_level=LoggingLevel.ERROR, code=code, message=message)
            checked.append(sym1)
        for scope in _scope.getScopes():
            cls.__checkScope(_neuron, scope)
        return
