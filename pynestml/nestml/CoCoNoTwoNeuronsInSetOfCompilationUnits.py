#
# CoCoNoTwoNeuronsInSetOfCompilationUnits.py
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
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Messages import Messages


class CoCoNoTwoNeuronsInSetOfCompilationUnits(CoCo):
    """
    This Coco checks that for a handed over list of compilation units, not two neurons have the same name.
    """

    @classmethod
    def checkCoCo(cls, _listOfCompilationUnits=None):
        """
        Checks the coco.
        :param _listOfCompilationUnits: a list of compilation units.
        :type _listOfCompilationUnits: list(ASTNESTMLCompilationUnit)
        """
        assert (_listOfCompilationUnits is not None and isinstance(_listOfCompilationUnits, list)), \
            '(PyNestML.CoCo.NameCollisionAcrossUnits) No or wrong type of list provided (%s)!' % type(
                _listOfCompilationUnits)
        listOfNeurons = ASTUtils.getAllNeurons(_listOfCompilationUnits)
        conflictingNeurons = list()
        checked = list()
        for neuronA in listOfNeurons:
            for neuronB in listOfNeurons:
                if neuronA is not neuronB and neuronA.getName() == neuronB.getName():
                    code, message = Messages.getCompilationUnitNameCollision(neuronA.getName(), neuronA.getArtifact(),
                                                                             neuronB.getArtifact())
                    Logger.logMessage(_code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
                conflictingNeurons.append(neuronB)
            checked.append(neuronA)
        return conflictingNeurons
