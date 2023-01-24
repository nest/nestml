# -*- coding: utf-8 -*-
#
# constant_printer.py
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


class ConstantPrinter:
    r"""
    """

    def print_constant(self, const: Union[str, float, int]) -> str:
        """
        Converts a single handed over constant.
        :param constant_name: a constant as string.
        :type constant_name: str
        :return: the corresponding nest representation
        """
        if isinstance(const, float) or isinstance(const, int):
            return str(const)

        return const
