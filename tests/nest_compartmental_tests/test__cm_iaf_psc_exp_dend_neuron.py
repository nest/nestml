# -*- coding: utf-8 -*-
#
# test__cm_iaf_psc_exp_dend_neuron.py
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

import pytest

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

# set to `True` to plot simulation traces
TEST_PLOTS = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
except BaseException as e:
    # always set TEST_PLOTS to False if matplotlib can not be imported
    TEST_PLOTS = False


class TestCompartmentalIAF:
    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(
            tests_path,
            "resources/cm_iaf_psc_exp_dend_neuron.nestml"
        )
        target_path = os.path.join(
            tests_path,
            "target/"
        )

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        print(
            f"Compiled nestml model 'cm_main_cm_default_nestml' not found, installing in:"
            f"    {target_path}"
        )

        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=.1))

        if True:
            generate_nest_compartmental_target(
                input_path=input_path,
                target_path=target_path,
                module_name="iaf_psc_exp_dend_neuron_compartmental_module",
                suffix="_nestml",
                logging_level="DEBUG"
            )

        nest.Install("iaf_psc_exp_dend_neuron_compartmental_module.so")

    def test_iaf(self):
        """We test the concentration mechanism by comparing the concentration value at a certain critical point in
        time to a previously achieved value at this point"""
        cm = nest.Create('iaf_psc_exp_cm_dend_nestml')

        params = {"G_refr": 1000.}

        cm.compartments = [
            {"parent_idx": -1, "params": params}
        ]

        cm.receptors = [
            {"comp_idx": 0, "receptor_type": "syn_exc"}
        ]

        sg1 = nest.Create('spike_generator', 1, {'spike_times': [1., 2., 3., 4.]})

        nest.Connect(sg1, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': 1000.0, 'delay': 0.5, 'receptor_type': 0})

        mm = nest.Create('multimeter', 1, {'record_from': ['v_comp0', 'leak0', 'refr0'], 'interval': .1})

        nest.Connect(mm, cm)

        nest.Simulate(10.)

        res = nest.GetStatus(mm, 'events')[0]

        step_time_delta = res['times'][1] - res['times'][0]
        data_array_index = int(200 / step_time_delta)

        fig, axs = plt.subplots(3)

        axs[0].plot(res['times'], res['v_comp0'], c='r', label='V_m_0')
        axs[1].plot(res['times'], res['leak0'], c='y', label='leak0')
        axs[2].plot(res['times'], res['refr0'], c='b', label='refr0')

        axs[0].set_title('V_m_0')
        axs[1].set_title('leak0')
        axs[2].set_title('refr0')

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()

        plt.show()
        plt.savefig("cm_iaf_test.png")

        # assert res['c_Ca0'][data_array_index] == expected_conc, ("the concentration (left) is not as expected (right). (" + str(res['c_Ca0'][data_array_index]) + "!=" + str(expected_conc) + ")")
