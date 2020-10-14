# -*- coding: utf-8 -*-
#
# gsl_names_converter.py
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
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.symbols.variable_symbol import VariableSymbol


class GSLNamesConverter(object):
    """
    A GSL names converter as use to transform names to GNU Scientific Library.
    """

    @classmethod
    def array_index(cls, symbol):
        """
        Transforms the haded over symbol to a GSL processable format.
        :param symbol: a single variable symbol
        :type symbol: VariableSymbol
        :return: the corresponding string format
        :rtype: str
        """
        return 'State_::' + NestNamesConverter.convert_to_cpp_name(symbol.get_symbol_name())

    @classmethod
    def name(cls, symbol):
        """
        Transforms the given symbol to a format that can be processed by GSL.
        :param symbol: a single variable symbol
        :type symbol: VariableSymbol
        :return: the corresponding string format
        :rtype: str
        """
        if symbol.is_init_values() and not symbol.is_function:
            return 'ode_state[State_::' + NestNamesConverter.convert_to_cpp_name(symbol.get_symbol_name()) + ']'
        else:
            return NestNamesConverter.name(symbol)

    @classmethod
    def getter(cls, variable_symbol):
        """
        Converts for a handed over symbol the corresponding name of the getter to a gsl processable format.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        return NestNamesConverter.getter(variable_symbol)

    @classmethod
    def setter(cls, variable_symbol):
        """
        Converts for a handed over symbol the corresponding name of the setter to a gsl processable format.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        return NestNamesConverter.setter(variable_symbol)

    @classmethod
    def buffer_value(cls, variable_symbol):
        """
        Converts for a handed over symbol the corresponding name of the buffer to a gsl processable format.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        return NestNamesConverter.buffer_value(variable_symbol)

    @classmethod
    def convert_to_cpp_name(cls, variable_name):
        """
        Converts a handed over name to the corresponding gsl / c++ naming guideline.
        In concrete terms:
            Converts names of the form g_in'' to a compilable C++ identifier: __DDX_g_in
        :param variable_name: a single name.
        :type variable_name: str
        :return: the corresponding transformed name.
        :rtype: str
        """
        return NestNamesConverter.convert_to_cpp_name(variable_name)
