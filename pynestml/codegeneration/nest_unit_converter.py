# -*- coding: utf-8 -*-
#
# nest_unit_converter.py
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

from typing import List, Mapping

from astropy import units

from pynestml.codegeneration.unit_converter import UnitConverter


class NESTUnitConverter(UnitConverter):
    r"""
    NEST Simulator stores all physical values as plain numbers, in a fixed set of preferred units: voltage in mV, current in pA, time in ms, and, following from these, conductance in nS, capacitance in pF, resistance in GOhm, rates in 1/ms, and so on. For instance, a literal ``1 V`` is printed as ``1000`` in the generated code.

    Following the convention of NEST, rates (the quantity "1 / time") are exchanged with the user in Hz: when a parameter or state variable is set (e.g. ``neuron.firing_rate = 10.``, meaning 10 Hz), read (with ``get()``) or recorded, the generated code converts between Hz and the 1/ms in which the value is stored.
    """

    #: Preferred units for a set of independent base quantities. Voltage takes the place of the SI base quantity "mass".
    PREFERRED_UNITS: Mapping[str, units.UnitBase] = {
        "time": units.ms,
        "voltage": units.mV,
        "current": units.pA,
        "length": units.m,
        "amount of substance": units.mol,
        "temperature": units.K,
        "luminous intensity": units.cd,
    }

    #: Rates are set and read in Hz
    INTERFACE_UNITS: List[units.UnitBase] = [units.Hz]
