# -*- coding: utf-8 -*-
#
# test__concmech_model.py
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

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

# set to `True` to plot simulation traces
TEST_PLOTS = True
try:
    import matplotlib
    import matplotlib.pyplot as plt
except BaseException as e:
    # always set TEST_PLOTS to False if matplotlib can not be imported
    TEST_PLOTS = False


class TestCompartmentalConcmech:
    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(
            tests_path,
            "resources",
            "concmech.nestml"
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

        generate_nest_compartmental_target(
            input_path=input_path,
            target_path=target_path,
            module_name="concmech_mockup_module",
            suffix="_nestml",
            logging_level="DEBUG"
        )

        nest.Install("concmech_mockup_module.so")

    def test_concmech(self):
        """We test the concentration mechanism by comparing the concentration value at a certain critical point in
        time to a previously achieved value at this point"""
        cm = nest.Create('multichannel_test_model_nestml')

        params = {'C_m': 10.0, 'g_C': 0.0, 'g_L': 1.5, 'e_L': -70.0, 'gbar_Ca_HVA': 1.0, 'gbar_SK_E2': 1.0}

        cm.compartments = [
            {"parent_idx": -1, "params": params}
        ]

        cm.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA"}
        ]

        sg1 = nest.Create('spike_generator', 1, {'spike_times': [100.]})

        nest.Connect(sg1, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': 4.0, 'delay': 0.5, 'receptor_type': 0})

        mm = nest.Create('multimeter', 1, {'record_from': ['v_comp0', 'c_Ca0', 'i_tot_Ca_LVAst0', 'i_tot_Ca_HVA0', 'i_tot_SK_E20', 'm_Ca_HVA0', 'h_Ca_HVA0'], 'interval': .1})

        nest.Connect(mm, cm)

        nest.Simulate(1000.)

        res = nest.GetStatus(mm, 'events')[0]

        step_time_delta = res['times'][1] - res['times'][0]
        data_array_index = int(200 / step_time_delta)

        expected_conc = 0.03559438228347359

        fig, axs = plt.subplots(5)

        axs[0].plot(res['times'], res['v_comp0'], c='r', label='V_m_0')
        axs[1].plot(res['times'], res['c_Ca0'], c='y', label='c_Ca_0')
        axs[2].plot(res['times'], res['i_tot_Ca_HVA0'], c='b', label='i_tot_Ca_HVA0')
        axs[3].plot(res['times'], res['i_tot_SK_E20'], c='b', label='i_tot_SK_E20')
        axs[4].plot(res['times'], res['m_Ca_HVA0'], c='g', label='gating var m')
        axs[4].plot(res['times'], res['h_Ca_HVA0'], c='r', label='gating var h')

        axs[0].set_title('V_m_0')
        axs[1].set_title('c_Ca_0')
        axs[2].set_title('i_Ca_HVA_0')
        axs[3].set_title('i_tot_SK_E20')
        axs[4].set_title('gating vars')

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()
        axs[3].legend()
        axs[4].legend()

        plt.savefig("concmech test.png")

        assert res['c_Ca0'][data_array_index] == expected_conc, ("the concentration (left) is not as expected (right). (" + str(res['c_Ca0'][data_array_index]) + "!=" + str(expected_conc) + ")")
