#
# CoCoCorrectOrderInEquation.py
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
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class CoCoCorrectOrderInEquation(CoCo):
    """
    This coco ensures that whenever a ode-equation is assigned to a variable, it have a differential order 
    of at leas one.
    Allowed:
        equations:
            V_m' = ...
        end
    Not allowed:
        equations:
            V_m = ...
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
            '(PyNestML.CoCo.OrderInEquation) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(OrderOfEquationVisitor())
        return


class OrderOfEquationVisitor(NESTMLVisitor):
    """
    This visitor checks that all differential equations have a differential order.
    """

    def visitOdeEquation(self, _equation=None):
        """
        Checks the coco.
        :param _equation: A single ode equation.
        :type _equation: ASTOdeEquation
        """
        if _equation.getLhs().getDifferentialOrder() == 0:
            code, message = Messages.getOrderNotDeclared(_equation.getLhs().getName())
            Logger.logMessage(_errorPosition=_equation.getSourcePosition(), _code=code,
                              _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        return
