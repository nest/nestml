#
# UnitConverter.py
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
from astropy import units as u



class UnitConverter(object):
    """
    Calculates the factor needed to convert a given unit to its
    NEST counterpart. I.e.: potentials are expressed as mV,
    conductances as nS etc.
    """

    def getFactor(self,_unit):
        """
        Gives a factor for a given unit that transforms it to a "neuroscience" scale
        If the given unit is not listed as a neuroscience unit, the factor is 1
        :param _unit: an astropy unit
        :return: a factor to that unit, converting it to "neuroscience" scales.
        """

        assert isinstance(_unit,u.IrreducibleUnit) or isinstance(_unit, u.CompositeUnit) or isinstance(_unit,u.Unit)\
        , "UnitConverter: given parameter is not a unit"

        targetUnit = None
        if(_unit.physical_type == "electrical conductance"):
            targetUnit = u.nS
        if (_unit.physical_type == "electrical resistance"):
            targetUnit = u.Gohm
        if (_unit.physical_type == "time"):
            targetUnit = u.ms
        if (_unit.physical_type == "electrical capacitance"):
            targetUnit = u.pF
        if (_unit.physical_type == "electrical potential"):
            targetUnit = u.mV
        if (_unit.physical_type == "electrical current"):
            targetUnit = u.pA

        if targetUnit is not None:
            return (_unit / targetUnit).si.scale
        return 1