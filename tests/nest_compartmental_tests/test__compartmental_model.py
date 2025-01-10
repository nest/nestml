# -*- coding: utf-8 -*-
#
# test__compartmental_model.py
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
import copy
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

dt = .001

soma_params = {
    # passive parameters
    'C_m': 89.245535,  # pF
    'g_C': 0.0,  # soma has no parent
    'g_L': 8.924572508,  # nS
    'e_L': -75.0,
    # E-type specific
    'gbar_Na': 4608.698576715,  # nS
    'e_Na': 60.,
    'gbar_K': 956.112772900,  # nS
    'e_K': -90.
}
dend_params_passive = {
    # passive parameters
    'C_m': 1.929929,
    'g_C': 1.255439494,
    'g_L': 0.192992878,
    'e_L': -75.0,
    # by default, active conducances are set to zero, so we don't need to specify
    # them explicitely
}
dend_params_active = {
    # passive parameters
    'C_m': 1.929929,  # pF
    'g_C': 1.255439494,  # nS
    'g_L': 0.192992878,  # nS
    'e_L': -75.0,  # mV
    # E-type specific
    'gbar_Na': 17.203212493,  # nS
    'e_Na': 60.,  # mV
    'gbar_K': 11.887347450,  # nS
    'e_K': -90.  # mV
}


