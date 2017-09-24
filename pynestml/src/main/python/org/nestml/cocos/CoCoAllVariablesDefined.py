#
# CoCoAllVariablesDefined.py
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
from pynestml.src.main.python.org.nestml.visitor.ASTExpressionCollectorVisitor import ASTExpressionCollectorVisitor


class CoCoAllVariablesDefined(CoCo):
    """
    This class represents a constraint condition which ensures that all elements as used in expressions have been
    previously defined.
    """
    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks if this coco applies for the handed over neuron. Models which use not defined elements are not 
        correct, thus an exception is generated. Caution: This 
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.ElementDefined) No or wrong type of neuron provided (%s)!' %type(_neuron)
        # for each variable in all expressions, check if the variable has been defined previously
        expressions = ASTExpressionCollectorVisitor.collectExpressionsInNeuron(_neuron)
        for expr in expressions:
            for var in expr.getVariables():
                #print(var.getName())
                pass


class ElementNotDefined(Exception):
    """
    This exception is thrown whenever an element, which is used in an expression, has not been defined.
    """
    pass
