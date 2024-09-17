# -*- coding: utf-8 -*-
#
# continuous_input_processing.py
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

import copy

from pynestml.utils.mechanism_processing import MechanismProcessing

from collections import defaultdict


class ContinuousInputProcessing(MechanismProcessing):
    mechType = "continuous_input"

    def __init__(self, params):
        super(MechanismProcessing, self).__init__(params)

    @classmethod
    def collect_information_for_specific_mech_types(cls, neuron, mechs_info):
        for continuous_name, continuous_info in mechs_info.items():
            continuous = defaultdict()
            for port in continuous_info["Continuous"]:
                continuous[port.name] = copy.deepcopy(port)
            mechs_info[continuous_name]["Continuous"] = continuous

        return mechs_info
