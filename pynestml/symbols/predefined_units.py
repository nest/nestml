#
# predefined_units.py
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

from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.unit_type import UnitType


class PredefinedUnits(object):
    """
    This class represents a collection of physical units. Units can be retrieved by means of get_unit(name).
    Attribute:
        name2unit (dict):  Dict of all predefined units, map from name to unit object.
        prefixless_units (list): A list of all units, stored without a prefix.
        prefixes (list): A list of all available prefixes.
    """
    name2unit = None
    prefixless_units = None
    prefixes = None

    @classmethod
    def register_units(cls):
        """
        Registers all predefined units into th system.
        """
        # first store all base units and the derived units without the prefix in a list
        cls.name2unit = {}
        cls.prefixless_units = list()
        cls.prefixes = list()
        # first construct the prefix
        for prefix in u.si_prefixes:
            cls.prefixes.append((prefix[0][0], prefix[1][0]))
        # now construct the prefix units
        cls.prefixless_units.append(('m', 'meter'))
        cls.prefixless_units.append(('g', 'gram'))
        cls.prefixless_units.append(('s', 'second'))
        cls.prefixless_units.append(('A', 'ampere'))
        cls.prefixless_units.append(('K', 'Kelvin'))
        cls.prefixless_units.append(('mol', 'mole'))
        cls.prefixless_units.append(('cd', 'candela'))
        cls.prefixless_units.append(('rad', 'radian'))
        cls.prefixless_units.append(('st', 'steradian'))
        cls.prefixless_units.append(('Hz', 'hertz'))
        cls.prefixless_units.append(('N', 'newton'))
        cls.prefixless_units.append(('Pa', 'Pascal'))
        cls.prefixless_units.append(('J', 'Joule'))
        cls.prefixless_units.append(('W', 'watt'))
        cls.prefixless_units.append(('C', 'coulomb'))
        cls.prefixless_units.append(('V', 'Volt'))
        cls.prefixless_units.append(('F', 'farad'))
        cls.prefixless_units.append(('Ohm', 'Ohm'))
        cls.prefixless_units.append(('S', 'Siemens'))
        cls.prefixless_units.append(('Wb', 'Weber'))
        cls.prefixless_units.append(('T', 'Tesla'))
        cls.prefixless_units.append(('H', 'Henry'))
        cls.prefixless_units.append(('lx', 'lux'))
        cls.prefixless_units.append(('lm', 'lumen'))
        # then generate all combinations with all prefixes
        for unit in cls.prefixless_units:
            for prefix in cls.prefixes:
                temp = eval(str('u.' + prefix[1] + unit[1]))
                temp_unit = UnitType(name=str(prefix[0] + unit[0]), unit=temp)
                cls.name2unit[str(prefix[0] + unit[0])] = temp_unit
            # add also without the prefix, e.g., s for seconds
            temp_unit = UnitType(name=str(unit[0]), unit=eval(str('u.' + unit[1])))
            cls.name2unit[str(unit[0])] = temp_unit
        # additionally four units are not directly defined, we define them by hand, Bq,Gy,Sv,kat
        bq = u.def_unit(['Bq', 'Becquerel'], 1 / u.s)
        gy = u.def_unit(['Gy', 'Gray'], (u.meter ** 2) / (u.s ** 2))
        sv = u.def_unit(['Sv', 'Sievert'], (u.meter ** 2) / (u.s ** 2))
        kat = u.def_unit(['kat', 'Katal'], u.mol / u.s)
        for prefix in cls.prefixes:
            cls.name2unit[str(prefix[0] + str(bq.name))] = UnitType(name=str(prefix[0] + str(bq.name)), unit=bq)
            cls.name2unit[str(prefix[0] + str(gy.name))] = UnitType(name=str(prefix[0] + str(gy.name)), unit=gy)
            cls.name2unit[str(prefix[0] + str(sv.name))] = UnitType(name=str(prefix[0] + str(sv.name)), unit=sv)
            cls.name2unit[str(prefix[0] + str(kat.name))] = UnitType(name=str(prefix[0] + str(kat.name)), unit=kat)
        return

    @classmethod
    def get_unit(cls, name):
        """
        Returns a single sympy unit symbol if the corresponding unit has been predefined.
        :param name: the name of a unit
        :type name: str
        :return: a single UnitType object.
        :rtype: UnitType
        """
        if name in cls.name2unit.keys():
            return cls.name2unit[name]
        else:
            code, message = Messages.get_unit_does_not_exist(name)
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.ERROR)
            return None

    @classmethod
    def is_unit(cls, name):
        """
        Indicates whether the handed over name represents a stored unit.
        :param name: a single name
        :type name: str
        :return: True if unit name, otherwise False.
        :rtype: bool
        """
        return name in cls.name2unit.keys()

    @classmethod
    def register_unit(cls, unit):
        """
        Registers the handed over unit in the set of the predefined units.
        :param unit: a single unit type.
        :type unit: UnitType
        """
        if unit.get_name() is not cls.name2unit.keys():
            cls.name2unit[unit.get_name()] = unit

    @classmethod
    def get_units(cls):
        """
        Returns the list of all currently defined units.
        :return: a list of all defined units.
        :rtype: list(UnitType)
        """
        return cls.name2unit
