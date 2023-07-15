# -*- coding: utf-8 -*-
#
# test_static_synapse.py
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


class TestStaticSynapse:

    neuron_model_name = "iaf_psc_exp_nestml__with_static_synapse_nestml"
    synapse_model_name = "static_synapse_nestml__with_iaf_psc_exp_nestml"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        """Generate the model code"""

        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp",
                                                  "synapse": "static_synapse"}]}

        files = [os.path.join("models", "neurons", "iaf_psc_exp.nestml"),
                 os.path.join("models", "synapses", "static_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    def test_static_synapse(self):
        pre_spike_times = [10., 40., 50.]
        resolution = 1.    # [ms]
        sim_time = 100.   # [ms]

        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})

        pre_neuron = nest.Create(self.neuron_model_name)
        post_neuron = nest.Create(self.neuron_model_name)

        pre_neuron.I_e = 999.

        mm = nest.Create("multimeter", params={"record_from": ["V_m"]})
        nest.Connect(mm, post_neuron)

        nest.Connect(pre_neuron, post_neuron, syn_spec={"synapse_model": self.synapse_model_name})

        spikedet_pre = nest.Create("spike_recorder")
        spikedet_post = nest.Create("spike_recorder")
        nest.Connect(pre_neuron, spikedet_pre)
        nest.Connect(post_neuron, spikedet_post)

        nest.Simulate(sim_time)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            timevec = nest.GetStatus(mm, "events")[0]["times"]
            V_m = nest.GetStatus(mm, "events")[0]["V_m"]
            ax[1].plot(timevec, V_m, label="nestml", alpha=.7, linestyle=":")
            ax[1].set_ylabel("V_m")

            n_spikes = len(spikedet_pre.events["times"])
            for i in range(n_spikes):
                if i == 0:
                    _lbl = "nest ref"
                else:
                    _lbl = None
                t_spike = spikedet_pre.events["times"]
                ax[0].plot(2 * [t_spike], [0, 1], linewidth=2, color="cyan", label=_lbl, alpha=.4)

            ax[0].set_ylabel("Pre spikes")
            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                # _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()

            fig.savefig("/tmp/static_synapse_test.png", dpi=300)

        # verify that membrane potential of post neuron goes up
        assert mm.events["V_m"][-1] > mm.events["V_m"][0]
