# -*- coding: utf-8 -*-
#
# nest_integration_doc_test.py
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

import nest
import os
import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


class TestNESTIntegration:

    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        # input_path = os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml")
        input_path = os.path.join("nestml_convolve_numerics.nestml")
        logging_level = "INFO"
        self._module_name = "nestmlmodule"
        suffix = "_nestml"

        if 1:
         generate_nest_target(input_path,
                             logging_level=logging_level,
                             module_name=self._module_name,
                             suffix=suffix)

        nest.Install(self._module_name)

    def _run_simulation(self, T_sim, syn_delay):
        # network construction

        neuron = nest.Create("iaf_psc_exp_nestml")

        sg = nest.Create("spike_generator", params={"spike_times": [1.]})
        nest.Connect(sg, neuron, syn_spec={"weight": 1000., "delay": syn_delay})

        mm = nest.Create("multimeter", params={"record_from": ["V_m", "I_syn_exc"], "interval": nest.resolution})
        nest.Connect(mm, neuron)

        # simulate

        nest.Simulate(T_sim)

        sg_spike_times = sg.spike_times
        mm_times = mm.events["times"]
        mm_vals = {k: mm.events[k] for k in mm.events.keys()}

        return sg_spike_times, mm_times, mm_vals


    """def _run_simulation(self, T_sim, syn_delay, t_pulse_start, t_pulse_stop, I_stim):
        # network construction

        neuron = nest.Create("iaf_psc_exp_nestml")

        sg = nest.Create("spike_generator", params={"spike_times": [1.]})
        nest.Connect(sg, neuron, syn_spec={"weight": 1000., "delay": syn_delay})

        mm = nest.Create("multimeter", params={"record_from": ["V_m", "I_syn_exc"], "interval": nest.resolution})
        nest.Connect(mm, neuron)

        # simulate

        nest.Simulate(t_pulse_start)
        dc.amplitude = I_stim * 1E12  # 1E12: convert A to pA

        nest.Simulate(t_pulse_stop)
        dc.amplitude = 0.

        nest.Simulate(T_sim - t_pulse_stop)

        return sg, mm
"""


    """def test_I_stim(self):
        T_sim = 10.  # [ms]
        syn_delay = 1.   # [ms]

        I_stim = 100E-12 # [A]

        t_pulse_start = 10. # [ms]
        t_pulse_stop = 90. # [ms]

        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.resolution = 1. # [ms]

        sg, mm = self._run_simulation(T_sim, syn_delay, t_pulse_start, t_pulse_stop, I_stim)

        nest.ResetKernel()
        nest.resolution = .01 # [ms]

        _, mm_fine = self._run_simulation(T_sim, syn_delay, t_pulse_start, t_pulse_stop, I_stim)

        # analysis

        if TEST_PLOTS:
            self._plot_psp(sg, mm, mm_fine, syn_delay)
"""

    def test_psp(self):
        T_sim = 11.  # [ms]
        syn_delay = 1.   # [ms]

        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.resolution = .01 # [ms]
        _, mm_fine_times, mm_fine_vals = self._run_simulation(T_sim, syn_delay)

        nest.ResetKernel()
        nest.resolution = 1. # [ms]

        sg_spike_times, mm_times, mm_vals = self._run_simulation(T_sim, syn_delay)

        # analysis

        if TEST_PLOTS:
            self._plot_psp(sg_spike_times, mm_times, mm_vals, mm_fine_times, mm_fine_vals, syn_delay)


    def _plot_psp(self, sg_spike_times, mm_times, mm_vals, mm_fine_times, mm_fine_vals, syn_delay):
        fig, ax = plt.subplots(nrows=3)

        for t in sg_spike_times:
            ax[0].arrow(t + syn_delay, 0, 0, .8, width=.5E-1, edgecolor="none", overhang=.2, color="black")
        ax[0].set_yticks([0., 1.])
        ax[0].set_ylabel("Dendritic input")

        for ax_idx, key, ylabel in [(1, "I_kernel_exc__X__exc_spikes", "current"),
                                        (2, "V_m", "voltage")]:
            ax[ax_idx].plot(mm_fine_times, mm_fine_vals[key], linestyle="-", color="#1f77b4")
            ax[ax_idx].plot(mm_times, mm_vals[key], label="I_psp", linestyle="dashdot", color="#9467bd")
            for i, (t, val) in enumerate(zip([0] + list(mm_times), [mm_vals[key][0]] + list(mm_vals[key]))):
                #ax[ax_idx].plot([t, t + nest.resolution], [val, val], linestyle=":", color="orange")
                #ax[ax_idx].plot([t + nest.resolution, t + nest.resolution], [val, mm_vals[key][min(i , len(mm_vals[key]) - 1)]], linestyle=":", color="orange")
                ax[ax_idx].plot([t], [val], markersize=5, marker='o', linestyle='', color="orange")
                #ax[ax_idx].plot([t + nest.resolution], [val], markersize=5, marker='o', linestyle='', fillstyle='full', color="orange", markerfacecolor="white")
                if i == 1:
                    ax[ax_idx].plot([t + nest.resolution], [val], markersize=5, marker='o', linestyle='', fillstyle='full', color="orange", markerfacecolor="white")
            ax[ax_idx].set_ylabel(ylabel)

        for _ax in ax:
            _ax.set_xlim(0., nest.biological_time - 1.)
            _ax.grid(True)

        for _ax in ax[:-1]:
            _ax.set_xticklabels([])

        ax[-1].set_xlabel("Time [ms]")

        fig.savefig("/tmp/integration_numeric.png")
