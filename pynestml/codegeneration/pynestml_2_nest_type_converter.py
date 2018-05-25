#
# pynestml_2_nest_type_converter.py
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
from pynestml.symbols.type_symbol import TypeSymbol


class PyNestml2NestTypeConverter(object):
    """
    This class contains a single operation as used to convert nestml types to nest centerpieces.
    """

    @classmethod
    def convert(cls, type_symbol):
        # type: (TypeSymbol) -> str
        """
        Converts the name of the type symbol to a corresponding nest representation.
        :param type_symbol: a single type symbol
        :type type_symbol: TypeSymbol
        :return: the corresponding string representation.
        :rtype: str
        """
        return type_symbol.nest_type
