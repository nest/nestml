# -*- coding: utf-8 -*-
#
# co_co_no_two_neurons_in_set_of_compilation_units.py
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
from pynestml.cocos.co_co import CoCo
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages


class CoCoNoTwoNeuronsInSetOfCompilationUnits(CoCo):
    """
    This Coco checks that for a handed over list of compilation units, not two neurons have the same name.
    """

    @classmethod
    def check_co_co(cls, list_of_compilation_units):
        """
        Checks the coco.
        :param list_of_compilation_units: a list of compilation units.
        :type list_of_compilation_units: list(ASTNestMLCompilationUnit)
        """
        list_of_neurons = ASTUtils.get_all_neurons(list_of_compilation_units)
        conflicting_neurons = list()
        checked = list()
        for neuronA in list_of_neurons:
            for neuronB in list_of_neurons:
                if neuronA is not neuronB and neuronA.get_name() == neuronB.get_name():
                    code, message = Messages.get_compilation_unit_name_collision(neuronA.get_name(),
                                                                                 neuronA.get_artifact_name(),
                                                                                 neuronB.get_artifact_name())
                    Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR)
                conflicting_neurons.append(neuronB)
            checked.append(neuronA)
        return conflicting_neurons
