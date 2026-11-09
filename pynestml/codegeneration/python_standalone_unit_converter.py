# -*- coding: utf-8 -*-
#
# python_standalone_unit_converter.py
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

from typing import Mapping

from astropy import units

from pynestml.codegeneration.unit_converter import UnitConverter


class PythonStandaloneUnitConverter(UnitConverter):
    r"""
    The Python-standalone target stores all physical values as plain numbers in SI units, without prefixes: voltage in V, current in A, time in s, conductance in S, capacitance in F, and so on. For instance, a literal ``-70 mV`` is printed as ``-0.07`` in the generated code.
    """

    #: Preferred units for a set of independent base quantities: the SI base units (with voltage taking the place of mass, which is equivalent as the SI is coherent).
    PREFERRED_UNITS: Mapping[str, units.UnitBase] = {
        "time": units.s,
        "voltage": units.V,
        "current": units.A,
        "length": units.m,
        "amount of substance": units.mol,
        "temperature": units.K,
        "luminous intensity": units.cd,
    }
