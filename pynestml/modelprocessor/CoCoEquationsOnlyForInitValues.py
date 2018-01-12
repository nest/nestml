#
# CoCoEquationsOnlyForInitValues.py
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
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class CoCoEquationsOnlyForInitValues(CoCo):
    """
    This coco ensures that ode equations are only provided for variables which have been defined in the
    initial_values block.
    Allowed:
        initial_values:
            V_m mV = 10mV
        end
        equations:
            V_m' = ....
        end
    Not allowed:
        state:
            V_m mV = 10mV
        end
        equations:
            V_m' = ....
        end
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(EquationsOnlyForInitValues())
        return


class EquationsOnlyForInitValues(NESTMLVisitor):
    """
    This visitor ensures that for all ode equations exists an initial value.
    """

    def visitOdeEquation(self, _equation=None):
        """
        Ensures the coco.
        :param _equation: a single equation object.
        :type _equation: ASTOdeEquation
        """
        symbol = _equation.getScope().resolveToSymbol(_equation.getLhs().getNameOfLhs(), SymbolKind.VARIABLE)
        if symbol is not None and not symbol.isInitValues():
            code, message = Messages.getEquationVarNotInInitValuesBlock(_equation.getLhs().getNameOfLhs())
            Logger.logMessage(_code=code, _message=message,
                              _errorPosition=_equation.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
            return
