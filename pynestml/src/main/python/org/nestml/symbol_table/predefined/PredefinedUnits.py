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
from sympy.physics.units.definitions import force, frequency, pressure, energy, power, charge, voltage, capacitance
from sympy.physics.units.definitions import impedance, conductance, magnetic_flux, magnetic_density
from sympy.physics.units.definitions import inductance, current, temperature
from sympy.physics.units.definitions import length, luminous_intensity, time, amount_of_substance, mass, kilo
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
        cls.__name2unit = {}
        cls.__prefixlessUnits = list()
        # rename name thus they can be used with upper case names
        meter = Quantity('Meter', length, 1, abbrev='m')
        kilogram = Quantity('Kilogram', mass, kilo, abbrev='g')
        second = Quantity('Second', time, 1, abbrev='s')
        ampere = Quantity('Ampere', current, 1, abbrev='A')
        kelvin = Quantity('Kelvin', temperature, 1, 'K')
        mole = Quantity('Mole', amount_of_substance, 1, 'mol')
        candela = Quantity('Candela', luminous_intensity, 1, 'cd')
        radian = Quantity('Radian', 1, 1)
        steradian = Quantity('Steradian', 1, 1, 'sr')
        hertz = Quantity('Hertz', frequency, 1, 'Hz')
        newton = Quantity('Newton', force, kilogram * meter / second ** 2, 'N')
        pascal = Quantity('Pascal', pressure, newton / meter ** 2, 'Pa')
        joule = Quantity('Joule', energy, newton * meter, 'J')
        watt = Quantity('Watt', power, joule / second, 'W')
        coulomb = Quantity('Coulomb', charge, 1, abbrev='C')
        volt = Quantity('Volt', voltage, joule / coulomb, abbrev='V')
        farad = Quantity('Farad', capacitance, coulomb / volt, abbrev='F')
        ohm = Quantity('Ohm', impedance, volt / ampere, abbrev='Ohm')
        siemens = Quantity('Siemens', conductance, ampere / volt, abbrev='S')
        weber = Quantity('Weber', magnetic_flux, joule / ampere, abbrev='Wb')
        tesla = Quantity('Tesla', magnetic_density, volt * second / meter ** 2, abbrev='T')
        henry =  Quantity('Henry', inductance, volt * second / ampere, abbrev='H')
        lux = Quantity('Lux', luminous_intensity / length ** 2, steradian * candela / meter ** 2,abbrev='lx')
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
        cls.__prefixlessUnits.append(lux)
        # the sympy system misses the following units:lumen, becquerel,gray,sievert,katal
        lumen = Quantity('Lumen', luminous_intensity, candela, 'lm')
        becquerel = Quantity('Becquerel', 1 / time, 1 / second, 'Bq')
        gray = Quantity('Gray', (length ** 2) / (time ** 2), meter * meter / (second * second), 'Gy')
        sievert = Quantity('Sievert', (length ** 2) / (time ** 2), meter * meter / (second * second), 'Sv')
        katal = Quantity('Katal', amount_of_substance / time, mole / second, 'kat')
        cls.__prefixlessUnits.append(lumen)
        cls.__prefixlessUnits.append(becquerel)
        cls.__prefixlessUnits.append(gray)
        cls.__prefixlessUnits.append(sievert)
        cls.__prefixlessUnits.append(katal)
        # then generate all combinations with all prefixes
        for unit in cls.__prefixlessUnits:
            for prefix in PREFIXES:
                temp = Quantity(str(PREFIXES[prefix].name) + str(unit.name).title(), unit.dimension,
                                PREFIXES[prefix] * unit,
                                prefix + str(unit.abbrev))
                tempUnit = UnitType(_name=str(temp.abbrev), _unit=temp)
                cls.__name2unit[str(temp.abbrev)] = tempUnit
            # add also without the prefix, e.g., s for seconds
            tempUnit = UnitType(_name=str(unit.abbrev), _unit=unit)
            cls.__name2unit[str(unit.abbrev)] = tempUnit
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
            Logger.logMessage('Unit does not exist (%s)' % _name, LOGGING_LEVEL.ERROR)
            return None

    @classmethod
    def registerUnit(cls, _unit=None):
        """
        Registers the handed over unit in the set of the predefined units.
        :param _unit: a single unit type.
        :type _unit: UnitType
        """
        assert (_unit is not None and isinstance(_unit, UnitType)), \
            '(PyNestML.SymbolTable.PredefinedUnits) No or wrong type of unit provided (%s)!' % type(_unit)
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
