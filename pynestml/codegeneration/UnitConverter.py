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
from astropy import units
from pynestml.utils.Messages import Messages
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


class UnitConverter(object):
    """
    Calculates the factor needed to convert a given unit to its
    NEST counterpart. I.e.: potentials are expressed as mV, consultancies as nS etc.
    """

    @classmethod
    def getFactor(cls, _unit):
        """
        Gives a factor for a given unit that transforms it to a "neuroscience" scale
        If the given unit is not listed as a neuroscience unit, the factor is 1
        :param _unit: an astropy unit
        :type _unit: IrreducibleUnit or Unit or CompositeUnit
        :return: a factor to that unit, converting it to "neuroscience" scales.
        :rtype float
        """
        assert isinstance(_unit, units.IrreducibleUnit) or isinstance(_unit, units.CompositeUnit) or \
               isinstance(_unit, units.Unit) or isinstance(_unit, units.PrefixUnit), \
            "UnitConverter: given parameter is not a unit (%s)!" % type(_unit)

        # check if it is dimensionless, thus only a prefix
        if _unit.physical_type == 'dimensionless':
            return _unit.si
        # otherwise check if it is one of the base units
        targetUnit = None
        if _unit.physical_type == 'electrical conductance':
            targetUnit = units.nS
        if _unit.physical_type == 'electrical resistance':
            targetUnit = units.Gohm
        if _unit.physical_type == 'time':
            targetUnit = units.ms
        if _unit.physical_type == 'electrical capacitance':
            targetUnit = units.pF
        if _unit.physical_type == 'electrical potential':
            targetUnit = units.mV
        if _unit.physical_type == 'electrical current':
            targetUnit = units.pA
        if targetUnit is not None:
            return (_unit / targetUnit).si.scale
        # this case means that we stuck in a recursive definition
        elif _unit == _unit.bases[0] and len(_unit.bases) == 1:
            if isinstance(_unit, units.PrefixUnit):
                prefixFactor = _unit.si.scale
                unitFactor = cls.getFactor(_unit.represents)
                return prefixFactor * unitFactor
            if isinstance(_unit, units.Unit):
                return cls.getFactor(_unit.represents)
            if isinstance(_unit, units.IrreducibleUnit):
                # TODO: this question is still open, what do we do with non-neuroscientific units,e.g., kg???
                code, message = Messages.getNotNeuroscienceUnitUsed(str(_unit))
                Logger.logMessage(_code=code, _logLevel=LOGGING_LEVEL.WARNING, _message=message)
                return 1

        # now if it is not a base unit, it has to be a combined one, e.g. s**2, decompose it
        factor = 1
        for i in range(0, len(_unit.bases)):
            factor *= cls.getFactor(_unit.bases[i]) ** _unit.powers[i]
        return factor
