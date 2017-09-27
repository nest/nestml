#
# CoCoCurrentBuffersNotSpecified.py
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


class CoCoCurrentBuffersNotSpecified(CoCo):
    """
    This coco ensures that current buffers are not specified with a keyword.
    Allowed:
        input:
            current <- current
        end
    Not allowed:
        input:
            current <- inhibitory current
        end     
    """
    __neuronName = None
    __currentInputBuffers = list()

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.CurrentBuffersNotSpecified) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__neuronName = _neuron.getName()
        ASTHigherOrderVisitor.visitNeuron(_neuron, cls.__checkCoco)
        return

    @classmethod
    def __checkCoco(cls, _ast=None):
        """
        For a given node of type current input buffer it checks the coco.
        :param _ast: a single ast.
        :type _ast: AST_
        """
        from pynestml.src.main.python.org.nestml.ast.ASTInputLine import ASTInputLine
        if isinstance(_ast, ASTInputLine) and _ast.isCurrent() and _ast.hasInputTypes() and \
                        len(_ast.getInputTypes()) > 0:
            Logger.logMessage(
                '[' + cls.__neuronName +
                '.nestml] Current buffer "%s" at %s specified with type keywords (%s)!'
                % (_ast.getName(), _ast.getSourcePosition().printSourcePosition(),
                   list((buf.printAST() for buf in _ast.getInputTypes()))),
                LOGGING_LEVEL.ERROR)
        return
