# -*- coding: utf-8 -*-
#
# unit_converter.py
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

from typing import Dict, List, Mapping

import functools
from fractions import Fraction

import numpy as np
from astropy import units

from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.symbols.type_symbol import TypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol


class UnitConverter:
    r"""
    Base class for the system of physical units used by a particular target platform.

    In a NESTML model, variables are typed by physical quantity (e.g. ``V_m "voltage"``) and do not imply any particular unit; physical units only appear in literals (``-70 mV``), in continuous input port declarations (``I_stim pA <- continuous``) and implicitly in spiking input ports (1/s, the unit of a Dirac delta function). Generated code stores all physical values as plain numbers, in a fixed set of preferred units of the target platform; every unit in the model is converted to the preferred unit of the same physical dimension by the factor returned by :py:meth:`get_factor`.

    The preferred units are specified for a set of independent base quantities only (see ``PREFERRED_UNITS``, to be defined by each subclass); the preferred units of all other quantities follow from these, such that the system of units is coherent: a product or quotient of values in preferred units is again a value in preferred units, without any additional factor. For example, if current is in pA and voltage in mV, conductance (current / voltage) is in nS, capacitance (current * time / voltage) in pF, and resistance in GOhm.
    """

    #: Preferred units for a set of independent base quantities (the keys are names of physical quantities as known to ``PredefinedQuantities``). Together, the base quantities need to span all seven dimensions of the SI; for instance, voltage can take the place of the SI base quantity "mass". To be defined by subclasses.
    PREFERRED_UNITS: Mapping[str, units.UnitBase] = {}

    _SI_BASE_UNITS: List[units.UnitBase] = [units.m, units.kg, units.s, units.A, units.K, units.mol, units.cd]

    _base_matrix_inverse_cache: Dict[type, np.ndarray] = {}

    #: Named derived units that are used to print a preferred unit, if exactly equal (for instance, ``nS`` rather than ``pA / mV``)
    _NAMED_DERIVED_UNITS: List[str] = ["S", "F", "Ohm", "C", "H", "Wb", "T", "N", "J", "W", "Pa"]
    _PREFIXES: List[str] = ["", "Y", "Z", "E", "P", "T", "G", "M", "k", "h", "da", "d", "c", "m", "u", "n", "p", "f", "a", "z", "y"]

    @classmethod
    def get_si_exponents(cls, unit: units.UnitBase) -> np.ndarray:
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
    def get_base_matrix_inverse(cls) -> np.ndarray:
        r"""
        Returns the inverse of the matrix :math:`B` whose columns are the physical dimensions of the base quantities in ``PREFERRED_UNITS``, expressed in terms of the SI base dimensions. This matrix is used by :py:meth:`get_preferred_unit` to express any physical dimension in terms of the base quantities.

        **Physical dimensions as vectors.** Any physical dimension can be written as a product of integer (or rational) powers of the seven SI base units, in the order of ``_SI_BASE_UNITS``: metre, kilogram, second, ampere, kelvin, mole and candela,

        .. math::

           \mathrm{m}^{v_1} \, \mathrm{kg}^{v_2} \, \mathrm{s}^{v_3} \, \mathrm{A}^{v_4} \, \mathrm{K}^{v_5} \, \mathrm{mol}^{v_6} \, \mathrm{cd}^{v_7}

        and can thus be represented by the vector of exponents :math:`\mathbf{v} = (v_1, \ldots, v_7)^T \in \mathbb{Q}^7` (see :py:meth:`get_si_exponents`). For example, volt and siemens are

        .. math::

           \mathrm{V} = \mathrm{m}^2 \, \mathrm{kg} \, \mathrm{s}^{-3} \, \mathrm{A}^{-1} \quad\rightarrow\quad \mathbf{v}_\mathrm{V} = (2, 1, -3, -1, 0, 0, 0)^T

           \mathrm{S} = \mathrm{m}^{-2} \, \mathrm{kg}^{-1} \, \mathrm{s}^{3} \, \mathrm{A}^{2} \quad\rightarrow\quad \mathbf{v}_\mathrm{S} = (-2, -1, 3, 2, 0, 0, 0)^T

        In this representation, multiplying two units corresponds to adding their vectors, and raising a unit to a power :math:`p` corresponds to multiplying its vector by :math:`p`. Physical dimensions thus form a vector space, and the magnitude of a unit (for instance, the factor :math:`10^{-3}` in mV compared to V) plays no role in it.

        **A different basis.** The SI base dimensions are only one possible basis of this vector space. The base quantities listed in ``PREFERRED_UNITS`` form another basis: for example, time, voltage, current, length, amount of substance, temperature and luminous intensity, where voltage takes the place of mass. Writing the dimension vectors of these base quantities as the columns :math:`\mathbf{b}_1, \ldots, \mathbf{b}_7` of a matrix (in the order of ``PREFERRED_UNITS``) gives

        .. math::

           B = \begin{pmatrix} \mathbf{b}_1 & \cdots & \mathbf{b}_7 \end{pmatrix} =
           \begin{pmatrix}
               0 &  2 & 0 & 1 & 0 & 0 & 0 \\
               0 &  1 & 0 & 0 & 0 & 0 & 0 \\
               1 & -3 & 0 & 0 & 0 & 0 & 0 \\
               0 & -1 & 1 & 0 & 0 & 0 & 0 \\
               0 &  0 & 0 & 0 & 0 & 1 & 0 \\
               0 &  0 & 0 & 0 & 1 & 0 & 0 \\
               0 &  0 & 0 & 0 & 0 & 0 & 1
           \end{pmatrix}

        where the rows correspond to m, kg, s, A, K, mol and cd, and the columns to time, voltage, current, length, amount of substance, temperature and luminous intensity. Note that :math:`B` only depends on *which* quantities are chosen as base quantities, not on their preferred units: the same matrix results for NEST (ms, mV, pA, ...) as for SI (s, V, A, ...).

        **Change of basis.** Expressing a dimension :math:`\mathbf{v}` in terms of the base quantities means finding exponents :math:`\mathbf{x} = (x_1, \ldots, x_7)^T` such that :math:`\mathbf{v} = \sum_i x_i \mathbf{b}_i`, that is,

        .. math::

           B \mathbf{x} = \mathbf{v} \quad\Leftrightarrow\quad \mathbf{x} = B^{-1} \mathbf{v}

        The preferred unit of dimension :math:`\mathbf{v}` is then the product :math:`\prod_i u_i^{x_i}`, where :math:`u_i` is the preferred unit of the :math:`i`-th base quantity. For conductance, :math:`B^{-1} \mathbf{v}_\mathrm{S} = (0, -1, 1, 0, 0, 0, 0)^T`, that is, conductance is current per voltage, and its preferred unit is :math:`\mathrm{pA}/\mathrm{mV} = \mathrm{nS}` for NEST, and :math:`\mathrm{A}/\mathrm{V} = \mathrm{S}` for SI. Similarly, mass becomes :math:`\mathbf{x} = (3, 1, 1, -2, 0, 0, 0)^T`, that is, :math:`\mathrm{kg} = \mathrm{V} \, \mathrm{A} \, \mathrm{s}^3 \, \mathrm{m}^{-2}`.

        Because every preferred unit is constructed from the same :math:`u_i`, the resulting system of units is coherent: if :math:`\mathbf{x}` and :math:`\mathbf{y}` are the exponents for two dimensions, the exponents for their product are :math:`\mathbf{x} + \mathbf{y}` (by linearity of :math:`B^{-1}`), so the product of two values in preferred units is again a value in the preferred unit of the product, without any additional factor.

        **Requirements.** :math:`B` is invertible if and only if the base quantities are linearly independent and span all seven SI dimensions; in other words, if every physical dimension can be expressed uniquely in terms of them. This is checked with an assertion, which catches an inconsistent ``PREFERRED_UNITS`` table (for instance, one listing both voltage and mass, but not current). As :math:`B` has integer entries and (being a change of basis between dimension systems) typically has determinant :math:`\pm 1`, the entries of :math:`B^{-1}` are integers, and :math:`\mathbf{x}` is integer for integer :math:`\mathbf{v}` and rational for rational :math:`\mathbf{v}` (e.g. for :math:`\mathrm{ns}^{1/2}`). The floating-point result is rounded to a rational number in :py:meth:`get_preferred_unit`.

        **Caching.** :math:`B^{-1}` is computed once per subclass and cached in ``_base_matrix_inverse_cache``, as it only depends on the (constant) keys of ``PREFERRED_UNITS``.

        :return: the matrix :math:`B^{-1}`, of shape (7, 7)
        """
        if cls not in UnitConverter._base_matrix_inverse_cache:
            from pynestml.symbols.predefined_quantities import PredefinedQuantities
            assert cls.PREFERRED_UNITS, "No preferred units defined for " + cls.__name__
            base_dimensions = np.array([cls.get_si_exponents(PredefinedQuantities.get_unit(quantity)) for quantity in cls.PREFERRED_UNITS.keys()]).T
            assert base_dimensions.shape == (len(cls._SI_BASE_UNITS), len(cls._SI_BASE_UNITS)) and np.linalg.matrix_rank(base_dimensions) == len(cls._SI_BASE_UNITS), \
                "Preferred units of " + cls.__name__ + " must be given for a set of independent base quantities that span all SI dimensions"
            UnitConverter._base_matrix_inverse_cache[cls] = np.linalg.inv(base_dimensions)

        return UnitConverter._base_matrix_inverse_cache[cls]

    @classmethod
    def get_preferred_unit(cls, unit: units.UnitBase) -> units.UnitBase:
        r"""
        Returns the preferred unit for the physical dimension of the given unit; for instance, with voltage preferred in mV, for both ``V`` and ``mV`` this is ``mV``.

        :param unit: an astropy unit
        :return: the preferred unit of the same physical dimension
        """
        exponents = cls.get_base_matrix_inverse() @ cls.get_si_exponents(unit)
        preferred_unit = cls._non_base_part(unit)
        for preferred_base_unit, exponent in zip(cls.PREFERRED_UNITS.values(), exponents):
            exponent = Fraction(exponent).limit_denominator(1000)
            if exponent != 0:
                preferred_unit = preferred_unit * preferred_base_unit ** exponent

        return preferred_unit

    @classmethod
    def get_factor(cls, unit: units.UnitBase) -> float:
        """
        Returns the factor that converts a value in the given unit to the corresponding preferred unit; for instance, with voltage preferred in mV, 1000 for ``V`` and 1 for ``mV``. For dimensionless units, this is the magnitude of the unit; for instance, 1E-3 for ``mV/V``.

        :param unit: an astropy unit
        :return: the conversion factor
        """
        assert (isinstance(unit, units.IrreducibleUnit) or isinstance(unit, units.CompositeUnit)
                or isinstance(unit, units.Unit) or isinstance(unit, units.PrefixUnit)), \
            "UnitConverter: given parameter is not a unit (%s)!" % type(unit)

        factor = float(unit.to(cls.get_preferred_unit(unit)))

        # remove floating-point noise from the unit conversion (e.g. 1000000.0000000002 for uS**2/ms)
        return float("%.15g" % factor)

    @classmethod
    def get_factor_of_unit_type(cls, unit_type: ASTUnitType) -> float:
        r"""
        Returns the conversion factor (see :py:meth:`get_factor`) for the unit of a numeric literal, such as the ``mV`` in ``-70 mV``.
        """
        if unit_type.get_type_symbol() is not None and isinstance(unit_type.get_type_symbol(), UnitTypeSymbol):
            unit = unit_type.get_type_symbol().astropy_unit
        else:
            unit = units.Unit(str(unit_type))

        return cls.get_factor(unit)

    @classmethod
    def print_unit(cls, type_symbol: TypeSymbol) -> str:
        r"""
        Returns the unit in which values of the given type are stored by the target platform; for instance, ``mV`` for the quantity "voltage", if voltage is preferred in mV. For non-physical types, the name of the type is returned (e.g. ``real``).
        """
        if isinstance(type_symbol, UnitTypeSymbol):
            return cls._print_unit(cls.get_preferred_unit(type_symbol.astropy_unit))

        return type_symbol.print_symbol()

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def _print_unit(unit: units.UnitBase) -> str:
        r"""Print a unit, using a single named unit if one exists that is exactly equal (for instance, ``nS`` rather than ``pA / mV``)."""
        if len(unit.bases) > 1 or (len(unit.bases) == 1 and unit.powers[0] != 1):
            from pynestml.symbols.predefined_units import PredefinedUnits
            candidates = [prefix + name for name in UnitConverter._NAMED_DERIVED_UNITS for prefix in UnitConverter._PREFIXES
                          if PredefinedUnits.is_unit(prefix + name)
                          and PredefinedUnits.get_unit(prefix + name).get_unit().is_equivalent(unit)
                          and PredefinedUnits.get_unit(prefix + name).get_unit().to(unit) == 1.]
            if candidates:
                return min(candidates, key=lambda name: (len(name), name))

        return str(unit)
