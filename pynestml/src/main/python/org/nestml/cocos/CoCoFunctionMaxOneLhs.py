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

    __declarations = list()

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.ElementDefined) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__declarations = list()
        ASTHigherOrderVisitor.visitNeuron(_neuron, cls.__collectDeclarations)
        for decl in cls.__declarations:
            if decl.isFunction() and len(decl.getVariables())>1:
                Logger.logMessage(
                    '[' + _neuron.getName() +
                    '.nestml] Function (aka. alias) at %s declared with several variables (%s)!'
                    % (
                        decl.getSourcePosition().printSourcePosition(),
                        list((var.getName() for var in decl.getVariables()))),
                    LOGGING_LEVEL.ERROR)

    @classmethod
    def __collectDeclarations(cls, _ast=None):
        """
        For a given node, it collects all the declarations.
        :param _ast: 
        :type _ast: 
        :return: 
        :rtype: 
        """
        from pynestml.src.main.python.org.nestml.ast.ASTDeclaration import ASTDeclaration
        if isinstance(_ast, ASTDeclaration):
            cls.__declarations.append(_ast)
        return
