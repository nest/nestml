# -*- coding: utf-8 -*-
#
# function_symbol.py
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
from pynestml.symbols.symbol import Symbol, SymbolKind


class FunctionSymbol(Symbol):
    """
    This class is used to store a single function symbol, e.g. the definition of the function max.
    Attributes:
        param_types (list(TypeSymbol)): A list of the types of parameters.
        return_type (type_symbol): The type of the returned value.
        is_predefined (bool): Indicates whether this function predefined or not.
    """

    def __init__(self, name, param_types, return_type, element_reference, scope=None, is_predefined=False):
        """
        Standard constructor.
        :param name: the name of the function symbol.
        :type name: str
        :param param_types: a list of argument types.
        :type param_types: list(TypeSymbol)
        :param return_type: the return type of the function.
        :type return_type: Union(TypeSymbol,None)
        :param element_reference: a reference to the ASTFunction which corresponds to this symbol (if not predefined)
        :type element_reference: ast_function or None
        :param scope: a reference to the scope in which this symbol is defined in
        :type scope: Scope
        :param is_predefined: True, if this element is a predefined one, otherwise False.
        :type is_predefined: bool
        """
        super(FunctionSymbol, self).__init__(element_reference=element_reference, scope=scope,
                                             name=name, symbol_kind=SymbolKind.FUNCTION)
        self.param_types = param_types
        self.return_type = return_type
        self.is_predefined = is_predefined

    def print_symbol(self):
        """
        Returns a string representation of this symbol.
        """
        ret = 'FunctionSymbol[' + self.get_symbol_name() + ', Parameters = {'
        for arg in self.param_types:
            ret += arg.print_symbol()
            if self.param_types.index(arg) < len(
                    self.param_types) - 1:  # in the case that it is not the last arg, print also a comma
                ret += ','
        ret += '}, return type = ' + (self.get_return_type().print_symbol())
        ret += ', @['
        if self.get_referenced_object() is not None:
            ret += str(self.get_referenced_object().get_source_position())
        else:
            ret += 'predefined'
        ret += ']'
        return ret

    def get_return_type(self):
        """
        Returns the return type of this function symbol
        :return: a single type symbol.
        :rtype: type_symbol
        """
        return self.return_type

    def set_return_type(self, new_type):
        """
        Sets the return type to the handed over one.
        :param new_type: a single type symbol
        :type new_type: type_symbol
        """
        self.return_type = new_type

    def get_parameter_types(self):
        """
        Returns a list of all parameter types.
        :return: a list of parameter types.
        :rtype: list(TypeSymbol)
        """
        return self.param_types

    def add_parameter_type(self, new_type):
        """
        Adds the handed over type to the list of argument types.
        :param new_type: a single type symbol
        :type new_type: type_symbol
        """
        self.param_types.append(new_type)

    def equals(self, _other=None):
        """
        Compares the handed over instance of function symbol to this one and returns true, if the they are equal.
        :param _other: a different function symbol
        :type _other: FunctionSymbol
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, FunctionSymbol):
            return False
        if not self.name == _other.get_symbol_name():
            return False
        if not self.return_type.equals(_other.return_type):
            return False
        if len(self.param_types) != len(_other.get_parameter_types()):
            return False
        other_args = _other.get_parameter_types()
        for i in range(0, len(self.param_types)):
            if not self.param_types[i].equals(other_args[i]):
                return False
        return True
