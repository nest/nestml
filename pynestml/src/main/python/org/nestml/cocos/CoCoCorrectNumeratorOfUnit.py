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
from pynestml.src.main.python.org.nestml.visitor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
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
    __unitTypes = list()
    __neuronName = None

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__unitTypes = list()
        cls.__neuronName = _neuron.getName()
        ASTHigherOrderVisitor.visitNeuron(_neuron, cls.__checkCoco)
        return

    @classmethod
    def __checkCoco(cls, _ast=None):
        """
        For a given node of type unit-type it checks, if the coco applies.
        :param _ast: a single ast node
        :type _ast: AST_
        """
        from pynestml.src.main.python.org.nestml.ast.ASTUnitType import ASTUnitType
        if isinstance(_ast, ASTUnitType) and _ast.isDiv() and isinstance(_ast.getLhs(), int) and _ast.getLhs() != 1:
            Logger.logMessage(
                '[' + cls.__neuronName + '.nestml] Numeric numerator of unit "%s" at %s not 1!'
                % (_ast.printAST(), _ast.getSourcePosition().printSourcePosition()),
                LOGGING_LEVEL.ERROR)
        return
