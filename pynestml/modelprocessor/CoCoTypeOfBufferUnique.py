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
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class CoCoTypeOfBufferUnique(CoCo):
    """
    This coco ensures that each spike buffer has at most one type of modifier inhibitory and excitatory.
    Allowed:
        spike <- inhibitory spike
    Not allowed:
        spike <- inhibitory inhibitory spike
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.neuronName = _neuron.getName()
        _neuron.accept(TypeOfBufferUniqueVisitor())
        return


class TypeOfBufferUniqueVisitor(ASTVisitor):
    """
    This visitor ensures that all buffers are specified uniquely by keywords.
    """

    def visitInputLine(self, _line=None):
        """
        Checks the coco on the current node.
        :param _line: a single input line.
        :type _line: ASTInputLine
        """
        from pynestml.modelprocessor.ASTInputLine import ASTInputLine
        assert (_line is not None and isinstance(_line, ASTInputLine)), \
            '(PyNestML.CoCo.TypeOfBufferUnique) No or wrong type of input line provided (%s)!' % type(_line)
        if _line.isSpike():
            if _line.hasInputTypes() and len(_line.getInputTypes()) > 1:
                inh = 0
                ext = 0
                for typ in _line.getInputTypes():
                    if typ.isExcitatory():
                        ext += 1
                    if typ.isInhibitory():
                        inh += 1
                if inh > 1:
                    code, message = Messages.getMultipleKeywords('inhibitory')
                    Logger.logMessage(_errorPosition=_line.get_source_position(), _code=code, _message=message,
                                      _logLevel=LOGGING_LEVEL.ERROR)
                if ext > 1:
                    code, message = Messages.getMultipleKeywords('excitatory')
                    Logger.logMessage(_errorPosition=_line.get_source_position(), _code=code, _message=message,
                                      _logLevel=LOGGING_LEVEL.ERROR)
        return
