# -*- coding: utf-8 -*-
#
# test_time_variable.py
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

import matplotlib.pyplot as plt
import numpy as np
import os
import pytest
import scipy.signal

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestTimeVariable:
    """Sanity test for the predefined variable ``t``, which represents simulation time"""

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        input_path = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "TimeVariableNeuron.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "neurons", "iaf_psc_delta_neuron.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "TimeVariableSynapse.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "TimeVariablePrePostSynapse.nestml")))]
        target_path = "target"
        logging_level = "DEBUG"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             suffix=suffix,
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_delta_neuron",
                                                                     "synapse": "time_variable_pre_post_synapse",
                                                                     "post_ports": ["post_spikes"]}],
                                           "weight_variable": {"time_variable_synapse": "w",
                                                               "time_variable_pre_post_synapse": "w"}})

    def test_time_variable_neuron(self):
        nest.ResetKernel()
        nest.resolution = .25    # [ms]
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass
        nrn = nest.Create("time_variable_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["x", "y"]})
        nest.Connect(mm, nrn)

        nest.Simulate(100.0)

        timevec = mm.get("events")["times"]
        x = mm.get("events")["x"]
        y = mm.get("events")["y"]

        np.testing.assert_allclose(x, timevec)
        np.testing.assert_allclose(1E-3 * x, y)

    def test_time_variable_synapse(self):
        """a synapse is only updated when presynaptic spikes arrive"""
        nest.ResetKernel()
        nest.resolution = .25    # [ms]
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass
        nrn = nest.Create("iaf_psc_delta", 2)
        nrn[0].I_e = 1000.  # [pA]
        sr = nest.Create("spike_recorder")
        nest.Connect(nrn[0], sr)
        nest.Connect(nrn[0], nrn[1], syn_spec={"synapse_model": "time_variable_synapse_nestml"})
        syn = nest.GetConnections(nrn[0], nrn[1])
        syn.delay = nest.resolution    # [ms]
        syn.d = nest.resolution
        assert len(syn) == 1

        sr_pre = nest.Create("spike_recorder")
        sr_post = nest.Create("spike_recorder")
        nest.Connect(nrn[0], sr_pre)
        nest.Connect(nrn[1], sr_post)

        nest.set_verbosity("M_FATAL")

        T_sim = 50.    # [ms]
        sim_interval = nest.resolution    # [ms]
        timevec = [0.]
        x = [syn[0].get("x")]
        y = [syn[0].get("y")]
        while nest.biological_time < T_sim:
            nest.Simulate(sim_interval)
            timevec.append(nest.biological_time)
            x.append(syn[0].get("x"))
            y.append(syn[0].get("y"))

        assert len(sr.get("events")["times"]) > 2, "Was expecting some more presynaptic spikes"

        #
        #   analysis
        #

        timevec = np.array(timevec)
        x = np.array(x)
        y = np.array(y)
        x_error = np.abs(timevec - x)
        y_error = np.abs(timevec - y)

        x_peaks_idx, _ = scipy.signal.find_peaks(-x_error)
        y_peaks_idx, _ = scipy.signal.find_peaks(-y_error)

        #
        #   plot
        #

        fig, ax = plt.subplots(nrows=4, figsize=(8, 8))

        ax[0].scatter(sr_pre.get("events")["times"], np.zeros_like(sr_pre.get("events")["times"]))
        ax[0].set_ylabel("Pre spikes")

        ax[1].scatter(sr_post.get("events")["times"], np.zeros_like(sr_post.get("events")["times"]))
        ax[1].set_ylabel("Post spikes")

        ax[2].plot(timevec, x, label="x")
        ax[2].plot(timevec, timevec, linestyle="--", c="gray")
        ax2_ = ax[2].twinx()
        ax2_.plot(timevec, x_error, c="red")
        ax2_.scatter(timevec[x_peaks_idx], x_error[x_peaks_idx], edgecolor="red", facecolor="none")

        ax[3].plot(timevec, y, label="y")
        ax[3].plot(timevec, timevec, linestyle="--", c="gray")
        ax3_ = ax[3].twinx()
        ax3_.plot(timevec, y_error, c="red")
        ax3_.scatter(timevec[y_peaks_idx], y_error[y_peaks_idx], edgecolor="red", facecolor="none")

        ax[-1].set_ylabel("Time [ms]")

        for _ax in ax:
            _ax.grid(True)
            _ax.legend()
            _ax.set_xlim(-1, T_sim + 1)

        fig.savefig("/tmp/test_time_variable_synapse.png")

        #
        #   testing
        #

        assert all(x_error[x_peaks_idx] <= nest.resolution + 1E-12)
        assert all(y_error[y_peaks_idx] <= nest.resolution + 1E-12)

    def test_time_variable_pre_post_synapse(self):
        """a synapse is updated when pre- and postsynaptic spikes arrive"""
        nest.ResetKernel()
        nest.resolution = .25    # [ms]
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass
        nrn = nest.Create("iaf_psc_delta_neuron_nestml__with_time_variable_pre_post_synapse_nestml", 2)
        nrn[0].I_e = 1000.  # [pA]
        nrn[1].I_e = 1500.  # [pA]
        sr_pre = nest.Create("spike_recorder")
        sr_post = nest.Create("spike_recorder")
        nest.Connect(nrn[0], sr_pre)
        nest.Connect(nrn[1], sr_post)
        nest.Connect(nrn[0], nrn[1], syn_spec={"synapse_model": "time_variable_pre_post_synapse_nestml__with_iaf_psc_delta_neuron_nestml"})
        syn = nest.GetConnections(nrn[0], nrn[1])
        syn.delay = nest.resolution    # [ms]
        syn.d = nest.resolution
        assert len(syn) == 1

        T_sim = 20.  # [ms]
        sim_interval = nest.resolution    # [ms]
        timevec = [0.]
        x = [syn[0].get("x")]
        y = [syn[0].get("y")]
        z = [syn[0].get("z")]
        # n_post_spikes = [syn[0].get("n_post_spikes")]
        while nest.biological_time < T_sim:
            nest.Simulate(sim_interval)
            timevec.append(nest.biological_time)
            x.append(syn[0].get("x"))
            y.append(syn[0].get("y"))
            z.append(syn[0].get("z"))
            # n_post_spikes.append(syn[0].get("n_post_spikes"))

        #
        #   analysis
        #

        timevec = np.array(timevec)
        x = np.array(x)
        y = np.array(y)
        x_error = np.abs(timevec - x)
        y_error = np.abs(timevec - y)
        z_error = np.abs(timevec - z)

        x_peaks_idx, _ = scipy.signal.find_peaks(-x_error)
        y_peaks_idx, _ = scipy.signal.find_peaks(-y_error)
        z_peaks_idx, _ = scipy.signal.find_peaks(-z_error)

        #
        #   plot
        #

        fig, ax = plt.subplots(nrows=5, figsize=(8, 8))

        ax[0].scatter(sr_pre.get("events")["times"], np.zeros_like(sr_pre.get("events")["times"]))
        ax[0].set_ylabel("Pre spikes")

        ax[1].scatter(sr_post.get("events")["times"], np.zeros_like(sr_post.get("events")["times"]))
        ax[1].set_ylabel("Post spikes")

        ax[2].plot(timevec, x, label="x")
        ax[2].plot(timevec, timevec, linestyle="--", c="gray")
        ax2_ = ax[2].twinx()
        ax2_.plot(timevec, x_error, c="red")
        ax2_.scatter(timevec[x_peaks_idx], x_error[x_peaks_idx], edgecolor="red", facecolor="none")

        ax[3].plot(timevec, y, label="y")
        ax[3].plot(timevec, timevec, linestyle="--", c="gray")
        ax3_ = ax[3].twinx()
        ax3_.plot(timevec, y_error, c="red")
        ax3_.scatter(timevec[y_peaks_idx], y_error[y_peaks_idx], edgecolor="red", facecolor="none")

        ax[4].plot(timevec, z, label="z")
        ax[4].plot(timevec, timevec, linestyle="--", c="gray")
        ax4_ = ax[4].twinx()
        ax4_.plot(timevec, z_error, c="red")
        ax4_.scatter(timevec[z_peaks_idx], z_error[z_peaks_idx], edgecolor="red", facecolor="none")

        ax[-1].set_ylabel("Time [ms]")

        for _ax in ax:
            _ax.grid(True)
            _ax.legend()
            _ax.set_xlim(-1, T_sim + 1)

        fig.savefig("/tmp/test_time_variable_pre_post_synapse.png")

        #
        #   testing
        #

        assert all(x_error[x_peaks_idx] <= nest.resolution + 1E-12)
        assert all(y_error[y_peaks_idx] <= nest.resolution + 1E-12)

        # for z, which is assigned to on post spike times but only actually updated when a pre spike is processed, compare to the last post spike time
        post_spike_times = sr_post.get("events")["times"]
        for i, t in enumerate(timevec[z_peaks_idx]):
            # find the last post spike before t
            for i_, t_post_sp in enumerate(post_spike_times):
                if t_post_sp > t:
                    t_post_sp = post_spike_times[i_ - 1]
                    break

            time_interval = t - t_post_sp

            assert z_error[z_peaks_idx[i]] <= time_interval + nest.resolution + 1E-12
