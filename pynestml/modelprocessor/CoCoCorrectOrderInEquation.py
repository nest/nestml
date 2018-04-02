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
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
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


class OrderOfEquationVisitor(ASTVisitor):
    """
    This visitor checks that all differential equations have a differential order.
    """

    def visit_ode_equation(self, node=None):
        """
        Checks the coco.
        :param node: A single ode equation.
        :type node: ASTOdeEquation
        """
        if node.get_lhs().get_differential_order() == 0:
            code, message = Messages.getOrderNotDeclared(node.get_lhs().get_name())
            Logger.logMessage(_errorPosition=node.get_source_position(), _code=code,
                              _message=message, _logLevel=LOGGING_LEVEL.ERROR)
        return
