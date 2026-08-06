# -*- coding: utf-8 -*-
#
# test_nest_gpu_code_generator_analytic.py
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

# try to import matplotlib; set the result in the flag TEST_PLOTS
try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

from pynestml.frontend.pynestml_frontend import generate_nest_gpu_target


class TestNESTGPUAnalyticCodeGenerator:
    """
    Tests code generation for NEST GPU target for neuron models requiring analytic solver
    """

    def test_nest_gpu_code_generator_analytic(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))))
        target_path = "target_gpu"
        logging_level = "INFO"
        suffix = "_nestml"
        generate_nest_gpu_target(input_path, target_path,
                                 logging_level=logging_level,
                                 suffix=suffix)
        import nestgpu as ngpu
        tolerance = 1e-5

        neuron = ngpu.Create("iaf_psc_exp_neuron_nestml")
        sg = ngpu.Create("spike_generator")
        spike_times = [10.0, 15., 23., 25., 36., 55., 62., 100., 125., 222., 333., 400.0, 550., 700.]
        ngpu.SetStatus(sg, {"spike_times": spike_times})

        conn_spec = {"rule": "all_to_all"}
        syn_spec_exc = {"receptor": 0, "weight": 200.0, "delay": 1.0}
        syn_spec_in = {"receptor": 1, "weight": -1.0, "delay": 100.0}

        ngpu.Connect(sg, neuron, conn_spec, syn_spec_exc)
        ngpu.Connect(sg, neuron, conn_spec, syn_spec_in)

        record = ngpu.CreateRecord("", ["V_m"], [neuron[0]], [0])

        ngpu.Simulate(800.0)

        data_list = ngpu.GetRecordData(record)
        t = [row[0] for row in data_list]
        V_m = [row[1] for row in data_list]

        np.savetxt("test.out", data_list, delimiter="\t")
        nest_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/iaf_ps_exp_nest_data.txt")
        data = np.loadtxt(nest_data_file, delimiter="\t")
        t1 = [x[0] for x in data]
        V_m1 = [x[1] for x in data]

        # np.testing.assert_allclose(V_m, V_m1)
        dV = [V_m[i * 10 + 20] - V_m1[i] for i in range(len(t1))]
        rmse = np.std(dV) / abs(np.mean(V_m))
        print("rmse : ", rmse, " tolerance: ", tolerance)
        if rmse > tolerance:
            raise Exception(f"rmse: {rmse} > tolerance: {tolerance}")

        if TEST_PLOTS:
            plt.figure(1)
            plt.plot(t, V_m, "r-", label="NEST GPU")
            plt.plot(t1, V_m1, "b--", label="NEST")
            plt.legend()
            plt.draw()
            plt.savefig("plot.png")
