# -*- coding: utf-8 -*-
#
# test_complex_quantities.py
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

import importlib
import numpy as np
import os

from astropy import units as u

from pynestml.frontend.pynestml_frontend import generate_python_standalone_target


class TestPythonStandaloneComplexQuantities:
    r"""
    Physical quantities that are combined using powers (including negative and fractional powers), products and quotients are converted correctly into the SI units used by the Python-standalone target.

    The expected values are computed independently using astropy, from the literals in the model ``tests/nest_tests/resources/ComplexQuantitiesNeuron.nestml``.
    """

    def test_python_standalone_complex_quantities(self):
        input_path = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, "nest_tests", "resources", "ComplexQuantitiesNeuron.nestml"))
        module_name = "nestml_complex_quantities_module"
        generate_python_standalone_target(input_path,
                                          target_path=module_name,
                                          module_name=module_name,
                                          logging_level="INFO",
                                          suffix="")

        neuron_module = importlib.import_module(module_name + ".complex_quantities_neuron")
        timestep = 1E-4    # [s]
        neuron = neuron_module.Neuron_complex_quantities_neuron(timestep=timestep)

        # parameter values as given in the model
        a_1 = 2 * (u.V / u.s)**-0.5
        a_2 = 2 * (u.V / u.ms)**-0.5
        b_sqrt_rate = 4 * (u.nS / u.uF)**0.5
        c = 3 * u.mV / u.ms

        # parameters, in SI units
        np.testing.assert_allclose(neuron.get_a_1(), a_1.to((u.V / u.s)**-0.5).value)
        np.testing.assert_allclose(neuron.get_a_2(), a_2.to((u.V / u.s)**-0.5).value)
        np.testing.assert_allclose(neuron.get_b_sqrt_rate(), b_sqrt_rate.to(u.s**-0.5).value)
        np.testing.assert_allclose(neuron.get_c(), c.to(u.V / u.s).value)

        # initial values of state variables, computed from the parameters
        np.testing.assert_allclose(neuron.get_rate_y(), (b_sqrt_rate**2).to(u.s**-1).value)
        np.testing.assert_allclose(neuron.get_t_half(), (a_2 * (1 * u.mV)**0.5).to(u.s**0.5).value)
        np.testing.assert_allclose(neuron.get_s_1(), a_1.to((u.V / u.s)**-0.5).value)

        # w' = -w / (a_1**2 * 1 mV): the time constant follows from a quantity raised to a fractional power
        tau = (a_1**2 * 1 * u.mV).to(u.s).value
        np.testing.assert_allclose(tau, 4E-3)

        n_steps = 40
        for i in range(n_steps):
            neuron.step(origin=i * timestep, timestep=timestep)

        np.testing.assert_allclose(neuron.get_w(), np.exp(-n_steps * timestep / tau))

        # s_1 = 3 * a_2 in the update block
        np.testing.assert_allclose(neuron.get_s_1(), (3 * a_2).to((u.V / u.s)**-0.5).value)
