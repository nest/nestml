# -*- coding: utf-8 -*-
#
# test_gap_junction.py
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

from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


class TestGapJunction:

    @pytest.mark.parametrize("neuron_model", ["iaf_psc_exp"])
    def test_gap_junction(self, neuron_model: str):

        codegen_opts = {"gap_junctions": {"enable": True,
                                          "gap_current_variable": "I_gap",
                                          "membrane_potential_variable": "V_m"}}

        files = [os.path.join("models", "neurons", neuron_model + ".nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             module_name="nestml_gap_module",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

        resolution = .1   # [ms]
        sim_time = 100.   # [ms]
        pre_spike_times = [1., 11., 21.]    # [ms]


        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.Install("nestml_gap_module")

        print("Pre spike times: " + str(pre_spike_times))

        # nest.set_verbosity("M_WARNING")
        nest.set_verbosity("M_ERROR")

        nest.resolution = resolution
        nest.wfr_comm_interval = 2.         # [ms]

        pre_neuron = nest.Create("parrot_neuron")
        post_neuron = nest.Create("iaf_psc_exp")

        # create spike_generators with these times
        pre_sg = nest.Create("spike_generator",
                             params={"spike_times": pre_spike_times})
        nest.Connect(pre_sg, pre_neuron)

        nest.Connect(pre_neuron, post_neuron, {'synapse_model': 'gap_junction'})

        spikedet_pre = nest.Create("spike_detector")
        nest.Connect(pre_neuron, spikedet_pre)

        mm = nest.Create("multimeter", params={"record_from": ["V_m"]})
        nest.Connect(mm, post_neuron)

        nest.Simulate(sim_time)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            timevec = nest.GetStatus(mm, "events")[0]["times"]
            V_m = nest.GetStatus(mm, "events")[0]["V_m"]
            ax1.plot(timevec, V_m)
            ax1.set_ylabel("V_m")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                # _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()

            fig.savefig("/tmp/gap_junction_test.png", dpi=300)
