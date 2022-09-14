# -*- coding: utf-8 -*-
#
# base_reference_converter.py
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

from typing import Union

from pynestml.codegeneration.printers.reference_converter import ReferenceConverter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.variable_symbol import VariableSymbol


class BaseReferenceConverter(ReferenceConverter):
    def convert_to_cpp_name(self, variable_name: str) -> str:
        """
        Converts a handed over name to the corresponding NEST/C++ naming guideline. This is chosen to be compatible with the naming strategy for ode-toolbox, such that the variable name in a NESTML statement like "G_ahp" += 1" will be converted into "G_ahp__d".
        :param variable_name: a single name.
        :return: the corresponding transformed name.
        """
        differential_order = variable_name.count("\"")
        if differential_order > 0:
            return variable_name.replace("\"", "").replace("$", "__DOLLAR") + "__" + "d" * differential_order

        return variable_name.replace("$", "__DOLLAR")

    def getter(self, variable_symbol: VariableSymbol) -> str:
        """
        Converts for a handed over symbol the corresponding name of the getter to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding representation as a string
        """
        return 'get_' + self.convert_to_cpp_name(variable_symbol.get_symbol_name())

    def setter(self, variable_symbol: VariableSymbol) -> str:
        """
        Converts for a handed over symbol the corresponding name of the setter to a nest processable format.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding representation as a string
        """
        return 'set_' + self.convert_to_cpp_name(variable_symbol.get_symbol_name())

    def name(self, node: Union[VariableSymbol, ASTVariable]) -> str:
        """
        Returns for the handed over element the corresponding nest processable string.
        :param node: a single variable symbol or variable
        :type node: VariableSymbol or ASTVariable
        :return: the corresponding string representation
        """
        if isinstance(node, VariableSymbol):
            return self.convert_to_cpp_name(node.get_symbol_name())

        return self.convert_to_cpp_name(node.get_complete_name())
