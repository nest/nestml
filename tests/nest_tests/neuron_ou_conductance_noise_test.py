# -*- coding: utf-8 -*-
#
# neuron_ou_conductance_noise_test.py
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
import numpy as np
import os
import unittest

from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


class TestOUConductanceNoise(unittest.TestCase):
    record_from = ["g_noise_exc", "g_noise_inh"]

    def simulate_OU_noise_neuron(self, resolution):
        r"""
        Simulates a single neuron with OU noise conductances.

        Parameters
        ----------
        resolution : float
            Resolution of the NEST simulation

        Returns
        -------
        dict
            State of the multimeter, which is connected to the neuron.
        tuple
            Tuple with the NEST id of the simulated neuron

        """
        seed = np.random.randint(0, 2**32 - 1)
        print("seed: {}".format(seed))
        nest.SetKernelStatus({"resolution": resolution, "rng_seed": seed + 1})

        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                "..", "..", "models", "neurons", "hh_cond_exp_destexhe.nestml")))
        target_path = "target"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.set_verbosity("M_ALL")

        nest.Install("nestmlmodule")
        neuron = nest.Create("hh_cond_exp_destexhe_nestml")

        multi = nest.Create("multimeter", params={"record_from": self.record_from, "interval": resolution})

        nest.Connect(multi, neuron)
        nest.Simulate(500000)

        return multi.get("events"), neuron

    def calc_statistics(self, state, neuron):
        """Calculates statistics for the Ornstein-Uhlenbeck-noise conductances.

        Calculates the means and variances of the conductances and compares them
        with the expected means and variances

        Parameters
        ----------
        state : dict
            The state of the multimeter which you get by calling multimeter.get("events")
        neuron : tuple
            Tuple with the NEST id of the neuron with the OU noise conductances
        """

        MAX_VAR_DIFF_PERC = 5.
        MAX_MEAN_DIFF_PERC = 1.

        print("\n\n======== Noise Conductance Statistics ==============")
        times = state["times"]

        # excitatory noise
        sigma_exc = neuron.get("sigma_noise_exc")
        mean_exc = neuron.get("g_noise_exc0")
        tau_exc = neuron.get("tau_syn_exc")
        var_exc = sigma_exc**2 / (2 / tau_exc)

        # inhibitory noise
        sigma_inh = neuron.get("sigma_noise_inh")
        mean_inh = neuron.get("g_noise_inh0")
        tau_inh = neuron.get("tau_syn_inh")
        var_inh = sigma_inh**2 / (2 / tau_inh)

        # variances
        print("\n____variances_______________________________________")
        vex = np.var(state["g_noise_exc"])
        vin = np.var(state["g_noise_inh"])
        vex_trgt = sigma_exc**2
        vin_trgt = sigma_inh**2
        diff_perc_vex = np.abs(1 - vex / vex_trgt) * 100
        diff_perc_vin = np.abs(1 - vin / vin_trgt) * 100
        print("ex: {:.2f}\ttarget = {:.2f}\tdiff = {:.2f} ({:.2f}%)".format(
            vex, vex_trgt, np.abs(vex - vex_trgt), diff_perc_vex))
        print("in: {:.2f}\ttarget = {:.2f}\tdiff = {:.2f} ({:.2f}%)".format(
            vin, vin_trgt, np.abs(vin - vin_trgt), diff_perc_vin))
        assert 0. < diff_perc_vex < MAX_VAR_DIFF_PERC
        assert 0. < diff_perc_vin < MAX_VAR_DIFF_PERC

        # means
        print("\n____means___________________________________________")
        m_exc_data = np.mean(state["g_noise_exc"])
        m_inh_data = np.mean(state["g_noise_inh"])
        diff_perc_mexc = np.abs(1 - m_exc_data / mean_exc) * 100
        diff_perc_minh = np.abs(1 - m_inh_data / mean_inh) * 100
        print("ex: {:.2f}\ttarget = {:.2f}\tdiff = {:.2f} ({:.2f}%)".format(
            m_exc_data, mean_exc, np.abs(m_exc_data - mean_exc), diff_perc_mexc))
        print("in: {:.2f}\ttarget = {:.2f}\tdiff = {:.2f} ({:.2f}%)\n".format(
            m_inh_data, mean_inh, np.abs(m_inh_data - mean_inh), diff_perc_minh))
        assert 0. < diff_perc_mexc < MAX_MEAN_DIFF_PERC
        assert 0. < diff_perc_minh < MAX_MEAN_DIFF_PERC

    def plot_results(self, state):
        """Reproduces figures 2A and 2B from Destexhe et al. 2001.

        Produces a plot with the time courses of the total excitatory (top left)
        and total inhibitory (bottom left) conductances during synaptic background
        activity as subplots. The two other subplots consist of distributions of
        values for each conductance (excitatory and inhibitory).

        Parameters
        ----------
        state : dict
            The state of the multimeter which you get by calling multimeter.get("events")
        """
        times = state["times"]
        fig, ax = plt.subplots(2, 2, constrained_layout=True, figsize=(15, 10))
        mask = times <= 1200.
        for idx, rf in enumerate(self.record_from):
            ax_cond = ax[idx][0]
            ax_hist = ax[idx][1]

            if "ex" in rf:
                ax_cond.set_ylim(0, 0.04)
                ax_cond.set_title("Excitatory Conductance")
                ax_hist.set_title("Conductance distribution (excitatory)")
            else:
                ax_cond.set_ylim(0.03, 0.08)
                ax_cond.set_title("Inhibitory Conductance")
                ax_hist.set_title("Conductance distribution (inhibitory)")

            ax_cond.plot(times[mask], state[rf][mask] / 1000.)
            ax_cond.set_xlabel("time (ms)")
            ax_cond.set_ylabel("Conductance (\u03bcS)")

            ax_hist.set_ylim((0, 2800))
            ax_hist.hist(state[rf][:19000] / 1000., bins=100, range=(0, 0.1))
            ax_hist.set_xlabel("Conductance (\u03bcS)")

        plt.savefig("figure2AB_destexhe2001.pdf")

    def test_ou_conductance_noise(self):
        state, neuron = self.simulate_OU_noise_neuron(resolution=1.)
        self.calc_statistics(state, neuron)

        if TEST_PLOTS:
            self.plot_results(state)
