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

        if True:
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
        I_s = 300

        aeif_dict = {
            "a": 0.,
            "b": 40.,
            "t_ref": 0.,
            "Delta_T": 2.,
            "C_m": 200.,
            "g_L": 10.,
            "E_L": -63.,
            "V_reset": -65.,
            "tau_w": 500.,
            "V_th": -50.,
            "V_peak": -40.,
        }

        aeif = nest.Create("aeif_cond_alpha", params=aeif_dict)

        cm = nest.Create('aeif_cond_alpha_neuron_nestml')

        soma_params = {
            "C_m": 362.5648533496359,
            "Ca_0": 0.0001,
            "Ca_th": 0.00043,
            "V_reset": -62.12885359171539,
            "Delta_T": 2.0,
            "E_K": -90.0,
            "E_L": -58.656837907086036,
            #"V_th": -50.0,
            "exp_K_Ca": 4.8,
            "g_C": 17.55192973190035,
            "g_L": 6.666182946322264,
            "g_Ca": 22.9883727668534,
            "g_K": 18.361017565618574,
            "h_half_Ca": -21.0,
            "h_slope_Ca": -0.5,
            "m_half_Ca": -9.0,
            "m_slope_Ca": 0.5,
            "phi_ca": 2.200252914099994e-08,
            #"refr_T": 0.0,
            "tau_Ca": 129.45363748885939,
            "tau_h_Ca": 80.0,
            "tau_m_Ca": 15.0,
            "tau_K": 1.0,
            "tau_w": 500.0,
            "SthA": 0,
            "b": 40.0,
            "V_peak": -40.0,
            "G_refr": 1000.
        }

        dendritic_params ={
            "C_m": 10.0,
            "E_L": -80.0,
            "g_L": 2.5088334130360064,
            "g_Ca": 22.9883727668534,
            "g_K": 18.361017565618574,
        }

        cm.compartments = [
            {"parent_idx": -1, "params": soma_params},
            {"parent_idx": 0, "params": dendritic_params}
        ]

        cm.receptors = [
            {"comp_idx": 0, "receptor_type": "I_syn_exc"}
        ]

        SimTime = 10
        stimulusStart = 0.0
        stimulusStop = SimTime
        countWindow = stimulusStop - stimulusStart

        # Poisson parameters
        spreading_factor = 4
        basic_rate = 600.0
        basic_weight = 0.6
        weight = basic_weight * spreading_factor
        rate = basic_rate / spreading_factor

        cf = 1.

        # Create and connct Poisson generator
        pg0 = nest.Create('poisson_generator', 20, params={'rate': rate, 'start': stimulusStart, 'stop': stimulusStop})
        nest.Connect(pg0, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': weight * cf, 'delay': 1.,
                                        'receptor_type': 0})
        nest.Connect(pg0, aeif, syn_spec={'synapse_model': 'static_synapse', 'weight': weight, 'delay': 1.})

        # create multimeters to record compartment voltages and various state variables
        rec_list = [
            'v_comp0', 'w0', 'i_tot_I_spike0', 'i_tot_I_syn_exc0', 'i_tot_refr0', 'i_tot_adapt0', 'i_tot_I_Ca0', 'i_tot_I_K0', 'c_Ca0',
        ]
        mm_cm = nest.Create('multimeter', 1, {'record_from': ['v_comp0', 'v_comp1', 'w0', 'i_tot_I_spike0', 'i_tot_I_syn_exc0', 'i_tot_refr0', 'i_tot_adapt0', 'i_tot_I_Ca0', 'i_tot_I_K0', 'c_Ca0'], 'interval': .1})
        mm_aeif = nest.Create('multimeter', 1, {'record_from': ['V_m', 'w'], 'interval': .1})
        nest.Connect(mm_cm, cm)
        nest.Connect(mm_aeif, aeif)

        # create and connect a spike recorder
        sr_cm = nest.Create('spike_recorder')
        sr_aeif = nest.Create('spike_recorder')
        nest.Connect(cm, sr_cm)
        nest.Connect(aeif, sr_aeif)

        nest.Simulate(SimTime)

        print('I_s current = ', I_s)

        res_cm = nest.GetStatus(mm_cm, 'events')[0]
        events_cm = nest.GetStatus(sr_cm)[0]['events']
        res_aeif = nest.GetStatus(mm_aeif, 'events')[0]
        events_aeif = nest.GetStatus(sr_aeif)[0]['events']

        totalSpikes_cm = sum(map(lambda x: x > stimulusStart and x < stimulusStop, events_cm['times']))
        totalSpikes_aeif = sum(map(lambda x: x > stimulusStart and x < stimulusStop, events_aeif['times']))
        print("Total spikes multiComp = ", totalSpikes_cm)
        print("Total spikes adex      = ", totalSpikes_aeif)
        print("FR multiComp           = ", totalSpikes_cm * 1000 / countWindow)
        print("FR adex                = ", totalSpikes_aeif * 1000 / countWindow)

        print("Spike times multiComp:\n")
        print(events_cm['times'])
        print("Spike times adex:\n")
        print(events_aeif['times'])

        stdtest = True

        if stdtest:
            plt.figure('ISI @ Is = ' + str(I_s))
            ###############################################################################
            plt.subplot(411)
            plt.plot(res_aeif['times'], res_aeif['V_m'], c='r', label='v_m adex')
            plt.plot(res_cm['times'], res_cm['v_comp0'], c='b', label='v_m soma cm')
            plt.plot(res_cm['times'], res_cm['v_comp1'], c='g', label='v_m dist cm')
            plt.legend()
            plt.xlim(0, SimTime)
            plt.ylabel('Vm [mV]')
            plt.title('MultiComp (blue) and adex (red) voltage')

            plt.subplot(412)
            # plt.plot(res_cm['times'], res_cm['m_Ca_1'], c='b', ls='--', lw=2., label='m')
            # plt.plot(res_cm['times'], res_cm['h_Ca_1'], c='r', ls='--', lw=2., label='h')
            # plt.plot(res_cm['times'], res_cm['m_Ca_1']*res_cm['h_Ca_1'], c='k', ls='--', lw=2., label='g')
            plt.legend()
            plt.xlim(0, SimTime)
            plt.ylabel('Ca')
            plt.title('Distal Ca activation')

            plt.subplot(413)
            plt.plot(res_cm['times'], res_cm['w0'], c='b', ls='--', lw=2., label='W cm')
            plt.plot(res_aeif['times'], res_aeif['w'], c='r', ls='--', lw=2., label='W adex')
            plt.legend()
            plt.xlim(0, SimTime)
            plt.ylabel('W')
            plt.title('Adaptation')

            plt.subplot(414)
            events_cm = nest.GetStatus(sr_cm)[0]['events']
            plt.eventplot(events_cm['times'], linelengths=0.2, color='b')
            events_aeif = nest.GetStatus(sr_aeif)[0]['events']
            plt.eventplot(events_aeif['times'], linelengths=0.2, color='r')
            plt.xlim(0, SimTime)
            plt.ylabel('Spikes')
            plt.title('Raster - cm (blue) VS adex (red)')
            plt.xlabel('Time [ms]')

            #plt.show()
        #else:
            fig, axs = plt.subplots(7)

            axs[0].plot(res_cm['times'], res_cm['i_tot_I_spike0'], c='b', label='I_spike0')
            axs[1].plot(res_cm['times'], res_cm['i_tot_I_syn_exc0'], c='b', label='I_syn_exc0')
            #plt.plot(res_cm['times'], res_cm['i_tot_I_syn_inh0'], c='b', label='3')
            #plt.plot(res_cm['times'], res_cm['i_tot_external_stim0'], c='b', label='4')
            axs[2].plot(res_cm['times'], res_cm['i_tot_refr0'], c='b', label='refr0')
            axs[3].plot(res_cm['times'], res_cm['i_tot_adapt0'], c='b', label='adapt0')
            axs[4].plot(res_cm['times'], res_cm['i_tot_I_Ca0'], c='b', label='I_Ca0')
            axs[5].plot(res_cm['times'], res_cm['i_tot_I_K0'], c='b', label='I_K0')
            axs[6].plot(res_cm['times'], res_cm['c_Ca0'], c='b', label='c_Ca0')

            axs[0].legend()
            axs[1].legend()
            axs[2].legend()
            axs[3].legend()
            axs[4].legend()
            axs[5].legend()
            axs[6].legend()

            plt.show()
