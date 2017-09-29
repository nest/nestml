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
from pynestml.src.main.python.org.nestml.visitor.NESTMLVisitor import NESTMLVisitor
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
    neuronName = None

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.CurrentBuffersNotSpecified) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.neuronName = _neuron.getName()
        _neuron.accept(CurrentTypeSpecifiedVisitor())
        return


class CurrentTypeSpecifiedVisitor(NESTMLVisitor):
    """
    This visitor ensures that all current buffers are not specified with keywords.
    """

    def visitInputLine(self, _line=None):
        if _line.isCurrent() and _line.hasInputTypes() and len(_line.getInputTypes()) > 0:
            Logger.logMessage(
                '[' + CoCoCurrentBuffersNotSpecified.neuronName +
                '.nestml] Current buffer "%s" at %s specified with type keywords (%s)!'
                % (_line.getName(), _line.getSourcePosition().printSourcePosition(),
                   list((buf.printAST() for buf in _line.getInputTypes()))),
                LOGGING_LEVEL.ERROR)
        return
