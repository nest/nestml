# -*- coding: utf-8 -*-
#
# co_co_neuron_name_unique.py
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
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages


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
    def check_co_co(cls, compilation_unit):
        """
        Checks the coco for the handed over compilation unit.
        :param compilation_unit: a single compilation unit.
        :type compilation_unit: ASTCompilationUnit
        """
        checked = list()  # a list of already checked elements
        for neuronA in compilation_unit.get_neuron_list():
            for neuronB in compilation_unit.get_neuron_list():
                if neuronA is not neuronB and neuronA.get_name() == neuronB.get_name() and neuronB not in checked:
                    code, message = Messages.get_neuron_redeclared(neuronB.get_name())
                    Logger.log_message(error_position=neuronB.get_source_position(),
                                       code=code, message=message,
                                       log_level=LoggingLevel.ERROR)
            checked.append(neuronA)
        return
