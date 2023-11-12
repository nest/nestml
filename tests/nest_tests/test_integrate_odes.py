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
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.model_parser import ModelParser

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
                                                                       os.path.join(os.pardir, os.pardir, "models", "neurons",  "iaf_psc_exp_neuron.nestml"))),
                                         os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                       os.path.join("resources", "integrate_odes_test.nestml"))),
                                         os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                       os.path.join("resources", "integrate_odes_nonlinear_test.nestml")))],
                             logging_level="INFO",
                             module_name="nestml_module",
                             suffix="_nestml")
        nest.Install("nestml_module")

    def test_convolutions_always_integrated(self):
        r"""Test that synaptic integration continues for iaf_psc_exp, even when neuron is refractory."""

        sim_time: float = 100.    # [ms]
        resolution: float = .1    # [ms]
        spike_interval = 5.     # [ms]

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})

        # create the network
        sg = nest.Create("spike_generator",
                         params={"spike_times": spike_interval * (1 + np.arange(sim_time / spike_interval))})

        spikedet = nest.Create("spike_recorder")
        neuron = nest.Create("iaf_psc_exp_neuron_nestml", params={"refr_T": 20.})  # long refractory period
        mm = nest.Create("multimeter", params={"record_from": ["V_m", "I_syn_exc"]})
        nest.Connect(sg, neuron, "one_to_one", syn_spec={"delay": 1., "weight": 9999.})
        nest.Connect(mm, neuron)
        nest.Connect(neuron, spikedet)
        nest.Simulate(sim_time)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            timevec = nest.GetStatus(mm, "events")[0]["times"]
            V_m = nest.GetStatus(mm, "events")[0]["V_m"]
            I_exc = nest.GetStatus(mm, "events")[0]["I_syn_exc"]
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

        sim_time: float = 100.    # [ms]
        resolution: float = .1    # [ms]

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})

        # create the network
        spikedet = nest.Create("spike_recorder")
        neuron = nest.Create("integrate_odes_test_nestml")
        mm = nest.Create("multimeter", params={"record_from": ["test_1", "test_2"]})
        nest.Connect(mm, neuron)
        nest.Connect(neuron, spikedet)
        nest.Simulate(sim_time)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            timevec = nest.GetStatus(mm, "events")[0]["times"]
            test_1 = nest.GetStatus(mm, "events")[0]["test_1"]
            test_2 = nest.GetStatus(mm, "events")[0]["test_2"]
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

        sim_time: float = 100.    # [ms]
        resolution: float = .1    # [ms]

        nest.set_verbosity("M_ALL")
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": resolution})

        # create the network
        spikedet = nest.Create("spike_recorder")
        neuron = nest.Create("integrate_odes_nonlinear_test_nestml")
        mm = nest.Create("multimeter", params={"record_from": ["test_1", "test_2"]})
        nest.Connect(mm, neuron)
        nest.Connect(neuron, spikedet)
        nest.Simulate(sim_time)

        # plot
        if TEST_PLOTS:
            fig, ax = plt.subplots(nrows=2)
            ax1, ax2 = ax

            timevec = nest.GetStatus(mm, "events")[0]["times"]
            test_1 = nest.GetStatus(mm, "events")[0]["test_1"]
            test_2 = nest.GetStatus(mm, "events")[0]["test_2"]
            ax2.plot(timevec, test_2, label="test_2")
            ax1.plot(timevec, test_1, label="test_1", alpha=.7, linestyle=":")

            for _ax in ax:
                _ax.grid(which="major", axis="both")
                _ax.grid(which="minor", axis="x", linestyle=":", alpha=.4)
                # _ax.minorticks_on()
                _ax.set_xlim(0., sim_time)
                _ax.legend()

            fig.savefig("/tmp/test_integrate_odes_nonlinear.png", dpi=300)

        # # verify
        np.testing.assert_allclose(test_1[-1], 9.65029871)
        np.testing.assert_allclose(test_2[-1], 5.34894639)

    def test_integrate_odes_params(self):
        r"""Test the integrate_odes() function, in particular with respect to the parameter types."""

        Logger.init_logger(LoggingLevel.INFO)
        SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedVariables.register_variables()
        PredefinedFunctions.register_functions()
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_file(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join("resources", "integrate_odes_test_params.nestml"))))
        assert len(Logger.get_all_messages_of_level_and_or_node(model.get_model_list()[0], LoggingLevel.ERROR)) == 6
