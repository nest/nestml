# -*- coding: utf-8 -*-
#
# implicit_conversion_factor.py
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

from __future__ import annotations

from typing import Optional

import math


class ImplicitConversionFactor(float):
    r"""
    A factor that converts a value from one physical unit to another, for instance 1000 from V to mV. The value of the float is this factor.

    Generated code for NEST and for Python holds a numeric literal with a physical unit in a NEST unit (see NESTUnitConverter): for instance, it holds ``1 V`` as ``1000.``, its value in mV. The attribute ``nest_factor`` is the factor that applies to the values as generated code holds them. For instance, in ``V_m mV = 1 V``, the factor is 1000, but ``nest_factor`` is 1. If it is not known in which units generated code holds the values, ``nest_factor`` is equal to the factor.
    """

    def __new__(cls, factor: float, nest_factor: Optional[float] = None):
        instance = super().__new__(cls, factor)
        instance.nest_factor = factor if nest_factor is None else nest_factor
        return instance

    def __getnewargs__(self):
        return float(self), self.nest_factor

    @classmethod
    def from_held_unit_scales(cls, factor: float, source_scale: Optional[float], target_scale: Optional[float]) -> ImplicitConversionFactor:
        r"""
        Create a factor from the scales of the units in which generated code holds the value before and after the conversion (see NESTUnitConverter.get_held_unit_scale()).

        :param factor: the factor that converts the value from its physical unit to the target unit
        :param source_scale: the scale (in SI units) of the unit in which generated code holds the value, or None if it is not known
        :param target_scale: the scale (in SI units) of the unit in which generated code holds the converted value, or None if it is not known
        :return: the factor
        """
        if source_scale is None or target_scale is None:
            return cls(factor)

        nest_factor = source_scale / target_scale
        if math.isclose(nest_factor, 1.):
            nest_factor = 1.    # remove rounding errors, so that no factor is printed

        return cls(factor, nest_factor)

    @staticmethod
    def get_nest_factor(factor: Optional[float]) -> Optional[float]:
        r"""
        Gives the factor that applies to the values as generated code for NEST and for Python holds them.

        :param factor: an implicit conversion factor (see ASTNode.set_implicit_conversion_factor()), or None
        :return: ``factor.nest_factor`` if ``factor`` is an ImplicitConversionFactor, otherwise ``factor``
        """
        if isinstance(factor, ImplicitConversionFactor):
            return factor.nest_factor

        return factor
