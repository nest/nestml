#
# CoCoTypeOfBufferUnique.py
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


class CoCoTypeOfBufferUnique(CoCo):
    """
    This coco ensures that each spike buffer has at most one type of modifier inhibitory and excitatory.
    Allowed:
        spike <- inhibitory spike
    Not allowed:
        spike <- inhibitory inhibitory spike
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
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__neuronName = _neuron.getName()
        ASTHigherOrderVisitor.visitNeuron(_neuron, cls.__checkCoco)
        return

    @classmethod
    def __checkCoco(cls, _ast=None):
        """
        For a given node, it collects all the spike buffers declarations.
        :param _ast: a single ast.
        :type _ast: AST_
        """
        from pynestml.src.main.python.org.nestml.ast.ASTInputLine import ASTInputLine
        if isinstance(_ast, ASTInputLine) and _ast.isSpike():
            if _ast.hasInputTypes() and len(_ast.getInputTypes()) > 1:
                inh = 0
                ext = 0
                for typ in _ast.getInputTypes():
                    if typ.isExcitatory():
                        ext += 1
                    if typ.isInhibitory():
                        inh += 1
                if inh > 1:
                    Logger.logMessage(
                        '[' + cls.__neuronName +
                        '.nestml] Spike buffer "%s" at %s defined with multiple inhibitory keywords!'
                        % (_ast.getName(), _ast.getSourcePosition().printSourcePosition()),
                        LOGGING_LEVEL.ERROR)
                if ext > 1:
                    Logger.logMessage(
                        '[' + cls.__neuronName +
                        '.nestml] Spike buffer "%s" at %s defined with multiple excitatory keywords!'
                        % (_ast.getName(), _ast.getSourcePosition().printSourcePosition()),
                        LOGGING_LEVEL.ERROR)
        return
