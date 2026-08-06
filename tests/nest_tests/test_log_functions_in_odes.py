# -*- coding: utf-8 -*-
#
# test_log_functions_in_odes.py
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
import os
import math

import nest
import numpy as np
from scipy.integrate import solve_ivp

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestLogFunctionsInODEs:
    """
    Tests the code generation of logarithmic functions when used in ODEs.
    """

    def ode_system(self, t, state, tau_d, tau_r, alpha_x, alpha_z, beta_x, beta_z, n_x, n_z):
        foo, x, z = state
        dfoodt = -foo + math.log10(tau_d / tau_r)
        dxdt = alpha_x / ((1 + x**n_x) * math.log(tau_d / tau_r) * 1.0) - beta_x * x
        dzdt = alpha_z / ((1 + x**n_z) * 1.0) - beta_z * z
        return [dfoodt, dxdt, dzdt]

    def evaluate_odes_scipy(self, inital_state, params, sim_time):
        solution = solve_ivp(
            fun=self.ode_system,
            t_span=[0, sim_time],  # interval of integration
            y0=inital_state,  # initial state
            args=params,  # parameters
            method="RK45",
            t_eval=np.arange(1.0, sim_time, 1.0),
            rtol=1e-6,  # relative tolerance
            atol=1e-6  # absolute tolerance
        )
        return solution.y

    def test_log_functions_in_odes(self):
        input_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "equations_log.nestml"))
        generate_nest_target(input_path=input_path,
                             target_path="target",
                             logging_level="INFO")
        nest.ResetKernel()
        nest.Install("nestmlmodule")
        nest.resolution = 0.1
        sim_time = 100.0

        n = nest.Create("equations_log_neuron")
        params_dict = nest.GetStatus(n)[0]
        initial_state = [params_dict["foo"], params_dict["x"], params_dict["z"]]
        params = [params_dict["tau_d"], params_dict["tau_r"], params_dict["alpha_x"],
                  params_dict["alpha_z"], params_dict["beta_x"], params_dict["beta_z"],
                  params_dict["n_x"], params_dict["n_z"]]

        mm = nest.Create("multimeter", params={"record_from": ["foo", "x", "z"]})
        nest.Connect(mm, n)

        nest.Simulate(sim_time)

        events = nest.GetStatus(mm, "events")[0]
        foo = events["foo"]
        x = events["x"]
        z = events["z"]

        # scipy solution
        solution_y = self.evaluate_odes_scipy(initial_state, params, sim_time)

        np.testing.assert_allclose(foo, solution_y[0, :], rtol=1e-5, atol=1e-5)
        np.testing.assert_allclose(x, solution_y[1, :], rtol=1e-5, atol=1e-5)
        np.testing.assert_allclose(z, solution_y[2, :], rtol=1e-5, atol=1e-5)
