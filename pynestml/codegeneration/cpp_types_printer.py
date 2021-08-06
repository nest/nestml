# -*- coding: utf-8 -*-
#
# cpp_types_printer.py
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

from typing import Tuple

from pynestml.codegeneration.types_printer import TypesPrinter


class CppTypesPrinter(TypesPrinter):
    """
    Returns a C++ syntax version of the handed over element.
    """

    @classmethod
    def pretty_print(cls, element):
        if isinstance(element, bool) and element:
            return 'true'

        if isinstance(element, bool) and not element:
            return 'false'

        if isinstance(element, int):
            return str(element)

        if isinstance(element, float):
            return "{0:E}".format(element)

        if isinstance(element, str):
            return element

        raise Exception("Tried to print unknown type: " + str(type(element)) + " (string representation: " + str(element) + ")")
