# -*- coding: utf-8 -*-
#
# nest_names_converter.py
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
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.variable_symbol import VariableSymbol


class NestNamesConverter(object):
    """
    This class provides several methods which can be used to convert names of objects to the corresponding
    nest representation.
    """

    @classmethod
    def name(cls, node):
        """
        Returns for the handed over element the corresponding nest processable string.
        :param node: a single variable symbol or variable
        :type node: VariableSymbol or ASTVariable
        :return: the corresponding string representation
        :rtype: str
        """
        if isinstance(node, VariableSymbol):
            return cls.convert_to_cpp_name(node.get_symbol_name())
        else:
            return cls.convert_to_cpp_name(node.get_complete_name())

    @classmethod
    def getter(cls, variable_symbol):
        """
        Converts for a handed over symbol the corresponding name of the getter to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        assert isinstance(variable_symbol, VariableSymbol), \
            '(PyNestML.CodeGeneration.NamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                variable_symbol)
        return 'get_' + cls.convert_to_cpp_name(variable_symbol.get_symbol_name())

    @classmethod
    def buffer_value(cls, variable_symbol):
        """
        Converts for a handed over symbol the corresponding name of the buffer to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        assert isinstance(variable_symbol, VariableSymbol), \
            '(PyNestML.CodeGeneration.NamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                variable_symbol)
        return variable_symbol.get_symbol_name() + '_grid_sum_'

    @classmethod
    def setter(cls, variable_symbol):
        """
        Converts for a handed over symbol the corresponding name of the setter to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :type variable_symbol: VariableSymbol
        :return: the corresponding representation as a string
        :rtype: str
        """
        assert isinstance(variable_symbol, VariableSymbol), \
            '(PyNestML.CodeGeneration.NamesConverter) No or wrong type of variable symbol provided (%s)!' % type(
                variable_symbol)
        return 'set_' + cls.convert_to_cpp_name(variable_symbol.get_symbol_name())

    @classmethod
    def convert_to_cpp_name(cls, variable_name):
        """
        Converts a handed over name to the corresponding NEST/C++ naming guideline. This is chosen to be compatible with the naming strategy for ode-toolbox, such that the variable name in a NESTML statement like "G_ahp' += 1" will be converted into "G_ahp__d".

        :param variable_name: a single name.
        :type variable_name: str
        :return: the corresponding transformed name.
        :rtype: str
        """
        differential_order = variable_name.count('\'')
        if differential_order > 0:
            return variable_name.replace('\'', '').replace("$", "__DOLLAR") + '__' + 'd' * differential_order
        else:
            return variable_name.replace("$", "__DOLLAR")
