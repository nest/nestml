# -*- coding: utf-8 -*-
#
# test__continuous_input.py
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


class TestContinuousInput:
    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(
            tests_path,
            "resources",
            "adex_test.nestml"
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
            module_name="aeif_cond_alpha_neuron_module",
            suffix="_nestml",
            logging_level="DEBUG"
        )

        nest.Install("aeif_cond_alpha_neuron_module.so")

    def test_continuous_input(self):
        """We test the continuous input mechanism by just comparing the input current at a certain critical point in
        time to a previously achieved value at this point"""
        cm = nest.Create('aeif_cond_alpha_neuron_nestml')

        self.soma_params = {'C_m': self.C_m_s,  # [pF] Soma capacitance
                            'g_L': self.g_L_s,  # [nS] Soma leak conductance
                            'e_L': self.e_L_s,  # [mV] Soma reversal potential
                            'gbar_Na_Adex': self.g_L_s,  # [nS] Adex conductance
                            'e_Na_Adex': self.e_Na_Adex,  # [mV] Adex threshold
                            'delta_T': self.delta_T  # [mV] Adex slope factor
                            }

        self.distal_params = {'C_m': self.C_m_d,  # [pF] Distal capacitance
                              'g_L': self.g_L_d,  # [nS] Distal leak conductance
                              'g_C': self.g_C_d,  # [nS] Soma-distal coupling conductance
                              'e_L': self.e_L_d,  # [mV] Distal reversal potential
                              'gbar_Ca': self.gbar_Ca,  # [nS] Ca maximal conductance
                              'gbar_K_Ca': self.gbar_K_Ca,  # [nS] K_Ca maximal conductance
                              'e_K': self.e_K,  # [mV] K reversal potential
                              'tau_decay_Ca': self.tau_decay_Ca,  # [ms] decay of Ca concentration
                              'phi': self.phi,  # [-] scale factor
                              'm_half': self.m_half,  # [mV] m half-value for Ca
                              'h_half': self.h_half,  # [mV] h half-value for Ca
                              'm_slope': self.m_slope,  # [-] m slope factor for Ca
                              'h_slope': self.h_slope,  # [-] h slope factor for Ca
                              'tau_m': self.tau_m,  # [ms] m tau decay for Ca
                              'tau_h': self.tau_h,  # [ms] h tau decay dor Ca
                              'tau_m_K_Ca': self.tau_m_K_Ca,  # [ms] m tau decay for K_Ca
                              'Ca_0': self.default_param["Ca_0"],  # [mM] Baseline intracellular Ca conc
                              'Ca_th': self.Ca_th,  # [mM] Threshold Ca conc for Ca channel opening
                              'exp_K_Ca': self.exp_K_Ca  # [-] Exponential factor in K_Ca current with Hay dyn
                              }

        cm.compartments = [
            {"parent_idx": -1, "params": soma_params}
        ]

        cm.receptors = [
            {"comp_idx": 0, "receptor_type": "con_in"},
            {"comp_idx": 0, "receptor_type": "AMPA"}
        ]

        dcg = nest.Create("ac_generator", {"amplitude": 2.0, "start": 200, "stop": 800, "frequency": 20})

        nest.Connect(dcg, cm, syn_spec={"synapse_model": "static_synapse", "weight": 1.0, "delay": 0.1, "receptor_type": 0})

        sg1 = nest.Create('spike_generator', 1, {'spike_times': [205]})

        nest.Connect(sg1, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': 3.0, 'delay': 0.5, 'receptor_type': 1})

        mm = nest.Create('multimeter', 1, {'record_from': ['v_comp0', 'i_tot_con_in0', 'i_tot_AMPA0'], 'interval': .1})

        nest.Connect(mm, cm)

        nest.Simulate(1000.)

        res = nest.GetStatus(mm, 'events')[0]

        fig, axs = plt.subplots(2)

        axs[0].plot(res['times'], res['v_comp0'], c='b', label='V_m_0')
        axs[1].plot(res['times'], res['i_tot_con_in0'], c='r', label='continuous')
        axs[1].plot(res['times'], res['i_tot_AMPA0'], c='g', label='synapse')

        axs[0].set_title('V_m_0')
        axs[1].set_title('inputs')

        axs[0].legend()
        axs[1].legend()

        plt.savefig("continuous input test.png")

        step_time_delta = res['times'][1] - res['times'][0]
        data_array_index = int(212 / step_time_delta)

        if not res['i_tot_con_in0'][data_array_index] > 19.9 and res['i_tot_con_in0'][data_array_index] < 20.1:
            self.fail("the current (left) is not close enough to expected (right). (" + str(
                res['i_tot_con_in0'][data_array_index]) + " != " + "20.0 +- 0.1" + ")")
