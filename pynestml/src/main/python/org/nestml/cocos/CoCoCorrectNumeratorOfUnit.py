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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo
from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger


class CoCoCorrectNumeratorOfUnit(CoCo):
    """
    This coco ensures that all units which consist of a dividend and divisor, where the numerator is a numeric
    value, have 1 as the numerator. 
    Allowed:
        V_m 1/mV = ...
    Not allowed:
        V_m 2/mV = ...
    """
    neuronName = None

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.neuronName = _neuron.getName()
        _neuron.accept(NumericNumeratorVisitor())
        return


class NumericNumeratorVisitor(NESTMLVisitor):
    """
    Visits a numeric numerator and checks if the value is 1.
    """

    def visitUnitType(self, _unitType=None):
        """
        Check if the coco applies,
        :param _unitType: a single unit type object.
        :type _unitType: ASTUnitType
        """
        if _unitType.isDiv() and isinstance(_unitType.getLhs(), int) and _unitType.getLhs() != 1:
            Logger.logMessage(
                '[' + CoCoCorrectNumeratorOfUnit.neuronName + '.nestml] Numeric numerator of unit "%s" at %s not 1!'
                % (_unitType.printAST(), _unitType.getSourcePosition().printSourcePosition()),
                LOGGING_LEVEL.ERROR)
        return
