#
# CoCoInitVarsWithOdesProvided.py
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
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class CoCoInitVarsWithOdesProvided(CoCo):
    """
    This CoCo ensures that all variables which have been declared in the "initial_values" block are provided 
    with a corresponding ode.
    Allowed:
        initial_values:
            V_m mV = E_L
        end
        ...
        equations:
            V_m' = ...
        end
    Not allowed:        
        initial_values:
            V_m mV = E_L
        end
        ...
        equations:
            # no ode declaration given
        end
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks this coco on the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.VariablesDefined) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(InitVarsVisitor())
        return


class InitVarsVisitor(ASTVisitor):
    """
    This visitor checks that all variables as provided in the init block have been provided with an ode.
    """

    def visit_declaration(self, node=None):
        """
        Checks the coco on the current node.
        :param node: a single declaration.
        :type node: ASTDeclaration
        """
        for var in node.get_variables():
            symbol = node.get_scope().resolveToSymbol(var.get_complete_name(), SymbolKind.VARIABLE)
            # first check that all initial value variables have a lhs
            if symbol is not None and symbol.is_init_values() and not node.has_expression():
                code, message = Messages.getNoRhs(symbol.get_symbol_name())
                Logger.logMessage(_errorPosition=var.get_source_position(), _code=code,
                                  _message=message, _logLevel=LOGGING_LEVEL.ERROR)
            # now check that they have been provided with an ODE
            if symbol is not None and symbol.is_init_values() and not symbol.is_ode_defined() and not symbol.is_function():
                code, message = Messages.getNoOde(symbol.get_symbol_name())
                Logger.logMessage(_errorPosition=var.get_source_position(), _code=code,
                                  _message=message, _logLevel=LOGGING_LEVEL.ERROR)
            if symbol is not None and symbol.is_init_values() and not symbol.has_initial_value():
                code, message = Messages.getNoInitValue(symbol.get_symbol_name())
                Logger.logMessage(_errorPosition=var.get_source_position(), _code=code,
                                  _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        return
