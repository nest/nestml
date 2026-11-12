# -*- coding: utf-8 -*-
#
# test_unit_converter.py
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

import itertools
import pytest

from astropy import units as u

from pynestml.codegeneration.nest_unit_converter import NESTUnitConverter
from pynestml.codegeneration.python_standalone_unit_converter import PythonStandaloneUnitConverter
from pynestml.symbols.predefined_quantities import PredefinedQuantities
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits


@pytest.fixture(scope="module", autouse=True)
def setUp():
    PredefinedUnits.register_units()
    PredefinedTypes.register_types()


# each case: (unit, expected preferred unit for NEST, expected preferred unit for the Python-standalone target (SI))
COMPLEX_UNITS = [
    ((u.V / u.s)**-0.5, (u.mV / u.ms)**-0.5, (u.V / u.s)**-0.5),
    ((u.V / u.ms)**-0.5, (u.mV / u.ms)**-0.5, (u.V / u.s)**-0.5),
    ((u.nS / u.uF)**0.5, u.ms**-0.5, u.s**-0.5),
    (u.uS**2 / u.ms, u.nS**2 / u.ms, u.S**2 / u.s),
    ((u.mmol / u.l)**-1.5, (u.mol / u.m**3)**-1.5, (u.mol / u.m**3)**-1.5),
    (u.mV**-2 / u.ms, u.mV**-2 / u.ms, u.V**-2 / u.s),
    ((u.pA * u.GOhm)**1.5, u.mV**1.5, u.V**1.5),
    (u.ns**(1 / 3), u.ms**(1 / 3), u.s**(1 / 3)),
    (u.pF / u.mV / u.ms, u.pA / u.mV**2, u.A / u.V**2),
    ((u.MOhm * u.uF)**-(3 / 2), u.ms**-1.5, u.s**-1.5),
    ((u.kHz * u.nC / u.uA)**2, u.dimensionless_unscaled, u.dimensionless_unscaled),
]


@pytest.mark.parametrize("unit, expected_nest_unit, expected_si_unit", COMPLEX_UNITS)
@pytest.mark.parametrize("converter", [NESTUnitConverter, PythonStandaloneUnitConverter])
def test_preferred_unit_and_factor(converter, unit, expected_nest_unit, expected_si_unit):
    r"""The preferred unit of complex units (products, quotients, negative and fractional powers) is as expected, and the conversion factor is equal to the one computed independently by astropy."""
    expected_unit = expected_nest_unit if converter is NESTUnitConverter else expected_si_unit

    preferred_unit = converter.get_preferred_unit(unit)
    assert preferred_unit.is_equivalent(expected_unit)
    assert preferred_unit.to(expected_unit) == pytest.approx(1., rel=1E-12)    # the same unit, not only the same dimension

    expected_factor = (1. * unit).to(expected_unit).value
    assert converter.get_factor(unit) == pytest.approx(expected_factor, rel=1E-12)


def test_si_factor_is_magnitude():
    r"""For the Python-standalone target, all values are in coherent SI units, so the conversion factor is the magnitude of the unit in SI."""
    for unit, _, _ in COMPLEX_UNITS:
        assert PythonStandaloneUnitConverter.get_factor(unit) == pytest.approx(unit.si.scale, rel=1E-12)


# units with which to construct products and powers; their combinations cover all preferred base units of NEST
BASE_UNITS = [u.mV, u.V, u.uS, u.pF, u.ns, u.s, u.mmol, u.GOhm, u.uA, u.kHz, u.l]
EXPONENTS = [-1.5, -0.5, 1 / 3, 2]


@pytest.mark.parametrize("converter", [NESTUnitConverter, PythonStandaloneUnitConverter])
def test_factor_is_coherent(converter):
    r"""The system of units is coherent: the conversion factor of a product (or power) of units is the product (or power) of their conversion factors. This guarantees that expressions combining values in preferred units are again in preferred units, without additional conversion factors."""
    for unit_a, unit_b in itertools.combinations(BASE_UNITS, 2):
        assert converter.get_factor(unit_a * unit_b) == pytest.approx(converter.get_factor(unit_a) * converter.get_factor(unit_b), rel=1E-12)
        assert converter.get_factor(unit_a / unit_b) == pytest.approx(converter.get_factor(unit_a) / converter.get_factor(unit_b), rel=1E-12)

        for exponent in EXPONENTS:
            assert converter.get_factor((unit_a * unit_b)**exponent) == pytest.approx((converter.get_factor(unit_a) * converter.get_factor(unit_b))**exponent, rel=1E-12)


@pytest.mark.parametrize("quantity, nest_unit", [
    ("(voltage / time)**-(1/2)", (u.mV / u.ms)**-0.5),
    ("(conductance / capacitance)**(1/2)", u.ms**-0.5),
    ("conductance**2 / time", u.nS**2 / u.ms),
])
def test_interface_unit_of_complex_quantities(quantity, nest_unit):
    r"""Only quantities that match an interface unit exactly are exchanged with the user in that unit: for NEST, "1 / time" is exchanged in Hz, but a quantity like "time**-(1/2)" (which is not a rate) is exchanged in its preferred unit."""
    unit = PredefinedQuantities.parse(quantity)
    type_symbol = PredefinedTypes.get_type(unit)

    assert NESTUnitConverter.get_interface_unit(unit).is_equivalent(nest_unit)
    assert NESTUnitConverter.get_interface_unit(unit).to(nest_unit) == pytest.approx(1.)
    assert NESTUnitConverter.get_interface_factor(type_symbol) == 1.

    # whereas a rate is exchanged in Hz, and stored in 1/ms
    rate_type = PredefinedTypes.get_type(PredefinedQuantities.parse("1 / time"))
    assert NESTUnitConverter.get_interface_unit(PredefinedQuantities.parse("1 / time")) == u.Hz
    assert NESTUnitConverter.get_interface_factor(rate_type) == pytest.approx(1000.)
