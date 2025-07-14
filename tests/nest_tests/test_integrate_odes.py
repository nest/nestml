# -*- coding: utf-8 -*-
#
# test_integrate_odes.py
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
import scipy
import scipy.signal

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target, generate_target
from pynestml.utils.logger import LoggingLevel, Logger

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.ticker
    import matplotlib.pyplot as plt

    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestIntegrateODEs:

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""Generate the model code"""

        generate_nest_target(input_path=[os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                       os.path.join(os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))),
                                         os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                       os.path.join("resources", "integrate_odes_test.nestml"))),
                                         os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                       os.path.join("resources", "integrate_odes_nonlinear_test.nestml"))),
                                         os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                       os.path.join("resources", "alpha_function_2nd_order_ode_neuron.nestml"))),
                                         os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                       os.path.join("resources", "aeif_cond_alpha_alt_neuron.nestml")))],
                             logging_level="INFO",
                             suffix="_nestml")

    def test_convolutions_always_integrated(self):
        r"""Test that synaptic integration continues for iaf_psc_exp, even when neuron is refractory."""

        sim_time: float = 100.  # [ms]
        resolution: float = .1  # [ms]
        spike_interval = 5.  # [ms]

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

        # create the network
        sg = nest.Create("spike_generator",
                         params={"spike_times": spike_interval * (1 + np.arange(sim_time / spike_interval))})

        spikedet = nest.Create("spike_recorder")
        neuron = nest.Create("iaf_psc_exp_neuron_nestml", params={"refr_T": 20.})  # long refractory period
        mm = nest.Create("multimeter", params={"record_from": ["V_m", "I_syn_exc"]})
        nest.Connect(sg, neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
        nest.Connect(mm, neuron)
        nest.Connect(neuron, spikedet)

        # simulate
        nest.Simulate(sim_time)

        # analyze
        timevec = nest.GetStatus(mm, "events")[0]["times"]
        V_m = nest.GetStatus(mm, "events")[0]["V_m"]
        I_exc = nest.GetStatus(mm, "events")[0]["I_syn_exc"]

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            ax2.plot(timevec, I_exc, label="I_exc")
            ax1.plot(timevec, V_m, label="V_m", alpha=.7, linestyle=":")
            ev = spikedet.events["times"]
            ax1.scatter(ev, np.mean(V_m) * np.ones_like(ev), marker="x", s=50)

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                _ax.set_xlim(0., sim_time)
                _ax.legend()

            fig.savefig("/tmp/test_integrate_odes.png", dpi=300)

        # verify
        n_peaks_in_I_exc = len(scipy.signal.find_peaks(I_exc)[0])
        assert n_peaks_in_I_exc > 18

    def test_integrate_odes(self):
        r"""Test the integrate_odes() function, in particular when not all the ODEs are being integrated."""

        sim_time: float = 100.  # [ms]
        resolution: float = .1  # [ms]

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

        # create the network
        neuron = nest.Create("integrate_odes_test_nestml")
        mm = nest.Create("multimeter", params={"record_from": ["test_1", "test_2"]})
        nest.Connect(mm, neuron)

        # simulate
        nest.Simulate(sim_time)

        # analyze
        timevec = nest.GetStatus(mm, "events")[0]["times"]
        test_1 = nest.GetStatus(mm, "events")[0]["test_1"]
        test_2 = nest.GetStatus(mm, "events")[0]["test_2"]

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            ax2.plot(timevec, test_2, label="test_2")
            ax1.plot(timevec, test_1, label="test_1", alpha=.7, linestyle=":")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                # _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()

            fig.savefig("/tmp/test_integrate_odes.png", dpi=300)

        # # verify
        np.testing.assert_allclose(test_1[-1], 9.65029871)
        np.testing.assert_allclose(test_2[-1], 5.34894639)

    def test_integrate_odes_nonlinear(self):
        r"""Test the integrate_odes() function, in particular when not all the ODEs are being integrated, for nonlinear ODEs."""

        sim_time: float = 100.  # [ms]
        resolution: float = .1  # [ms]

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

        # create the network
        neuron = nest.Create("integrate_odes_nonlinear_test_nestml")
        mm = nest.Create("multimeter", params={"record_from": ["test_1", "test_2"]})
        nest.Connect(mm, neuron)

        # simulate
        nest.Simulate(sim_time)

        # analyze
        timevec = nest.GetStatus(mm, "events")[0]["times"]
        test_1 = nest.GetStatus(mm, "events")[0]["test_1"]
        test_2 = nest.GetStatus(mm, "events")[0]["test_2"]

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            ax2.plot(timevec, test_2, label="test_2")
            ax1.plot(timevec, test_1, label="test_1", alpha=.7, linestyle=":")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                _ax.set_xlim(0., sim_time)
                _ax.legend()

            fig.savefig("/tmp/test_integrate_odes_nonlinear.png", dpi=300)

        # # verify
        np.testing.assert_allclose(test_1[-1], 9.65029871)
        np.testing.assert_allclose(test_2[-1], 5.34894639)

    def test_integrate_odes_params(self):
        r"""Test the integrate_odes() function, in particular with respect to the parameter types."""

        fname = os.path.realpath(
            os.path.join(os.path.dirname(__file__), os.path.join("resources", "integrate_odes_test_params.nestml")))
        generate_target(input_path=fname, target_platform="NONE", logging_level="DEBUG")

        assert len(Logger.get_messages("integrate_odes_test", LoggingLevel.ERROR)) == 2

    def test_integrate_odes_params2(self):
        r"""Test the integrate_odes() function, in particular with respect to non-existent parameter variables."""

        fname = os.path.realpath(
            os.path.join(os.path.dirname(__file__), os.path.join("resources", "integrate_odes_test_params2.nestml")))
        generate_target(input_path=fname, target_platform="NONE", logging_level="DEBUG")

        assert len(Logger.get_messages("integrate_odes_test", LoggingLevel.ERROR)) == 2

    def test_integrate_odes_higher_order(self):
        r"""
        Tests for higher-order ODEs of the form F(x'',x',x)=0, integrate_odes(x) integrates the full dynamics of x.
        """
        resolution = 0.1
        simtime = 15.
        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})
        try:
            nest.Install("nestmlmodule")
        except Exception:
            # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
            pass

        n = nest.Create("alpha_function_2nd_order_ode_neuron_nestml")
        sgX = nest.Create("spike_generator", params={"spike_times": [10.]})
        nest.Connect(sgX, n, syn_spec={"weight": 1., "delay": resolution})

        mm = nest.Create("multimeter", params={"interval": resolution, "record_from": ["x", "y"]})
        nest.Connect(mm, n)

        nest.Simulate(simtime)
        times = mm.get()["events"]["times"]
        x_actual = mm.get()["events"]["x"]
        y_actual = mm.get()["events"]["y"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            ax2.plot(times, x_actual, label="x")
            ax1.plot(times, y_actual, label="y")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                _ax.set_xlim(0., simtime)
                _ax.legend()

            fig.savefig("/tmp/test_integrate_odes_higher_order.png", dpi=300)

        # verify
        np.testing.assert_allclose(x_actual[-1], 0.10737970490959549)
        np.testing.assert_allclose(y_actual[-1], 0.6211608596446752)

    def test_integrate_odes_numeric_higher_order(self):
        r"""
        Tests for higher-order ODEs of the form F(x'',x',x)=0, integrate_odes(x) integrates the full dynamics of x with a numeric solver.
        """
        resolution = 0.1
        simtime = 800.
        params_nestml = {"V_peak": 0.0, "a": 4.0, "b": 80.5, "E_L": -70.6,
                         "g_L": 300.0, 'E_exc': 20.0, 'E_inh': -85.0,
                         'tau_syn_exc': 40.0, 'tau_syn_inh': 20.0}

        params_nest = {"V_peak": 0.0, "a": 4.0, "b": 80.5, "E_L": -70.6,
                       "g_L": 300.0, 'E_ex': 20.0, 'E_in': -85.0,
                       'tau_syn_ex': 40.0, 'tau_syn_in': 20.0}

        for model in ["aeif_cond_alpha_alt_neuron_nestml", "aeif_cond_alpha"]:
            nest.set_verbosity("M_ALL")
            nest.ResetKernel()
            nest.SetKernelStatus({"resolution": resolution})
            try:
                nest.Install("nestmlmodule")
            except Exception:
                # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
                pass
            n = nest.Create(model)
            if "_nestml" in model:
                nest.SetStatus(n, params_nestml)
            else:
                nest.SetStatus(n, params_nest)

            spike = nest.Create("spike_generator")
            spike_times = [10.0, 400.0]
            nest.SetStatus(spike, {"spike_times": spike_times})
            nest.Connect(spike, n, syn_spec={"weight": 0.1, "delay": 1.0})
            nest.Connect(spike, n, syn_spec={"weight": -0.2, "delay": 100.})

            mm = nest.Create("multimeter", params={"record_from": ["V_m"]})
            nest.Connect(mm, n)

            nest.Simulate(simtime)
            times = mm.get()["events"]["times"]
            if "_nestml" in model:
                v_m_nestml = mm.get()["events"]["V_m"]
            else:
                v_m_nest = mm.get()["events"]["V_m"]

        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=1)

            ax.plot(times, v_m_nestml, label="NESTML")
            ax.plot(times, v_m_nest, label="NEST")
            ax.legend()

            fig.savefig("/tmp/test_integrate_odes_numeric_higher_order.png")

        np.testing.assert_allclose(v_m_nestml, v_m_nest)
