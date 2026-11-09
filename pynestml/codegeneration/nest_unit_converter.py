# -*- coding: utf-8 -*-
#
# nest_unit_converter.py
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

from typing import List, Mapping

from fractions import Fraction

import numpy as np
from astropy import units


class NESTUnitConverter:
    r"""
    NEST Simulator stores all physical values as plain numbers, in a fixed set of preferred units: voltage in mV, current in pA, time in ms, and so on. This class holds those preferred units, and calculates the factor needed to convert a value given in any physical unit to the corresponding NEST unit.

    In a NESTML model, variables are typed by physical quantity (e.g. ``V_m "voltage"``) and do not imply any particular unit; physical units only appear in literals (``-70 mV``) and in continuous input port declarations (``I_stim pA <- continuous``). When generating code for NEST, every value is stored in its NEST unit, so each literal is converted by the factor returned by :py:meth:`get_factor`; for instance, ``1 V`` is printed as ``1000``.

    The preferred units are specified only for a set of independent base quantities (see ``PREFERRED_UNITS``); the preferred units of all other quantities follow from these, such that the system of units is coherent (a product or quotient of NEST values is again a NEST value, without any additional factor). For example, as current is in pA and voltage in mV, conductance is in pA/mV = nS, capacitance (current * time / voltage) is in pF, and resistance in GOhm.
    """

    #: Preferred units for a set of independent base quantities. Voltage takes the place of the SI base quantity "mass".
    PREFERRED_UNITS: Mapping[str, units.UnitBase] = {
        "time": units.ms,
        "voltage": units.mV,
        "current": units.pA,
        "length": units.m,
        "amount of substance": units.mol,
        "temperature": units.K,
        "luminous intensity": units.cd,
    }

    _SI_BASE_UNITS: List[units.UnitBase] = [units.m, units.kg, units.s, units.A, units.K, units.mol, units.cd]

    _base_matrix_inverse = None

    @classmethod
    def _si_exponents(cls, unit: units.UnitBase) -> np.ndarray:
        r"""Returns the exponents of the SI base units (in the order of ``_SI_BASE_UNITS``) of the dimension of ``unit``."""
        si_unit = units.Unit(unit).decompose()
        exponents = np.zeros(len(cls._SI_BASE_UNITS))
        for base, power in zip(si_unit.bases, si_unit.powers):
            for i, si_base in enumerate(cls._SI_BASE_UNITS):
                if base == si_base:
                    exponents[i] += float(power)
                    break

        return exponents

    @classmethod
    def _non_base_part(cls, unit: units.UnitBase) -> units.UnitBase:
        r"""Returns the part of the dimension of ``unit`` that is not expressed in SI base units (such as ``rad``); this part is carried over unchanged to the preferred unit."""
        si_unit = units.Unit(unit).decompose()
        non_base_part = units.dimensionless_unscaled
        for base, power in zip(si_unit.bases, si_unit.powers):
            if not any(base == si_base for si_base in cls._SI_BASE_UNITS):
                non_base_part = non_base_part * base ** power

        return non_base_part

    @classmethod
    def _get_base_matrix_inverse(cls) -> np.ndarray:
        if cls._base_matrix_inverse is None:
            from pynestml.symbols.predefined_quantities import PredefinedQuantities
            base_dimensions = np.array([cls._si_exponents(PredefinedQuantities.get_unit(quantity)) for quantity in cls.PREFERRED_UNITS.keys()]).T
            assert np.linalg.matrix_rank(base_dimensions) == len(cls._SI_BASE_UNITS), "Preferred units must be given for a set of independent base quantities"
            cls._base_matrix_inverse = np.linalg.inv(base_dimensions)

        return cls._base_matrix_inverse

    @classmethod
    def get_preferred_unit(cls, unit: units.UnitBase) -> units.UnitBase:
        r"""
        Returns the NEST unit for the physical dimension of the given unit; for instance, for ``V`` or ``mV``, this is ``mV``, and for ``uS`` this is ``nS``.

        :param unit: an astropy unit
        :return: the NEST unit of the same physical dimension
        """
        exponents = cls._get_base_matrix_inverse() @ cls._si_exponents(unit)
        preferred_unit = cls._non_base_part(unit)
        for preferred_base_unit, exponent in zip(cls.PREFERRED_UNITS.values(), exponents):
            exponent = Fraction(exponent).limit_denominator(1000)
            if exponent != 0:
                preferred_unit = preferred_unit * preferred_base_unit ** exponent

        return preferred_unit

    @classmethod
    def get_factor(cls, unit: units.UnitBase) -> float:
        """
        Returns the factor that converts a value in the given unit to the corresponding NEST unit; for instance, 1000 for ``V`` (as NEST uses mV), and 1 for ``mV``. For dimensionless units, this is the magnitude of the unit; for instance, 1E-3 for ``mV/V``.

        :param unit: an astropy unit
        :return: the conversion factor
        """
        assert (isinstance(unit, units.IrreducibleUnit) or isinstance(unit, units.CompositeUnit)
                or isinstance(unit, units.Unit) or isinstance(unit, units.PrefixUnit)), \
            "UnitConverter: given parameter is not a unit (%s)!" % type(unit)

        factor = float(unit.to(cls.get_preferred_unit(unit)))

        # remove floating-point noise from the unit conversion (e.g. 1000000.0000000002 for uS**2/ms)
        return float("%.15g" % factor)
