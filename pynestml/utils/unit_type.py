# -*- coding: utf-8 -*-
#
# unit_type.py
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
from astropy.units.core import PrefixUnit, Unit, IrreducibleUnit, CompositeUnit
from astropy.units.quantity import Quantity


class UnitType(object):
    """
    This class is used to encapsulate the functionality of astropy.units in a new layer which provided additional functionality as required during context checks.

    :attr name: The name of this unit.
    :type name: str
    :attr unit: The corresponding astropy Unit.
    :type unit: astropy.units.core.Unit
    """

    def __init__(self, name, unit):
        """
        Standard constructor.
        :param name: the name of this unit.
        :type name: str
        :param unit: an astropy Unit object
        :type unit: astropy.units.core.Unit
        """
        assert isinstance(name, str), \
            '(PyNestML.SymbolTable.UnitType) No or wrong type of name provided (%s)!' % type(name)
        assert (isinstance(unit, Unit) or isinstance(unit, PrefixUnit)
                or isinstance(unit, IrreducibleUnit)
                or isinstance(unit, CompositeUnit)
                or isinstance(unit, Quantity)), \
            '(PyNestML.SymbolTable.UnitType) No or wrong type of unit provided (%s)!' % type(unit)
        self.name = name
        self.unit = unit
        return

    def get_name(self):
        """
        Returns the name of this unit.
        :return: the name of the unit.
        :rtype: str
        """
        return self.name

    def get_unit(self):
        """
        Returns the astropy unit of this unit.
        :return: the astropy unit
        :rtype: astropy.units.core.Unit
        """
        return self.unit

    def print_unit(self):
        """
        Returns a string representation of this unit symbol.
        :return: a string representation.
        :rtype: str
        """
        return str(self.get_unit())

    def equals(self, _obj=None):
        """
        Compares this to the handed object and checks if they are semantically equal.
        :param _obj: a single object
        :type _obj: object
        :return: True if equal, otherwise false.
        :rtype: bool
        """
        if not isinstance(_obj, UnitType):
            return False
        # defer comparison to astropy
        return self.get_name() == _obj.get_name() and self.get_unit() == _obj.get_unit()
