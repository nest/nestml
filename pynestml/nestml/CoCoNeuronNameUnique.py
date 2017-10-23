#
# CoCoNeuronNameUnique.py
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
from pynestml.nestml.CoCo import CoCo
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class CoCoNeuronNameUnique(CoCo):
    """
    This coco ensures that for all elements in a single compile units, the names of all neurons are pairwise 
    distinct.
    Allowed:
        neuron a:
            ...
        end
        ...
        neuron b:
            ...
        end
    Not allowed:
        neuron a:
            ...
        end
        ...
        neuron a: <- neuron with the same name
            ...
        end
    """

    @classmethod
    def checkCoCo(cls, _compilationUnit=None):
        """
        Checks the coco for the handed over compilation unit.
        :param _compilationUnit: a single compilation unit.
        :type _compilationUnit: ASTCompilationUnit
        """
        from pynestml.nestml.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
        assert (_compilationUnit is not None and isinstance(_compilationUnit, ASTNESTMLCompilationUnit)), \
            '(PyNestML.CoCo.NeuronNameUnique) No or wrong type of compilation unit provided (%s)!' % type(
                _compilationUnit)
        checked = list()  # a list of already checked elements
        for neuronA in _compilationUnit.getNeuronList():
            for neuronB in _compilationUnit.getNeuronList():
                if neuronA is not neuronB and neuronA.getName() == neuronB.getName() and neuronB not in checked:
                    code, message = Messages.getNeuronRedeclared(neuronB.getName())
                    Logger.logMessage(_errorPosition=neuronB.getSourcePosition(),
                                      _code=code, _message=message,
                                      _logLevel=LOGGING_LEVEL.ERROR)
            checked.append(neuronA)
        return
