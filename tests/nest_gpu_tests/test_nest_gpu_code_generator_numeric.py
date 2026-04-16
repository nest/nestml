# -*- coding: utf-8 -*-
#
# test_nest_gpu_code_generator_numeric.py
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

import numpy as np
import pytest
import multiprocessing as mp

# try to import matplotlib; set the result in the flag TEST_PLOTS
try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

from pynestml.frontend.pynestml_frontend import generate_nest_gpu_target


class TestNESTGPUNumericCodeGenerator:
    """
    Tests code generation for NEST GPU target for neuron models requiring numeric solver
    """

    @pytest.fixture(scope="module", autouse=True)
    def setup_method(self):
        model_files = ["aeif_psc_exp_neuron.nestml", "aeif_cond_alpha_alt_neuron.nestml", "izhikevich_neuron.nestml"]
        input_path = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", model)))) for model in model_files]
        target_path = "target_gpu_numeric"
        logging_level = "INFO"
        suffix = "_nestml"
        codegen_opts = {"solver": "numeric"}
        generate_nest_gpu_target(input_path, target_path,
                                 logging_level=logging_level,
                                 suffix=suffix,
                                 codegen_opts=codegen_opts)

        # Use spawn method for clean process creation
        mp.set_start_method('spawn', force=True)

    def run_aeif_simulation(self, neuron_model_name, params):
        import nestgpu as ngpu

        neuron = ngpu.Create(neuron_model_name, 1)
        ngpu.SetStatus(neuron, params)

        spike = ngpu.Create("spike_generator")
        spike_times = [10.0, 400.0]

        # set spike times and heights
        ngpu.SetStatus(spike, {"spike_times": spike_times})
        delay = [1.0, 100.0]
        weight = [0.1, 0.2]

        conn_spec = {"rule": "all_to_all"}
        syn_spec_ex = {'receptor': 0, 'weight': weight[0], 'delay': delay[0]}
        syn_spec_in = {'receptor': 1, 'weight': weight[1], 'delay': delay[1]}
        ngpu.Connect(spike, neuron, conn_spec, syn_spec_ex)
        ngpu.Connect(spike, neuron, conn_spec, syn_spec_in)

        record = ngpu.CreateRecord("", ["V_m"], [neuron[0]], [0])

        ngpu.Simulate(800.0)

        data_list = ngpu.GetRecordData(record)
        t = [row[0] for row in data_list]
        V_m = [row[1] for row in data_list]

        return t, V_m

    def run_izhikevich_simulation(self, neuron_model_name):
        import nestgpu as ngpu

        neuron = ngpu.Create(neuron_model_name, 1)
        spike = ngpu.Create("spike_generator")
        spike_times = [10.0, 40.0]

        # set spike times and height
        ngpu.SetStatus(spike, {"spike_times": spike_times})
        delay = [1.0, 10.0]
        weight = [1.0, -2.0]

        conn_spec = {"rule": "all_to_all"}

        syn_spec_ex = {'weight': weight[0], 'delay': delay[0]}
        syn_spec_in = {'weight': weight[1], 'delay': delay[1]}
        ngpu.Connect(spike, neuron, conn_spec, syn_spec_ex)
        ngpu.Connect(spike, neuron, conn_spec, syn_spec_in)

        record = ngpu.CreateRecord("", ["V_m"], [neuron[0]], [0])

        ngpu.Simulate(80.0)

        data_list = ngpu.GetRecordData(record)
        t = [row[0] for row in data_list]
        V_m = [row[1] for row in data_list]

        return t, V_m

    @pytest.mark.parametrize("neuron_model_name,params,nest_data_file_name",
                             [("aeif_psc_exp_neuron_nestml",
                               {"V_peak": 0.0, "a": 4.0, "b": 80.5, "E_L": -70.6, "g_L": 300.0, "tau_exc": 40.0,
                                "tau_inh": 20.0}, "test_aeif_psc_exp_nest.txt"),
                              ("aeif_cond_alpha_alt_neuron_nestml",
                               {"V_peak": 0.0, "a": 4.0, "b": 80.5, "E_L": -70.6, "g_L": 300.0, 'E_exc': 20.0,
                                'E_inh': -85.0, 'tau_syn_exc': 40.0, 'tau_syn_inh': 20.0},
                               "test_aeif_cond_alpha_nest.txt")])
    def test_nest_gpu_code_generator_aeif(self, neuron_model_name, params, nest_data_file_name):
        tolerance = 0.0001

        # Pass self and only iteration-specific parameters
        with mp.Pool(processes=1) as pool:
            result = pool.apply(self.run_aeif_simulation, (neuron_model_name, params))
            t, V_m = result

        nest_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      os.path.join("resources", nest_data_file_name))
        data = np.loadtxt(nest_data_file, delimiter="\t")
        t_nest = [x[0] for x in data]
        V_m_nest = [x[1] for x in data]

        dV = [V_m[i * 10 + 20] - V_m_nest[i] for i in range(len(t_nest))]
        rmse = np.std(dV) / abs(np.mean(V_m))
        print("rmse : ", rmse, " tolerance: ", tolerance)
        if rmse > tolerance:
            raise Exception(f"rmse: {rmse} > tolerance: {tolerance}")

        if TEST_PLOTS:
            plt.figure(1)
            plt.plot(t, V_m, "r-", label="NEST GPU")
            plt.plot(t_nest, V_m_nest, "b--", label="NEST")
            plt.legend()
            plt.draw()
            plt.savefig(f"{neuron_model_name}.png")

    def test_nest_gpu_code_generator_izhikevich(self):
        tolerance = 0.005
        neuron_model_name = "izhikevich_neuron_nestml"

        # Pass self and only iteration-specific parameters
        with mp.Pool(processes=1) as pool:
            result = pool.apply(self.run_izhikevich_simulation, (neuron_model_name,))
            t, V_m = result

        nest_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.join("resources", "test_izh_nest.txt"))
        data = np.loadtxt(nest_data_file, delimiter="\t")
        t_nest = [x[0] for x in data]
        V_m_nest = [x[1] for x in data]

        dV = [V_m[i + 2] - V_m_nest[i] for i in range(len(t_nest))]
        rmse = np.std(dV) / abs(np.mean(V_m))
        print("rmse : ", rmse, " tolerance: ", tolerance)
        if rmse > tolerance:
            raise Exception(f"rmse: {rmse} > tolerance: {tolerance}")

        if TEST_PLOTS:
            plt.figure(1)
            plt.plot(t, V_m, "r-", label="NEST GPU")
            plt.plot(t_nest, V_m_nest, "b--", label="NEST")
            plt.legend()
            plt.draw()
            plt.savefig("izhikevich_plot.png")
