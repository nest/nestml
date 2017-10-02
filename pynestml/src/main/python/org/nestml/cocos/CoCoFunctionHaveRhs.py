#
# CoCoFunctionHaveRhs.py
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


class CoCoFunctionHaveRhs(CoCo):
    """
    This coco ensures that all function declarations, e.g., function V_rest mV = V_m - 55mV, have a rhs.
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionWithRhs) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(FunctionRhsVisitor())
        return


class FunctionRhsVisitor(NESTMLVisitor):
    """
    This visitor ensures that everything declared as function has a rhs.
    """

    def visitDeclaration(self, _declaration=None):
        """
        Checks if the coco applies.
        :param _declaration: a single declaration.
        :type _declaration: ASTDeclaration.
        """
        if _declaration.isFunction() and not _declaration.hasExpression():
            Logger.logMessage(
                'Function variable %s at %s has no right-hand side!'
                % (_declaration.getVariables()[0].getName(),
                   _declaration.getSourcePosition().printSourcePosition()), LOGGING_LEVEL.ERROR)
        return
