#
# CoCoFunctionMaxOneLhs.py
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


class CoCoFunctionMaxOneLhs(CoCo):
    """
    This coco ensures that whenever a function (aka alias) is declared, only one left-hand side is presend.
    Allowed:
        function V_rest mV = V_m - 55mV
    Not allowed:
        function V_reset,V_rest mV = V_m - 55mV
    """

    __neuronName = None

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionsWithLhs) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__neuronName = _neuron.getName()
        ASTHigherOrderVisitor.visitNeuron(_neuron, cls.__checkCoco)
        return

    @classmethod
    def __checkCoco(cls, _ast=None):
        """
        For a given node of type declaration, it checks if the coco applies.
        :param _ast: a single node
        :type _ast: AST_
        """
        from pynestml.src.main.python.org.nestml.ast.ASTDeclaration import ASTDeclaration
        if isinstance(_ast, ASTDeclaration) and _ast.isFunction() and len(_ast.getVariables()) > 1:
            Logger.logMessage(
                '[' + cls.__neuronName +
                '.nestml] Function (aka. alias) at %s declared with several variables (%s)!'
                % (
                    _ast.getSourcePosition().printSourcePosition(),
                    list((var.getName() for var in _ast.getVariables()))),
                LOGGING_LEVEL.ERROR)
        return
