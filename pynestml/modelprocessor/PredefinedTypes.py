#
# PredefinedTypes.py
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
from copy import copy

from astropy.units.core import CompositeUnit
from astropy.units.quantity import Quantity

from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.TypeSymbol import TypeSymbol
from pynestml.modelprocessor.UnitType import UnitType
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.Messages import Messages


class PredefinedTypes(object):
    """
    This class represents all types which are predefined in the system.
    
    Attributes:
        name2type     A dict from names of variables to the corresponding type symbols. Type: dict(str->TypeSymbol)
        REAL_TYPE     The identifier of the type 'real'. Type: str
        VOID_TYPE     The identifier of the type 'void'. Type: str
        BOOLEAN_TYPE  The identifier of the type 'boolean'. Type: str
        STRING_TYPE   The identifier of the type 'string'. Type: str
        INTEGER_TYPE  The identifier of the type 'integer'. Type: str
    """
    name2type = {}
    REAL_TYPE = 'real'
    VOID_TYPE = 'void'
    BOOLEAN_TYPE = 'boolean'
    STRING_TYPE = 'string'
    INTEGER_TYPE = 'integer'

    @classmethod
    def register_types(cls):
        """
        Adds a set of primitive and unit data types to the set of predefined types. It assures that those types are
        valid and can be used.
        """
        cls.name2type = {}
        cls.__register_units()
        cls.__register_real()
        cls.__register_void()
        cls.__register_boolean()
        cls.__register_string()
        cls.__register_integer()
        return

    @classmethod
    def __register_units(cls):
        """
        Adds all units as predefined type symbols to the list of available types.
        """
        from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
        units = PredefinedUnits.get_units()
        for unitName in units.keys():
            t_symbol = TypeSymbol(element_reference=None, name=unitName,
                                  unit=units[unitName], is_integer=False, is_real=False, is_void=False,
                                  is_boolean=False, is_string=False, is_buffer=False)
            cls.name2type[unitName] = t_symbol
        return

    @classmethod
    def __register_real(cls):
        """
        Adds the real type symbol to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.REAL_TYPE, is_real=True)
        cls.name2type[cls.REAL_TYPE] = symbol
        return

    @classmethod
    def __register_void(cls):
        """
        Adds the void type to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.VOID_TYPE, is_void=True)
        cls.name2type[cls.VOID_TYPE] = symbol
        return

    @classmethod
    def __register_boolean(cls):
        """
        Adds the boolean type to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.BOOLEAN_TYPE, is_boolean=True)
        cls.name2type[cls.BOOLEAN_TYPE] = symbol
        return

    @classmethod
    def __register_string(cls):
        """
        Adds the string type to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.STRING_TYPE, is_string=True)
        cls.name2type[cls.STRING_TYPE] = symbol
        return

    @classmethod
    def __register_integer(cls):
        """
        Adds the integer type to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.INTEGER_TYPE, is_integer=True)
        cls.name2type[cls.INTEGER_TYPE] = symbol
        return

    @classmethod
    def get_types(cls):
        """
        Returns the list of all predefined types.
        :return: a copy of a list of all predefined types.
        :rtype: copy(list(TypeSymbol)
        """
        return copy(cls.name2type)

    @classmethod
    def get_type(cls, name):
        """
        Returns the symbol corresponding to the handed over name.
        :param name: the name of a symbol
        :type name: str
        :return: a copy of a TypeSymbol
        :rtype: copy(TypeSymbol)
        """
        typ_e = cls.get_type_if_exists(name)
        if typ_e is not None:
            return typ_e
        else:
            raise RuntimeError(
                '(PyNestML.SymbolTable.PredefinedTypes) Cannot resolve the predefined type: ' + name)

    @classmethod
    def get_type_if_exists(cls, name):
        """
        Return a TypeSymbol for
        -registered types
        -Correct SI Units in name ("ms")
        -Correct Serializations of a UnitRepresentation

        In Case of UNITS always return a TS with serialization as name
        :param name: the name of the symbol. 
        :type name: str or unit
        :return: a single symbol copy or none
        :rtype: TypeSymbol or None
        """
        # this case deals with something like 1.0 if we have (1/ms) * ms
        if isinstance(name, Quantity) and name.unit == '':
            if name.value == 1.0 or name.value == 1:
                # in this case its only the factor 1, thus not a
                # real scalar or anything, thus return the simple real type
                return cls.get_real_type()
            else:
                # otherwise its a prefix, store it as such
                cls.register_unit(name)
                return cls.get_type_if_exists(str(name))
        # this case deals with something like 1.0 if we have (ms/ms)
        if isinstance(name, CompositeUnit) and len(name.bases) == 0:
            return cls.get_real_type()
        if isinstance(name, CompositeUnit):
            cls.register_unit(name)
            return cls.get_type_if_exists(str(name))
        if isinstance(name, Quantity):
            cls.register_unit(name.unit)
            return cls.get_type_if_exists(str(name.unit))
        if name in cls.name2type:
            return copy(cls.name2type[name])
        else:
            return

    @classmethod
    def get_real_type(cls):
        """
        Returns a copy of the type symbol of type real.
        :return: a real symbol.
        :rtype: TypeSymbol
        """
        return copy(cls.name2type[cls.REAL_TYPE])

    @classmethod
    def get_void_type(cls):
        """
        Returns a copy of the type symbol of type void.
        :return: a void symbol.
        :rtype: TypeSymbol
        """
        return copy(cls.name2type[cls.VOID_TYPE])

    @classmethod
    def get_boolean_type(cls):
        """
        Returns a copy of the type symbol of type boolean.
        :return: a boolean symbol.
        :rtype: TypeSymbol
        """
        return copy(cls.name2type[cls.BOOLEAN_TYPE])

    @classmethod
    def get_string_type(cls):
        """
        Returns a copy of the type symbol of type string.
        :return: a new string symbol.
        :rtype: TypeSymbol 
        """
        return copy(cls.name2type[cls.STRING_TYPE])

    @classmethod
    def get_integer_type(cls):
        """
        Returns a new type symbol of type integer.
        :return: a new integer symbol.
        :rtype: TypeSymbol
        """
        return copy(cls.name2type[cls.INTEGER_TYPE])

    @classmethod
    def register_type(cls, symbol):
        """
        Registers a new type into the system.
        :param: a single type symbol.
        :type: TypeSymbol
        """
        if not symbol.is_primitive() and symbol.get_unit().get_name() not in cls.name2type.keys():
            cls.name2type[symbol.get_unit().get_name()] = symbol
            code, message = Messages.getNewTypeRegistered(symbol.get_unit().get_name())
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.INFO)

    @classmethod
    def register_unit(cls, unit):
        """
        Registers a new sympy unit into the system
        :param unit: a sympy unit.
        :type unit: SympyUnit
        """
        unit_type = UnitType(str(unit), unit)
        PredefinedUnits.register_unit(unit_type)
        type_symbol = TypeSymbol(name=unit_type.get_name(), unit=unit_type)
        PredefinedTypes.register_type(type_symbol)
