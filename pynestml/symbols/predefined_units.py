# -*- coding: utf-8 -*-
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
    """
    name2unit = None

    @classmethod
    def register_units(cls):
        """
        Registers all units in astropy.units (more specifically, from the si, cgs and astrophys submodules) as predefined units into NESTML.
        """
        # first store all base units and the derived units without the prefix in a list
        cls.name2unit = {}

        for unit_str in dir(u.si) + dir(u.cgs) + dir(u.astrophys):
            try:
                unit = eval("u." + unit_str)    # grab the unit object
            except BaseException:
                unit = None

            if issubclass(type(unit), u.core.UnitBase):
                for unit_name in unit.names:
                    temp_unit = UnitType(name=str(unit_name), unit=unit)
                    cls.name2unit[str(unit_name)] = temp_unit

    @classmethod
    def get_unit(cls, name):
        """
        Returns a single UnitType if the corresponding unit has been predefined.
        :param name: the name of a unit
        :type name: str
        :return: a single UnitType object, or None
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
