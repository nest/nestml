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
from sympy.physics.units.prefixes import PREFIXES
from sympy.physics.units.quantities import Quantity
from sympy.physics.units.definitions import meter, kilogram, second, ampere, kelvin, mole, candela  # base units
from sympy.physics.units.definitions import radian, steradian, hertz, newton, pascal, joule, watt, coulomb, volt, farad
from sympy.physics.units.definitions import ohm, siemens, weber, tesla, henry, degree, lux
from sympy.physics.units.definitions import length, luminous_intensity, time, amount_of_substance
from pynestml.src.main.python.org.nestml.symbol_table.predefined.UnitType import UnitType
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL


class PredefinedUnits(object):
    """
    This class represents a collection of physical units. Units can be retrieved by means of getUnitIfExists(name).
    Attribute:
        __name2unit  Dict of all predefined units, map from name to unit object. Type: str -> UnitType
    """
    __name2unit = {}
    __prefixlessUnits = list()

    @classmethod
    def registerUnits(cls):
        """
        Registers all predefined units into th system.
        """
        # first store all base units and the derived units without the prefix in a list
        cls.__prefixlessUnits.append(meter)
        cls.__prefixlessUnits.append(kilogram)
        cls.__prefixlessUnits.append(second)
        cls.__prefixlessUnits.append(ampere)
        cls.__prefixlessUnits.append(kelvin)
        cls.__prefixlessUnits.append(mole)
        cls.__prefixlessUnits.append(candela)
        cls.__prefixlessUnits.append(radian)
        cls.__prefixlessUnits.append(steradian)
        cls.__prefixlessUnits.append(hertz)
        cls.__prefixlessUnits.append(newton)
        cls.__prefixlessUnits.append(pascal)
        cls.__prefixlessUnits.append(joule)
        cls.__prefixlessUnits.append(watt)
        cls.__prefixlessUnits.append(coulomb)
        cls.__prefixlessUnits.append(volt)
        cls.__prefixlessUnits.append(farad)
        cls.__prefixlessUnits.append(ohm)
        cls.__prefixlessUnits.append(siemens)
        cls.__prefixlessUnits.append(weber)
        cls.__prefixlessUnits.append(tesla)
        cls.__prefixlessUnits.append(henry)
        # cls.__prefixlessUnits.append(degree) # currently not required
        cls.__prefixlessUnits.append(lux)
        # the sympy system misses the following units:lumen, becquerel,gray,sievert,katal
        lumen = Quantity('lumen', luminous_intensity, candela, 'lm')
        becquerel = Quantity('becquerel', 1 / time, 1 / second, 'Bq')
        gray = Quantity('gray', (length ** 2) / (time ** 2), meter * meter / (second * second), 'Gy')
        sievert = Quantity('sievert', (length ** 2) / (time ** 2), meter * meter / (second * second), 'Sv')
        katal = Quantity('katal', amount_of_substance / time, mole / second, 'kat')
        cls.__prefixlessUnits.append(lumen)
        cls.__prefixlessUnits.append(becquerel)
        cls.__prefixlessUnits.append(gray)
        cls.__prefixlessUnits.append(sievert)
        cls.__prefixlessUnits.append(katal)
        # then generate all combinations with all prefixes
        for prefix in PREFIXES:
            for unit in cls.__prefixlessUnits:
                temp = Quantity(str(PREFIXES[prefix].name) + str(unit.name).title(), unit.dimension,
                                PREFIXES[prefix] * unit,
                                prefix + str(unit.abbrev))
                tempUnit = UnitType(_name=str(temp.abbrev), _unit=temp)
                cls.__name2unit[str(temp.abbrev)] = tempUnit
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
            '(PyNestML.SymbolTable.PredefinedUnits) No or wrong type of name provided (%s)!' %type(_name)
        if _name in cls.__name2unit.keys():
            return cls.__name2unit[_name]
        else:
            Logger.logAndPrintMessage('Unit does not exist (%s)' % _name, LOGGING_LEVEL.WARNING)
            return None

    @classmethod
    def registerUnit(cls, _unit=None):
        """
        Registers the handed over unit in the set of the predefined units.
        :param _unit: a single unit type.
        :type _unit: UnitType
        """
        if _unit.getName() is not cls.__name2unit.keys():
            cls.__name2unit[_unit.getName()] = _unit
        return

    @classmethod
    def getUnits(cls):
        """
        Returns the list of all currently defined units.
        :return: a list of all defined units.
        :rtype: list(UnitType)
        """
        return cls.__name2unit
