#
# CoCoCorrectNumeratorOfUnit.py
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


class CoCoCorrectNumeratorOfUnit(CoCo):
    """
    This coco ensures that all units which consist of a dividend and divisor, where the numerator is a numeric
    value, have 1 as the numerator. 
    Allowed:
        V_m 1/mV = ...
    Not allowed:
        V_m 2/mV = ...
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(node)
        node.accept(NumericNumeratorVisitor())
        return


class NumericNumeratorVisitor(ASTVisitor):
    """
    Visits a numeric numerator and checks if the value is 1.
    """

    def visit_unit_type(self, node):
        """
        Check if the coco applies,
        :param node: a single unit type object.
        :type node: ASTUnitType
        """
        if node.is_div and isinstance(node.lhs, int) and node.lhs != 1:
            code, message = Messages.getWrongNumerator(str(node))
            Logger.logMessage(_code=code, _message=message, _errorPosition=node.get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
