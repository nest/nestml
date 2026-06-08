# -*- coding: utf-8 -*-
#
# co_co_plan.py
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

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class CoCoPlan:
    run_compartmental_neuron_cocos: bool = False
    require_integrate_odes_call: bool = True

    def for_model(self, is_synapse_model: bool) -> "CoCoPlan":
        if is_synapse_model:
            return replace(self, run_compartmental_neuron_cocos=False)

        return self
