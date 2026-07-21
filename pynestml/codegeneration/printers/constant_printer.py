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

    n_float_digits = 9    # number of digits to print for floating point numbers. Increasing this value makes things more precise, but can also encourage unhelpful rewrites like "1E-6" being rendered as "9.9999999999999995e-07"

    def print_constant(self, node: Union[str, float, int]) -> str:
        """
        Converts a single handed over constant.
        :param node: a constant.
        :return: the corresponding string representation
        """
        if isinstance(node, int):
            return str(node)

        if isinstance(node, float):
            return f"{node:#.{ConstantPrinter.n_float_digits}g}".rstrip("0")    # make sure decimal point is always included

        raise Exception("Cannot print constant (" + str(node) + ") of unknown type")
