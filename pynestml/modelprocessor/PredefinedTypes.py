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
from astropy.units.core import CompositeUnit
from astropy.units.quantity import Quantity
from pynestml.modelprocessor.TypeSymbol import TypeSymbol
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.modelprocessor.UnitType import UnitType
from copy import copy


class PredefinedTypes(object):
    """
    This class represents all types which are predefined in the system.
    
    Attributes:
        __name2type     A dict from names of variables to the corresponding type symbols. Type: dict(str->TypeSymbol)
        __REAL_TYPE     The identifier of the type 'real'. Type: str
        __VOID_TYPE     The identifier of the type 'void'. Type: str
        __BOOLEAN_TYPE  The identifier of the type 'boolean'. Type: str
        __STRING_TYPE   The identifier of the type 'string'. Type: str
        __INTEGER_TYPE  The identifier of the type 'integer'. Type: str
    """
    __name2type = {}
    __REAL_TYPE = 'real'
    __VOID_TYPE = 'void'
    __BOOLEAN_TYPE = 'boolean'
    __STRING_TYPE = 'string'
    __INTEGER_TYPE = 'integer'

    @classmethod
    def registerTypes(cls):
        """
        Adds a set of primitive and unit data types to the set of predefined types. It assures that those types are
        valid and can be used.
        """
        cls.__name2type = {}
        cls.__registerUnits()
        cls.__registerReal()
        cls.__registerVoid()
        cls.__registerBoolean()
        cls.__registerString()
        cls.__registerInteger()
        return

    @classmethod
    def __registerUnits(cls):
        """
        Adds all units as predefined type symbols to the list of available types.
        """
        from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
        units = PredefinedUnits.getUnits()
        for unitName in units.keys():
            tSymbol = TypeSymbol(element_reference=None, name=unitName,
                                 unit=units[unitName], is_integer=False, is_real=False, is_void=False,
                                 is_boolean=False, is_string=False, is_buffer=False)
            cls.__name2type[unitName] = tSymbol
        return

    @classmethod
    def __registerReal(cls):
        """
        Adds the real type symbol to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.__REAL_TYPE, is_real=True)
        cls.__name2type[cls.__REAL_TYPE] = symbol
        return

    @classmethod
    def __registerVoid(cls):
        """
        Adds the void type to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.__VOID_TYPE, is_void=True)
        cls.__name2type[cls.__VOID_TYPE] = symbol
        return

    @classmethod
    def __registerBoolean(cls):
        """
        Adds the boolean type to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.__BOOLEAN_TYPE, is_boolean=True)
        cls.__name2type[cls.__BOOLEAN_TYPE] = symbol
        return

    @classmethod
    def __registerString(cls):
        """
        Adds the string type to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.__STRING_TYPE, is_string=True)
        cls.__name2type[cls.__STRING_TYPE] = symbol
        return

    @classmethod
    def __registerInteger(cls):
        """
        Adds the integer type to the dict of predefined types.
        """
        symbol = TypeSymbol(name=cls.__INTEGER_TYPE, is_integer=True)
        cls.__name2type[cls.__INTEGER_TYPE] = symbol
        return

    @classmethod
    def getTypes(cls):
        """
        Returns the list of all predefined types.
        :return: a copy of a list of all predefined types.
        :rtype: copy(list(TypeSymbol)
        """
        return copy(cls.__name2type)

    @classmethod
    def getType(cls, _name=None):
        """
        Returns the symbol corresponding to the handed over name.
        :param _name: the name of a symbol
        :type _name: str
        :return: a copy of a TypeSymbol
        :rtype: copy(TypeSymbol)
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.PredefinedTypes) No or wrong type of name provided (%s)!' % (type(_name))
        typE = cls.getTypeIfExists(_name)
        if typE is not None:
            return typE
        else:
            raise RuntimeException(
                '(PyNestML.SymbolTable.PredefinedTypes) Cannot resolve the predefined type: ' + _name)

    @classmethod
    def getTypeIfExists(cls, _name=None):
        """
        Return a TypeSymbol for
        -registered types
        -Correct SI Units in name ("ms")
        -Correct Serializations of a UnitRepresentation

        In Case of UNITS always return a TS with serialization as name
        :param _name: the name of the symbol. 
        :type _name: str or unit
        :return: a single symbol copy or none
        :rtype: TypeSymbol or None
        """
        assert (_name is not None and (isinstance(_name, str) or isinstance(_name, CompositeUnit)
                                       or isinstance(_name, Quantity))), \
            '(PyNestML.SymbolTable.PredefinedTypes) No or wrong type of name provided (%s)!' % (type(_name))
        # this case deals with something like 1.0 if we have (1/ms) * ms
        if isinstance(_name, Quantity) and _name.unit == '':
            if _name.value == 1.0 or _name.value == 1:
                # in this case its only the factor 1, thus not a
                # real scalar or anything, thus return the simple real type
                return cls.getRealType()
            else:
                # otherwise its a prefix, store it as such
                cls.registerUnit(_name)
                return cls.getTypeIfExists(str(_name))
        # this case deals with something like 1.0 if we have (ms/ms)
        if isinstance(_name, CompositeUnit) and len(_name.bases) == 0:
            return cls.getRealType()
        if isinstance(_name, CompositeUnit):
            cls.registerUnit(_name)
            return cls.getTypeIfExists(str(_name))
        if isinstance(_name, Quantity):
            cls.registerUnit(_name.unit)
            return cls.getTypeIfExists(str(_name.unit))
        if _name in cls.__name2type:
            return copy(cls.__name2type[_name])
        else:
            return

    @classmethod
    def getRealType(cls):
        """
        Returns a copy of the type symbol of type real.
        :return: a real symbol.
        :rtype: TypeSymbol
        """
        return copy(cls.__name2type[cls.__REAL_TYPE])

    @classmethod
    def getVoidType(cls):
        """
        Returns a copy of the type symbol of type void.
        :return: a void symbol.
        :rtype: TypeSymbol
        """
        return copy(cls.__name2type[cls.__VOID_TYPE])

    @classmethod
    def getBooleanType(cls):
        """
        Returns a copy of the type symbol of type boolean.
        :return: a boolean symbol.
        :rtype: TypeSymbol
        """
        return copy(cls.__name2type[cls.__BOOLEAN_TYPE])

    @classmethod
    def getStringType(cls):
        """
        Returns a copy of the type symbol of type string.
        :return: a new string symbol.
        :rtype: TypeSymbol 
        """
        return copy(cls.__name2type[cls.__STRING_TYPE])

    @classmethod
    def getIntegerType(cls):
        """
        Returns a new type symbol of type integer.
        :return: a new integer symbol.
        :rtype: TypeSymbol
        """
        return copy(cls.__name2type[cls.__INTEGER_TYPE])

    @classmethod
    def registerType(cls, _symbol=None):
        """
        Registers a new type into the system.
        :param: a single type symbol.
        :type: TypeSymbol
        """
        from pynestml.utils.Messages import Messages
        from pynestml.modelprocessor.TypeSymbol import TypeSymbol
        assert (_symbol is not None and isinstance(_symbol, TypeSymbol)), \
            '(PyNestML.SymbolTable.PredefinedTypes) No or wrong type of symbol provided (%s)!' % (type(_symbol))
        if not _symbol.is_primitive() and _symbol.get_unit().get_name() not in cls.__name2type.keys():
            cls.__name2type[_symbol.get_unit().get_name()] = _symbol
            code, message = Messages.getNewTypeRegistered(_symbol.get_unit().get_name())
            Logger.log_message(code=code, message=message, log_level=LoggingLevel.INFO)
        return

    @classmethod
    def registerUnit(cls, _unit=None):
        """
        Registers a new sympy unit into the system
        :param _unit: a sympy unit.
        :type _unit: SympyUnit
        """
        from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
        unitType = UnitType(str(_unit), _unit)
        PredefinedUnits.registerUnit(unitType)
        typeSymbol = TypeSymbol(name=unitType.get_name(), unit=unitType)
        PredefinedTypes.registerType(typeSymbol)
        return


class RuntimeException(Exception):
    """
    This exception is thrown whenever a general error occurs at runtime.
    """
    pass
