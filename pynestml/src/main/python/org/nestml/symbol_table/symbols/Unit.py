#
# Archetype.py
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


class Unit:
    """
    This class is used to represent a single physical unit consisting of the seven SI base units.
    
    Attributes:
        __name                      The name of the unit, e.g. mV. Type: str
        __LENGTH                    The exponent of the dimension length. Type: int
        __MASS                      The exponent of the dimension mass. Type: int
        __TIME                      The exponent of the dimension time. Type: int
        __ELECTRIC_CURRENT          The exponent of the dimension electric current. Type: int
        __THERMODYNAMIC_TEMPERATURE The exponent of the dimension thermodynamic temperature. Type: int
        __AMOUNT_OF_SUBSTANCE       The exponent of the dimension amount of substance. Type: int
        __LUMINOUS_INTENSITY        The exponent of the dimension luminous intensity. Type: int
    """
    __name = None
    __LENGTH = None
    __MASS = None
    __TIME = None
    __ELECTRIC_CURRENT = None
    __THERMODYNAMIC_TEMPERATURE = None
    __AMOUNT_OF_SUBSTANCE = None
    __LUMINOUS_INTENSITY = None

    def __init__(self, _name=None, _length=None, _mass=None, _time=None, _electricCurrent=None,
                 _thermodynamicTemperature=None,
                 _amountOfSubstance=None,
                 _luminousIntensity=None):
        """
        Standard construcotr.
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Unit) No or wrong type of name provided!'
        assert (_length is not None and isinstance(_length, int)), \
            '(PyNestML.SymbolTable.Unit) No or wrong type of "length" dimension provided!'
        assert (_mass is not None and isinstance(_mass, int)), \
            '(PyNestML.SymbolTable.Unit) No or wrong type of "mass" dimension provided!'
        assert (_time is not None and isinstance(_time, int)), \
            '(PyNestML.SymbolTable.Unit) No or wrong type of "time" dimension provided!'
        assert (_electricCurrent is not None and isinstance(_electricCurrent, int)), \
            '(PyNestML.SymbolTable.Unit) No or wrong type of "electric current" dimension provided!'
        assert (_thermodynamicTemperature is not None and isinstance(_thermodynamicTemperature, int)), \
            '(PyNestML.SymbolTable.Unit) No or wrong type of "thermodynamic temperature" dimension provided!'
        assert (_amountOfSubstance is not None and isinstance(_amountOfSubstance, int)), \
            '(PyNestML.SymbolTable.Unit) No or wrong type of "amount of substance" dimension provided!'
        assert (_luminousIntensity is not None and isinstance(_luminousIntensity, int)), \
            '(PyNestML.SymbolTable.Unit) No or wrong type of "luminous intensity" dimension provided!'
        self.__name = _name
        self.__LENGTH = _length
        self.__MASS = _mass
        self.__TIME = _time
        self.__ELECTRIC_CURRENT = _electricCurrent
        self.__THERMODYNAMIC_TEMPERATURE = _thermodynamicTemperature
        self.__AMOUNT_OF_SUBSTANCE = _amountOfSubstance
        self.__LUMINOUS_INTENSITY = _luminousIntensity

    def getName(self):
        """
        Returns the name of the physical unit.
        :return: the name of the unit.
        :rtype: str
        """
        return self.__name

    def getLengthExponent(self):
        """
        Returns the exponent of the length dimension.
        :return: exponent of the length dimension.
        :rtype: int
        """
        return self.__LENGTH

    def getMassExponent(self):
        """
        Returns the exponent of the mass dimension.
        :return: exponent of the mass dimension.
        :rtype: int
        """
        return self.__MASS

    def getTimeExponent(self):
        """
        Returns the exponent of the time dimension.
        :return: exponent of the time dimension.
        :rtype: int
        """
        return self.__TIME

    def getElectricCurrentExponent(self):
        """
        Returns the exponent of the electric current dimension.
        :return: exponent of the electric current dimension.
        :rtype: int
        """
        return self.__ELECTRIC_CURRENT

    def getThermodynamicTemperatureExponent(self):
        """
        Returns the exponent of the thermodynamic temperature dimension.
        :return: exponent of the thermodynamic temperature dimension.
        :rtype: int
        """
        return self.__THERMODYNAMIC_TEMPERATURE

    def getAmountOfSubstanceExponent(self):
        """
        Returns the exponent of the amount of substance dimension.
        :return: exponent of the amount of substance dimension.
        :rtype: int
        """
        return self.__AMOUNT_OF_SUBSTANCE

    def getLuminousIntensity(self):
        """
        Returns the exponent of the luminous intensity dimension.
        :return: exponent of the luminous intensity  dimension.
        :rtype: int
        """
        return self.__LUMINOUS_INTENSITY