class TestCM():

    def reset_nest(self):
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=dt))

    def install_nestml_model(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(
            tests_path,
            "resources",
            "cm_default.nestml"
        )
        target_path = os.path.join(
            tests_path,
            "target/"
        )

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        print(
            f"Compiled nestml model 'cm_main_cm_default_nestml' not found, installing in:"
            f"    {target_path}")

        generate_nest_compartmental_target(
            input_path=input_path,
            target_path=target_path,
            module_name="cm_defaultmodule",
            suffix="_nestml",
            logging_level="ERROR"
        )

    def get_model(self, reinstall_flag=True):
        if self.nestml_flag:
            # Currently, we have no way of checking whether the *.so-file
            # associated with the model is in {nest build directory}/lib/nest,
            # so we only check the reinstall flag, which should be set to True
            # unless the testcase is being debugged
            if reinstall_flag:
                self.install_nestml_model()

            print("Instantiating NESTML compartmental model")

            nest.Install("cm_defaultmodule")

            cm_act = nest.Create("cm_default_nestml")
            cm_pas = nest.Create("cm_default_nestml")
        else:
            print("Instantiating NEST compartmental model")
            # default model built into NEST Simulator
            cm_pas = nest.Create('cm_default')
            cm_act = nest.Create('cm_default')

        return cm_act, cm_pas

    def get_rec_list(self):
        if self.nestml_flag:
            return [
                'v_comp0', 'v_comp1',
                'm_Na0', 'h_Na0', 'n_K0', 'm_Na1', 'h_Na1', 'n_K1',
                'g_AN_AMPA1', 'g_AN_NMDA1'
            ]
        else:
            return [
                'v_comp0',
                'v_comp1',
                'm_Na_0',
                'h_Na_0',
                'n_K_0',
                'm_Na_1',
                'h_Na_1',
                'n_K_1',
                'g_r_AN_AMPA_1',
                'g_d_AN_AMPA_1',
                'g_r_AN_NMDA_1',
                'g_d_AN_NMDA_1']

    def run_model(self):
        self.reset_nest()
        cm_act, cm_pas = self.get_model()

        # accomodate new initialization convention in NEST 3.6
        soma_params_ = copy.deepcopy(soma_params)
        dend_params_passive_ = copy.deepcopy(dend_params_passive)
        dend_params_active_ = copy.deepcopy(dend_params_active)
        if not self.nestml_flag:
            soma_params_["v_comp"] = soma_params_["e_L"]
            dend_params_passive_["v_comp"] = dend_params_passive_["e_L"]
            dend_params_active_["v_comp"] = dend_params_active_["e_L"]

        # create a neuron model with a passive dendritic compartment
        cm_pas.compartments = [
            {"parent_idx": -1, "params": soma_params_},
            {"parent_idx": 0, "params": dend_params_passive_}
        ]

        # create a neuron model with an active dendritic compartment
        cm_act.compartments = [
            {"parent_idx": -1, "params": soma_params_},
            {"parent_idx": 0, "params": dend_params_active_}
        ]

        # set spike thresholds
        cm_pas.V_th = -50.
        cm_act.V_th = -50.

        # add somatic and dendritic receptor to passive dendrite model
        cm_pas.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA_NMDA"},
            {"comp_idx": 1, "receptor_type": "AMPA_NMDA"}
        ]
        syn_idx_soma_pas = 0
        syn_idx_dend_pas = 1

        # add somatic and dendritic receptor to active dendrite model
        cm_act.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA_NMDA"},
            {"comp_idx": 1, "receptor_type": "AMPA_NMDA"}
        ]
        syn_idx_soma_act = 0
        syn_idx_dend_act = 1

        # create a two spike generators
        sg_soma = nest.Create('spike_generator', 1, {
                              'spike_times': [10., 13., 16.]})
        sg_dend = nest.Create('spike_generator', 1, {
                              'spike_times': [70., 73., 76.]})

        # connect spike generators to passive dendrite model (weight in nS)
        nest.Connect(
            sg_soma,
            cm_pas,
            syn_spec={
                'synapse_model': 'static_synapse',
                'weight': 5.,
                'delay': .5,
                'receptor_type': syn_idx_soma_pas})
        nest.Connect(
            sg_dend,
            cm_pas,
            syn_spec={
                'synapse_model': 'static_synapse',
                'weight': 2.,
                'delay': .5,
                'receptor_type': syn_idx_dend_pas})
        # connect spike generators to active dendrite model (weight in nS)
        nest.Connect(
            sg_soma,
            cm_act,
            syn_spec={
                'synapse_model': 'static_synapse',
                'weight': 5.,
                'delay': .5,
                'receptor_type': syn_idx_soma_act})
        nest.Connect(
            sg_dend,
            cm_act,
            syn_spec={
                'synapse_model': 'static_synapse',
                'weight': 2.,
                'delay': .5,
                'receptor_type': syn_idx_dend_act})

        # create multimeters to record state variables
        rec_list = self.get_rec_list()
        mm_pas = nest.Create(
            'multimeter', 1, {
                'record_from': rec_list, 'interval': dt})
        mm_act = nest.Create(
            'multimeter', 1, {
                'record_from': rec_list, 'interval': dt})
        # connect the multimeters to the respective neurons
        nest.Connect(mm_pas, cm_pas)
        nest.Connect(mm_act, cm_act)

        # simulate the models
        nest.Simulate(160.)
        res_pas = nest.GetStatus(mm_pas, 'events')[0]
        res_act = nest.GetStatus(mm_act, 'events')[0]

        return res_act, res_pas

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_compartmental_model(self):
        """We numerically compare the output of the standard nest compartmental model to the equivalent nestml
        compartmental model"""
        self.nestml_flag = False
        recordables_nest = self.get_rec_list()
        res_act_nest, res_pas_nest = self.run_model()

        self.nestml_flag = True
        recordables_nestml = self.get_rec_list()
        res_act_nestml, res_pas_nestml = self.run_model()

        if TEST_PLOTS:
            w_legends = False

            plt.figure('voltage', figsize=(6, 6))
            # NEST
            # plot voltage for somatic compartment
            ax_soma = plt.subplot(221)
            ax_soma.set_title('NEST')
            ax_soma.plot(
                res_pas_nest['times'],
                res_pas_nest['v_comp0'],
                c='b',
                label='passive dend')
            ax_soma.plot(res_act_nest['times'], res_act_nest['v_comp0'],
                         c='b', ls='--', lw=2., label='active dend')
            ax_soma.plot(res_act_nestml['times'], res_act_nestml['v_comp0'],
                         c='r', ls=':', lw=2., label='active dend')
            ax_soma.set_xlabel(r'$t$ (ms)')
            ax_soma.set_ylabel(r'$v_{soma}$ (mV)')
            ax_soma.set_ylim((-90., 40.))
            if w_legends:
                ax_soma.legend(loc=0)
            # plot voltage for dendritic compartment
            ax_dend = plt.subplot(222)
            ax_dend.set_title('NEST')
            ax_dend.plot(
                res_pas_nest['times'],
                res_pas_nest['v_comp1'],
                c='r',
                label='passive dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['v_comp1'],
                         c='r', ls='--', lw=2., label='active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'$v_{dend}$ (mV)')
            ax_dend.set_ylim((-90., 40.))
            if w_legends:
                ax_dend.legend(loc=0)

            # NESTML
            # plot voltage for somatic compartment
            ax_soma = plt.subplot(223)
            ax_soma.set_title('NESTML')
            ax_soma.plot(
                res_pas_nestml['times'],
                res_pas_nestml['v_comp0'],
                c='b',
                label='passive dend')
            ax_soma.plot(res_act_nestml['times'], res_act_nestml['v_comp0'],
                         c='b', ls='--', lw=2., label='active dend')
            ax_soma.set_xlabel(r'$t$ (ms)')
            ax_soma.set_ylabel(r'$v_{soma}$ (mV)')
            ax_soma.set_ylim((-90., 40.))
            if w_legends:
                ax_soma.legend(loc=0)
            # plot voltage for dendritic compartment
            ax_dend = plt.subplot(224)
            ax_dend.set_title('NESTML')
            ax_dend.plot(
                res_pas_nestml['times'],
                res_pas_nestml['v_comp1'],
                c='r',
                label='passive dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['v_comp1'],
                         c='r', ls='--', lw=2., label='active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'$v_{dend}$ (mV)')
            ax_dend.set_ylim((-90., 40.))
            if w_legends:
                ax_dend.legend(loc=0)
            plt.savefig("compartmental_model_test - voltage.png")

            plt.figure('channel state variables', figsize=(6, 6))
            # NEST
            # plot traces for somatic compartment
            ax_soma = plt.subplot(221)
            ax_soma.set_title('NEST')
            ax_soma.plot(
                res_pas_nest['times'],
                res_pas_nest['m_Na_0'],
                c='b',
                label='m_Na passive dend')
            ax_soma.plot(
                res_pas_nest['times'],
                res_pas_nest['h_Na_0'],
                c='r',
                label='h_Na passive dend')
            ax_soma.plot(
                res_pas_nest['times'],
                res_pas_nest['n_K_0'],
                c='g',
                label='n_K passive dend')
            ax_soma.plot(res_act_nest['times'], res_act_nest['m_Na_0'],
                         c='b', ls='--', lw=2., label='m_Na active dend')
            ax_soma.plot(res_act_nest['times'], res_act_nest['h_Na_0'],
                         c='r', ls='--', lw=2., label='h_Na active dend')
            ax_soma.plot(res_act_nest['times'], res_act_nest['n_K_0'],
                         c='g', ls='--', lw=2., label='n_K active dend')
            ax_soma.set_xlabel(r'$t$ (ms)')
            ax_soma.set_ylabel(r'svar')
            ax_soma.set_ylim((0., 1.))
            if w_legends:
                ax_soma.legend(loc=0)
            # plot voltage for dendritic compartment
            ax_dend = plt.subplot(222)
            ax_dend.set_title('NEST')
            ax_dend.plot(
                res_pas_nest['times'],
                res_pas_nest['m_Na_1'],
                c='b',
                label='m_Na passive dend')
            ax_dend.plot(
                res_pas_nest['times'],
                res_pas_nest['h_Na_1'],
                c='r',
                label='h_Na passive dend')
            ax_dend.plot(
                res_pas_nest['times'],
                res_pas_nest['n_K_1'],
                c='g',
                label='n_K passive dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['m_Na_1'],
                         c='b', ls='--', lw=2., label='m_Na active dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['h_Na_1'],
                         c='r', ls='--', lw=2., label='h_Na active dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['n_K_1'],
                         c='g', ls='--', lw=2., label='n_K active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'svar')
            ax_dend.set_ylim((0., 1.))
            if w_legends:
                ax_dend.legend(loc=0)

            # NESTML
            # plot traces for somatic compartment
            ax_soma = plt.subplot(223)
            ax_soma.set_title('NESTML')
            ax_soma.plot(
                res_pas_nestml['times'],
                res_pas_nestml['m_Na0'],
                c='b',
                label='m_Na passive dend')
            ax_soma.plot(
                res_pas_nestml['times'],
                res_pas_nestml['h_Na0'],
                c='r',
                label='h_Na passive dend')
            ax_soma.plot(
                res_pas_nestml['times'],
                res_pas_nestml['n_K0'],
                c='g',
                label='n_K passive dend')
            ax_soma.plot(res_act_nestml['times'], res_act_nestml['m_Na0'],
                         c='b', ls='--', lw=2., label='m_Na active dend')
            ax_soma.plot(res_act_nestml['times'], res_act_nestml['h_Na0'],
                         c='r', ls='--', lw=2., label='h_Na active dend')
            ax_soma.plot(res_act_nestml['times'], res_act_nestml['n_K0'],
                         c='g', ls='--', lw=2., label='n_K active dend')
            ax_soma.set_xlabel(r'$t$ (ms)')
            ax_soma.set_ylabel(r'svar')
            ax_soma.set_ylim((0., 1.))
            if w_legends:
                ax_soma.legend(loc=0)
            # plot voltage for dendritic compartment
            ax_dend = plt.subplot(224)
            ax_dend.set_title('NESTML')
            ax_dend.plot(
                res_pas_nestml['times'],
                res_pas_nestml['m_Na1'],
                c='b',
                label='m_Na passive dend')
            ax_dend.plot(
                res_pas_nestml['times'],
                res_pas_nestml['h_Na1'],
                c='r',
                label='h_Na passive dend')
            ax_dend.plot(
                res_pas_nestml['times'],
                res_pas_nestml['n_K1'],
                c='g',
                label='n_K passive dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['m_Na1'],
                         c='b', ls='--', lw=2., label='m_Na active dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['h_Na1'],
                         c='r', ls='--', lw=2., label='h_Na active dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['n_K1'],
                         c='g', ls='--', lw=2., label='n_K active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'svar')
            ax_dend.set_ylim((0., 1.))
            if w_legends:
                ax_dend.legend(loc=0)
            plt.savefig(
                "compartmental_model_test - channel state variables.png")

            plt.figure('dendritic synapse conductances', figsize=(3, 6))
            # NEST
            # plot traces for dendritic compartment
            ax_dend = plt.subplot(211)
            ax_dend.set_title('NEST')
            ax_dend.plot(
                res_pas_nest['times'],
                res_pas_nest['g_r_AN_AMPA_1'] + res_pas_nest['g_d_AN_AMPA_1'],
                c='b',
                label='AMPA passive dend')
            ax_dend.plot(
                res_pas_nest['times'],
                res_pas_nest['g_r_AN_NMDA_1'] + res_pas_nest['g_d_AN_NMDA_1'],
                c='r',
                label='NMDA passive dend')
            ax_dend.plot(
                res_act_nest['times'],
                res_act_nest['g_r_AN_AMPA_1'] + res_act_nest['g_d_AN_AMPA_1'],
                c='b',
                ls='--',
                lw=2.,
                label='AMPA active dend')
            ax_dend.plot(
                res_act_nest['times'],
                res_act_nest['g_r_AN_NMDA_1'] + res_act_nest['g_d_AN_NMDA_1'],
                c='r',
                ls='--',
                lw=2.,
                label='NMDA active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'$g_{syn1}$ (uS)')
            if w_legends:
                ax_dend.legend(loc=0)
            # plot traces for dendritic compartment
            # NESTML
            ax_dend = plt.subplot(212)
            ax_dend.set_title('NESTML')
            ax_dend.plot(
                res_pas_nestml['times'],
                res_pas_nestml['g_AN_AMPA1'],
                c='b',
                label='AMPA passive dend')
            ax_dend.plot(
                res_pas_nestml['times'],
                res_pas_nestml['g_AN_NMDA1'],
                c='r',
                label='NMDA passive dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['g_AN_AMPA1'],
                         c='b', ls='--', lw=2., label='AMPA active dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['g_AN_NMDA1'],
                         c='r', ls='--', lw=2., label='NMDA active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'$g_{syn1}$ (uS)')
            if w_legends:
                ax_dend.legend(loc=0)

            plt.tight_layout()
            plt.savefig(
                "compartmental_model_test - dendritic synapse conductances.png")

        # check if voltages, ion channels state variables are equal
        for var_nest, var_nestml in zip(
                recordables_nest[:8], recordables_nestml[:8]):
            if var_nest == "v_comp0":
                atol = 1.0
            elif var_nest == "v_comp1":
                atol = 0.3
            else:
                atol = 0.02
            assert (np.allclose(
                res_act_nest[var_nest], res_act_nestml[var_nestml], atol=atol
            ))
        for var_nest, var_nestml in zip(
                recordables_nest[:8], recordables_nestml[:8]):
            if not var_nest in ["h_Na_1", "m_Na_1", "n_K_1"]:
                if var_nest == "v_comp0":
                    atol = 1.0
                elif var_nest == "v_comp1":
                    atol = 0.3
                else:
                    atol = 0.02
                assert (np.allclose(
                    res_pas_nest[var_nest], res_pas_nestml[var_nestml], atol=atol
                ))

        # check if synaptic conductances are equal
        assert (
            np.allclose(
                res_act_nest['g_r_AN_AMPA_1'] + res_act_nest['g_d_AN_AMPA_1'],
                res_act_nestml['g_AN_AMPA1'],
                5e-3))
        assert (
            np.allclose(
                res_act_nest['g_r_AN_NMDA_1'] + res_act_nest['g_d_AN_NMDA_1'],
                res_act_nestml['g_AN_NMDA1'],
                5e-3))
