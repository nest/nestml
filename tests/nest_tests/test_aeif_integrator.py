# -*- coding: utf-8 -*-
#
# test_aeif_integrator.py
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

import numpy as np
import os
import pytest

import nest
from nest.lib.hl_api_exceptions import NESTErrors

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestAEIFIntegrator_with_respect_to_solution:
    r"""Check that the integrator default tolerances are set such that the adaptive exponential models do not cause trouble for the numerical integrator"""

    @pytest.mark.parametrize("gsl_adaptive_step_size_controller", ["with_respect_to_solution", "with_respect_to_derivative"])
    def test_aeif_integrator(self, gsl_adaptive_step_size_controller: str):
        # generate the code

        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, "models", "neurons", "aeif_cond_exp_neuron.nestml")))]
        logging_level = "DEBUG"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")

        generate_nest_target(input_path,
                             logging_level=logging_level,
                             suffix=suffix,
                             codegen_opts={"gsl_adaptive_step_size_controller": gsl_adaptive_step_size_controller})

        # run the simulation

        nest.ResetKernel()
        nest.resolution = 0.01
        nest.Install("nestmlmodule")

        params = {
            'E_L': -80,
            'V_reset': -60.0,
            'refr_T': 2.0,
            'g_L': 4,
            'C_m': 32,
            'E_exc': 0.0,
            'E_inh': -80.0,
            'tau_syn_exc': 1.5,
            'tau_syn_inh': 4.2,
            'a': 0.8,
            'b': 80,
            'Delta_T': 0.8,
            'tau_w': 144.0,
            'V_th': -57.0
        }

        neuron = nest.Create("aeif_cond_exp_neuron_nestml")
        neuron.set(**params)
        neuron.set({'V_m': -54.})

        # the test succeeds if the integrator terminates

        nest.Simulate(100.)

        assert not np.isnan(neuron.V_m)
