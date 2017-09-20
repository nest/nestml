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
from sympy.physics.units.quantities import Quantity


class UnitType(object):
    """
    This class is used to encapsulate the functionality of sympy in a new layer which provided additional functionality
    as required during context checks.
    
    Attributes:
        __name  The name of this unit. type: str
        __unit  The corresponding sympy unit. type: sympy.physics.unit.quantities.Quantity
    """
    __name = None
    __unit = None

    def __init__(self, _name=None, _unit=None):
        """
        Standard constructor.
        :param _name: the name of this unit.
        :type _name: str
        :param _unit: a single unit object from sympy.physics.unit
        :type _unit: Unit
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.UnitType) No or wrong type of name provided!'
        assert (_unit is not None and isinstance(_unit, Quantity)), \
            '(PyNestML.SymbolTable.UnitType) No or wrong type of unit provided!'
        self.__name = _name
        self.__unit = _unit

    def getName(self):
        """
        Returns the name of this unit.
        :return: the name of the unit.
        :rtype: str
        """
        return self.__name

    def getUnit(self):
        """
        Returns the sympy unit of this unit.
        :return: a single unit quantity
        :rtype: sympy.physics.unit.quantities.Quantity
        """
        return self.__unit
