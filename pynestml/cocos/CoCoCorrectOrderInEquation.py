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
from pynestml.cocos.CoCo import CoCo
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages
from pynestml.visitors.ASTVisitor import ASTVisitor


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
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        node.accept(OrderOfEquationVisitor())


class OrderOfEquationVisitor(ASTVisitor):
    """
    This visitor checks that all differential equations have a differential order.
    """

    def visit_ode_equation(self, node):
        """
        Checks the coco.
        :param node: A single ode equation.
        :type node: ASTOdeEquation
        """
        if node.get_lhs().get_differential_order() == 0:
            code, message = Messages.get_order_not_declared(node.get_lhs().get_name())
            Logger.log_message(error_position=node.get_source_position(), code=code,
                               message=message, log_level=LoggingLevel.ERROR)
