#
# PredefinedUnits.py
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
from pynestml.modelprocessor.UnitType import UnitType
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from astropy import units as u


class PredefinedUnits(object):
    """
    This class represents a collection of physical units. Units can be retrieved by means of getUnitIfExists(name).
    Attribute:
        __name2unit (dict):  Dict of all predefined units, map from name to unit object.
        __prefixlessUnits (list): A list of all units, stored without a prefix.
        __prefixes (list): A list of all available prefixes.
    """
    __name2unit = None
    __prefixlessUnits = None
    __prefixes = None

    @classmethod
    def registerUnits(cls):
        """
        Registers all predefined units into th system.
        """
        # first store all base units and the derived units without the prefix in a list
        cls.__name2unit = {}
        cls.__prefixlessUnits = list()
        cls.__prefixes = list()
        # first construct the prefix
        for prefix in u.si_prefixes:
            cls.__prefixes.append((prefix[0][0], prefix[1][0]))
        # now construct the prefix units
        cls.__prefixlessUnits.append(('m', 'meter'))
        cls.__prefixlessUnits.append(('g', 'gram'))
        cls.__prefixlessUnits.append(('s', 'second'))
        cls.__prefixlessUnits.append(('A', 'ampere'))
        cls.__prefixlessUnits.append(('K', 'Kelvin'))
        cls.__prefixlessUnits.append(('mol', 'mole'))
        cls.__prefixlessUnits.append(('cd', 'candela'))
        cls.__prefixlessUnits.append(('rad', 'radian'))
        cls.__prefixlessUnits.append(('st', 'steradian'))
        cls.__prefixlessUnits.append(('Hz', 'hertz'))
        cls.__prefixlessUnits.append(('N', 'newton'))
        cls.__prefixlessUnits.append(('Pa', 'Pascal'))
        cls.__prefixlessUnits.append(('J', 'Joule'))
        cls.__prefixlessUnits.append(('W', 'watt'))
        cls.__prefixlessUnits.append(('C', 'coulomb'))
        cls.__prefixlessUnits.append(('V', 'Volt'))
        cls.__prefixlessUnits.append(('F', 'farad'))
        cls.__prefixlessUnits.append(('Ohm', 'Ohm'))
        cls.__prefixlessUnits.append(('S', 'Siemens'))
        cls.__prefixlessUnits.append(('Wb', 'Weber'))
        cls.__prefixlessUnits.append(('T', 'Tesla'))
        cls.__prefixlessUnits.append(('H', 'Henry'))
        cls.__prefixlessUnits.append(('lx', 'lux'))
        cls.__prefixlessUnits.append(('lm', 'lumen'))
        # then generate all combinations with all prefixes
        for unit in cls.__prefixlessUnits:
            for prefix in cls.__prefixes:
                temp = eval(str('u.' + prefix[1] + unit[1]))
                tempUnit = UnitType(_name=str(prefix[0] + unit[0]), _unit=temp)
                cls.__name2unit[str(prefix[0] + unit[0])] = tempUnit
            # add also without the prefix, e.g., s for seconds
            tempUnit = UnitType(_name=str(unit[0]), _unit=eval(str('u.' + unit[1])))
            cls.__name2unit[str(unit[0])] = tempUnit
        # additionally four units are not directly defined, we define them by hand, Bq,Gy,Sv,kat
        Bq = u.def_unit(['Bq', 'Becquerel'], 1 / u.s)
        Gy = u.def_unit(['Gy', 'Gray'], (u.meter ** 2) / (u.s ** 2))
        Sv = u.def_unit(['Sv', 'Sievert'], (u.meter ** 2) / (u.s ** 2))
        kat = u.def_unit(['kat', 'Katal'], u.mol / u.s)
        for prefix in cls.__prefixes:
            cls.__name2unit[str(prefix[0] + str(Bq.name))] = UnitType(_name=str(prefix[0] + str(Bq.name)), _unit=Bq)
            cls.__name2unit[str(prefix[0] + str(Gy.name))] = UnitType(_name=str(prefix[0] + str(Gy.name)), _unit=Gy)
            cls.__name2unit[str(prefix[0] + str(Sv.name))] = UnitType(_name=str(prefix[0] + str(Sv.name)), _unit=Sv)
            cls.__name2unit[str(prefix[0] + str(kat.name))] = UnitType(_name=str(prefix[0] + str(kat.name)), _unit=kat)
        return

    @classmethod
    def getUnitIfExists(cls, _name=None):
        """
        Returns a single sympy unit symbol if the corresponding unit has been predefined.
        :param _name: the name of a unit
        :type _name: str
        :return: a single UnitType object.
        :rtype: UnitType
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.PredefinedUnits) No or wrong type of name provided (%s)!' % type(_name)
        if _name in cls.__name2unit.keys():
            return cls.__name2unit[_name]
        else:
            from pynestml.utils.Messages import Messages
            code, message = Messages.getUnitDoesNotExist(_name)
            Logger.logMessage(_code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR)
            return None

    @classmethod
    def isUnit(cls, _name=None):
        """
        Indicates whether the handed over name represents a stored unit.
        :param _name: a single name
        :type _name: str
        :return: True if unit name, otherwise False.
        :rtype: bool
        """
        return _name in cls.__name2unit.keys()

    @classmethod
    def registerUnit(cls, _unit=None):
        """
        Registers the handed over unit in the set of the predefined units.
        :param _unit: a single unit type.
        :type _unit: UnitType
        """
        assert (_unit is not None and isinstance(_unit, UnitType)), \
            '(PyNestML.SymbolTable.PredefinedUnits) No or wrong type of unit provided (%s)!' % type(_unit)
        if _unit.get_name() is not cls.__name2unit.keys():
            cls.__name2unit[_unit.get_name()] = _unit
        return

    @classmethod
    def getUnits(cls):
        """
        Returns the list of all currently defined units.
        :return: a list of all defined units.
        :rtype: list(UnitType)
        """
        return cls.__name2unit
