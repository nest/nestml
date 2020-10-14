# -*- coding: utf-8 -*-
#
# predefined_variables.py
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
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.variable_symbol import VariableSymbol, BlockType, VariableType


class PredefinedVariables(object):
    """
    This class is used to store all predefined variables as generally available.
    """
    name2variable = {}  # type: dict -> VariableSymbol
    E_CONSTANT = 'e'  # type: str
    TIME_CONSTANT = 't'  # type: str

    @classmethod
    def register_variables(cls):
        """
        Registers the predefined variables.
        """
        cls.name2variable = {}
        cls.__register_euler_constant()
        cls.__register_time_constant()

    @classmethod
    def __register_predefined_type_variables(cls):
        """
        Registers all predefined type variables, e.g., mV and integer.
        """
        for name in PredefinedTypes.get_types().keys():
            symbol = VariableSymbol(name=name, block_type=BlockType.PREDEFINED,
                                    is_predefined=True,
                                    type_symbol=PredefinedTypes.get_type(name),
                                    variable_type=VariableType.TYPE)
            cls.name2variable[name] = symbol
        return

    @classmethod
    def __register_euler_constant(cls):
        """
        Adds the euler constant e.
        """
        symbol = VariableSymbol(name='e', block_type=BlockType.STATE,
                                is_predefined=True, type_symbol=PredefinedTypes.get_real_type(),
                                variable_type=VariableType.VARIABLE)
        cls.name2variable[cls.E_CONSTANT] = symbol
        return

    @classmethod
    def __register_time_constant(cls):
        """
        Adds the time constant t.
        """
        symbol = VariableSymbol(name='t', block_type=BlockType.STATE,
                                is_predefined=True, type_symbol=PredefinedTypes.get_type('ms'),
                                variable_type=VariableType.VARIABLE)
        cls.name2variable[cls.TIME_CONSTANT] = symbol
        return

    @classmethod
    def get_time_constant(cls):
        """
        Returns a copy of the variable symbol representing the time constant t.
        :return: a variable symbol.
        :rtype: VariableSymbol
        """
        return cls.name2variable[cls.TIME_CONSTANT]

    @classmethod
    def get_euler_constant(cls):
        """
        Returns a copy of the variable symbol representing the euler constant t.
        :return: a variable symbol.
        :rtype: VariableSymbol
        """
        return cls.name2variable[cls.E_CONSTANT]

    @classmethod
    def get_variable(cls, name):
        """
        Returns the variable symbol belonging to the handed over name if such an element exists.
        :param name: the name of a symbol.
        :type name: str
        :return: a variable symbol if one exists, otherwise none
        :rtype: None or VariableSymbol
        """
        if name in cls.name2variable.keys():
            return cls.name2variable[name]
        else:
            return None

    @classmethod
    def get_variables(cls):
        """
        Returns the list of all defined variables.
        :return: a list of variable symbols.
        :rtype: list(VariableSymbol)
        """
        return cls.name2variable
