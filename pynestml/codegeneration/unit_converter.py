# -*- coding: utf-8 -*-
#
# unit_converter.py
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
from astropy import units


class UnitConverter(object):
    """
    Calculates the factor needed to convert a given unit to its
    NEST counterpart. I.e.: potentials are expressed as mV, consultancies as nS etc.
    """

    @classmethod
    def get_factor(cls, unit):
        """
        Gives a factor for a given unit that transforms it to a "neuroscience" scale
        If the given unit is not listed as a neuroscience unit, the factor is 1
        :param unit: an astropy unit
        :type unit: IrreducibleUnit or Unit or CompositeUnit
        :return: a factor to that unit, converting it to "neuroscience" scales.
        :rtype float
        """
        assert (isinstance(unit, units.IrreducibleUnit) or isinstance(unit, units.CompositeUnit)
                or isinstance(unit, units.Unit) or isinstance(unit, units.PrefixUnit)), \
            "UnitConverter: given parameter is not a unit (%s)!" % type(unit)

        # check if it is dimensionless, thus only a prefix
        if unit.physical_type == 'dimensionless':
            return unit.si
        # otherwise check if it is one of the base units
        target_unit = None
        if unit.physical_type == 'electrical conductance':
            target_unit = units.nS
        if unit.physical_type == 'electrical resistance':
            target_unit = units.Gohm
        if unit.physical_type == 'time':
            target_unit = units.ms
        if unit.physical_type == 'electrical capacitance':
            target_unit = units.pF
        if unit.physical_type == 'electrical potential':
            target_unit = units.mV
        if unit.physical_type == 'electrical current':
            target_unit = units.pA
        if target_unit is not None:
            return (unit / target_unit).si.scale
        # this case means that we stuck in a recursive definition
        elif unit == unit.bases[0] and len(unit.bases) == 1:
            # just return the factor 1.0
            return 1.0

        # now if it is not a base unit, it has to be a combined one, e.g. s**2, decompose it
        factor = 1.0
        for i in range(0, len(unit.bases)):
            factor *= cls.get_factor(unit.bases[i]) ** unit.powers[i]
        return factor
