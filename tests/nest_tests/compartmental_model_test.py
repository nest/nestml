"""
Example comparison of a two-compartment model with an active dendritic
compartment and a two-compartment model with a passive dendritic compartment.
"""

import nest, pynestml
from pynestml.frontend.pynestml_frontend import to_nest, install_nest

import os
import unittest

import numpy as np
try:
    import matplotlib
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False

DT = .001

SOMA_PARAMS = {
    # passive parameters
    'C_m': 89.245535, # pF
    'g_c': 0.0, # soma has no parameters
    'g_L': 8.924572508, # nS
    'e_L': -75.0,
    # E-type specific
    'gbar_Na': 4608.698576715, # nS
    'e_Na': 60.,
    'gbar_K': 956.112772900, # nS
    'e_K': -90.
}
DEND_PARAMS_PASSIVE = {
    # passive parameters
    'C_m': 1.929929,
    'g_c': 1.255439494,
    'g_L': 0.192992878,
    'e_L': -75.0,
    # by default, active conducances are set to zero, so we don't need to specify
    # them explicitely
}
DEND_PARAMS_ACTIVE = {
    # passive parameters
    'C_m': 1.929929, # pF
    'g_c': 1.255439494, # nS
    'g_L': 0.192992878, # nS
    'e_L': -70.0, # mV
    # E-type specific
    'gbar_Na': 17.203212493, # nS
    'e_Na': 60., # mV
    'gbar_K': 11.887347450, # nS
    'e_K': -90. # mV
}


class CMTest(unittest.TestCase):

    def reset_nest(self):
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=DT))

    def install_nestml_model(self):
        print("Compiled nestml model \'cm_main_cm_default\' not found, installing...")

        path_nestml = pynestml.__path__[0]
        path_target = "target/"
        # get the path to the nest installation
        path_nest = nest.ll_api.sli_func("statusdict/prefix ::")

        if not os.path.exists(path_target):
                os.makedirs(path_target)

        to_nest(input_path=os.path.join(path_nestml, "../models/cm_default.nestml"),
                target_path=os.path.join(path_target, "compartmental_model/"),
                module_name="cm_defaultmodule",
                logging_level="ERROR")
        install_nest(os.path.join(path_target, "compartmental_model/"), path_nest)

        nest.Install("cm_defaultmodule")


    def get_model(self):
        if self.nestml_flag:
            try:
                nest.Install("cm_defaultmodule")

                cm_act = nest.Create("cm_main_cm_default")
                cm_pas = nest.Create("cm_main_cm_default")

            except nest.pynestkernel.NESTError as e:
                self.install_nestml_model()

                cm_act = nest.Create("cm_main_cm_default")
                cm_pas = nest.Create("cm_main_cm_default")

        else:
            cm_pas = nest.Create('cm_main')
            cm_act = nest.Create('cm_main')

        return cm_act, cm_pas

    def get_rec_list(self):
        if self.nestml_flag:
            return ['v_comp0', 'v_comp1',
                    'm_Na0', 'h_Na0', 'n_K0', 'm_Na1', 'h_Na1', 'n_K1',
                    'g_AN_AMPA1', 'g_AN_NMDA1']
        else:
            return ['v_comp0', 'v_comp1',
                    'm_Na_0', 'h_Na_0', 'n_K_0', 'm_Na_1', 'h_Na_1', 'n_K_1',
                    'g_r_AN_AMPA_1', 'g_d_AN_AMPA_1', 'g_r_AN_NMDA_1', 'g_d_AN_NMDA_1']

    def run_model(self):
        self.reset_nest()
        cm_act, cm_pas = self.get_model()

        # create a neuron model with a passive dendritic compartment
        nest.AddCompartment(cm_pas, 0, -1, SOMA_PARAMS)
        nest.AddCompartment(cm_pas, 1, 0, DEND_PARAMS_PASSIVE)
        # create a neuron model with an active dendritic compartment
        nest.AddCompartment(cm_act, 0, -1, SOMA_PARAMS)
        nest.AddCompartment(cm_act, 1, 0, DEND_PARAMS_ACTIVE)

        # set spike thresholds
        nest.SetStatus(cm_pas, {'V_th': -50.})
        nest.SetStatus(cm_act, {'V_th': -50.})

        # add somatic and dendritic receptor to passive dendrite model
        syn_idx_soma_pas = nest.AddReceptor(cm_pas, 0, "AMPA_NMDA")
        syn_idx_dend_pas = nest.AddReceptor(cm_pas, 1, "AMPA_NMDA")
        # add somatic and dendritic receptor to active dendrite model
        syn_idx_soma_act = nest.AddReceptor(cm_act, 0, "AMPA_NMDA")
        syn_idx_dend_act = nest.AddReceptor(cm_act, 1, "AMPA_NMDA")

        # create a two spike generators
        sg_soma = nest.Create('spike_generator', 1, {'spike_times': [10.,13.,16.]})
        sg_dend = nest.Create('spike_generator', 1, {'spike_times': [70.,73.,76.]})

        # connect spike generators to passive dendrite model (weight in nS)
        nest.Connect(sg_soma, cm_pas, syn_spec={
            'synapse_model': 'static_synapse', 'weight': 5., 'delay': 5*DT, 'receptor_type': syn_idx_soma_pas})
        nest.Connect(sg_dend, cm_pas, syn_spec={
            'synapse_model': 'static_synapse', 'weight': 2., 'delay': 5*DT, 'receptor_type': syn_idx_dend_pas})
        # connect spike generators to active dendrite model (weight in nS)
        nest.Connect(sg_soma, cm_act, syn_spec={
            'synapse_model': 'static_synapse', 'weight': 5., 'delay': 5*DT, 'receptor_type': syn_idx_soma_act})
        nest.Connect(sg_dend, cm_act, syn_spec={
            'synapse_model': 'static_synapse', 'weight': 2., 'delay': 5*DT, 'receptor_type': syn_idx_dend_act})

        # create multimeters to record state variables
        rec_list = self.get_rec_list()
        mm_pas = nest.Create('multimeter', 1, {'record_from': rec_list, 'interval': DT})
        mm_act = nest.Create('multimeter', 1, {'record_from': rec_list, 'interval': DT})
        # connect the multimeters to the respective neurons
        nest.Connect(mm_pas, cm_pas)
        nest.Connect(mm_act, cm_act)

        # simulate the models
        nest.Simulate(160.)
        res_pas = nest.GetStatus(mm_pas, 'events')[0]
        res_act = nest.GetStatus(mm_act, 'events')[0]

        return res_act, res_pas

    def test_compartmental_model(self):
        self.nestml_flag = False
        recordables_nest = self.get_rec_list()
        res_act_nest, res_pas_nest = self.run_model()

        self.nestml_flag = True
        recordables_nestml = self.get_rec_list()
        res_act_nestml, res_pas_nestml = self.run_model()

        # check if voltages, ion channels state variables are equal
        for var_nest, var_nestml in zip(recordables_nest[:8], recordables_nestml[:8]):
            self.assertTrue(np.allclose(res_act_nest[var_nest], res_act_nestml[var_nestml], atol=5e-1))

        # check if synaptic conductances are equal
        self.assertTrue(np.allclose(res_act_nest['g_r_AN_AMPA_1']+res_act_nest['g_d_AN_AMPA_1'],
                                    res_act_nestml['g_AN_AMPA1'], 5e-3))
        self.assertTrue(np.allclose(res_act_nest['g_r_AN_NMDA_1']+res_act_nest['g_d_AN_NMDA_1'],
                                    res_act_nestml['g_AN_NMDA1'], 5e-3))

        if TEST_PLOTS:
            w_legends = False

            plt.figure('voltage', figsize=(6,6))
            # NEST
            # plot voltage for somatic compartment
            ax_soma = plt.subplot(221)
            ax_soma.set_title('NEST')
            ax_soma.plot(res_pas_nest['times'], res_act_nestml['v_comp0'], c='b', label='passive dend')
            ax_soma.plot(res_act_nest['times'], res_act_nest['v_comp0'], c='b', ls='--', lw=2., label='active dend')
            ax_soma.set_xlabel(r'$t$ (ms)')
            ax_soma.set_ylabel(r'$v_{soma}$ (mV)')
            ax_soma.set_ylim((-90.,40.))
            if w_legends: ax_soma.legend(loc=0)
            # plot voltage for dendritic compartment
            ax_dend = plt.subplot(222)
            ax_dend.set_title('NEST')
            ax_dend.plot(res_pas_nest['times'], res_pas_nest['v_comp1'], c='r', label='passive dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['v_comp1'], c='r', ls='--', lw=2., label='active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'$v_{dend}$ (mV)')
            ax_dend.set_ylim((-90.,40.))
            if w_legends: ax_dend.legend(loc=0)

            ## NESTML
            # plot voltage for somatic compartment
            ax_soma = plt.subplot(223)
            ax_soma.set_title('NESTML')
            ax_soma.plot(res_pas_nestml['times'], res_pas_nestml['v_comp0'], c='b', label='passive dend')
            ax_soma.plot(res_act_nestml['times'], res_act_nestml['v_comp0'], c='b', ls='--', lw=2., label='active dend')
            ax_soma.set_xlabel(r'$t$ (ms)')
            ax_soma.set_ylabel(r'$v_{soma}$ (mV)')
            ax_soma.set_ylim((-90.,40.))
            if w_legends: ax_soma.legend(loc=0)
            # plot voltage for dendritic compartment
            ax_dend = plt.subplot(224)
            ax_dend.set_title('NESTML')
            ax_dend.plot(res_pas_nestml['times'], res_pas_nestml['v_comp1'], c='r', label='passive dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['v_comp1'], c='r', ls='--', lw=2., label='active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'$v_{dend}$ (mV)')
            ax_dend.set_ylim((-90.,40.))
            if w_legends: ax_dend.legend(loc=0)

            plt.figure('channel state variables', figsize=(6,6))
            ## NEST
            # plot traces for somatic compartment
            ax_soma = plt.subplot(221)
            ax_soma.set_title('NEST')
            ax_soma.plot(res_pas_nest['times'], res_pas_nest['m_Na_0'], c='b', label='m_Na passive dend')
            ax_soma.plot(res_pas_nest['times'], res_pas_nest['h_Na_0'], c='r', label='h_Na passive dend')
            ax_soma.plot(res_pas_nest['times'], res_pas_nest['n_K_0'], c='g', label='n_K passive dend')
            ax_soma.plot(res_act_nest['times'], res_act_nest['m_Na_0'], c='b', ls='--', lw=2., label='m_Na active dend')
            ax_soma.plot(res_act_nest['times'], res_act_nest['h_Na_0'], c='r', ls='--', lw=2., label='h_Na active dend')
            ax_soma.plot(res_act_nest['times'], res_act_nest['n_K_0'], c='g', ls='--', lw=2., label='n_K active dend')
            ax_soma.set_xlabel(r'$t$ (ms)')
            ax_soma.set_ylabel(r'svar')
            ax_soma.set_ylim((0.,1.))
            if w_legends: ax_soma.legend(loc=0)
            # plot voltage for dendritic compartment
            ax_dend = plt.subplot(222)
            ax_dend.set_title('NEST')
            ax_dend.plot(res_pas_nest['times'], res_pas_nest['m_Na_1'], c='b', label='m_Na passive dend')
            ax_dend.plot(res_pas_nest['times'], res_pas_nest['h_Na_1'], c='r', label='h_Na passive dend')
            ax_dend.plot(res_pas_nest['times'], res_pas_nest['n_K_1'], c='g', label='n_K passive dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['m_Na_1'], c='b', ls='--', lw=2., label='m_Na active dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['h_Na_1'], c='r', ls='--', lw=2., label='h_Na active dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['n_K_1'], c='g', ls='--', lw=2., label='n_K active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'svar')
            ax_dend.set_ylim((0.,1.))
            if w_legends: ax_dend.legend(loc=0)

            ## NESTML
            # plot traces for somatic compartment
            ax_soma = plt.subplot(223)
            ax_soma.set_title('NESTML')
            ax_soma.plot(res_pas_nestml['times'], res_pas_nestml['m_Na0'], c='b', label='m_Na passive dend')
            ax_soma.plot(res_pas_nestml['times'], res_pas_nestml['h_Na0'], c='r', label='h_Na passive dend')
            ax_soma.plot(res_pas_nestml['times'], res_pas_nestml['n_K0'], c='g', label='n_K passive dend')
            ax_soma.plot(res_act_nestml['times'], res_act_nestml['m_Na0'], c='b', ls='--', lw=2., label='m_Na active dend')
            ax_soma.plot(res_act_nestml['times'], res_act_nestml['h_Na0'], c='r', ls='--', lw=2., label='h_Na active dend')
            ax_soma.plot(res_act_nestml['times'], res_act_nestml['n_K0'], c='g', ls='--', lw=2., label='n_K active dend')
            ax_soma.set_xlabel(r'$t$ (ms)')
            ax_soma.set_ylabel(r'svar')
            ax_soma.set_ylim((0.,1.))
            if w_legends: ax_soma.legend(loc=0)
            # plot voltage for dendritic compartment
            ax_dend = plt.subplot(224)
            ax_dend.set_title('NESTML')
            ax_dend.plot(res_pas_nestml['times'], res_pas_nestml['m_Na1'], c='b', label='m_Na passive dend')
            ax_dend.plot(res_pas_nestml['times'], res_pas_nestml['h_Na1'], c='r', label='h_Na passive dend')
            ax_dend.plot(res_pas_nestml['times'], res_pas_nestml['n_K1'], c='g', label='n_K passive dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['m_Na1'], c='b', ls='--', lw=2., label='m_Na active dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['h_Na1'], c='r', ls='--', lw=2., label='h_Na active dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['n_K1'], c='g', ls='--', lw=2., label='n_K active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'svar')
            ax_dend.set_ylim((0.,1.))
            if w_legends: ax_dend.legend(loc=0)

            plt.figure('dendritic synapse conductances', figsize=(3,6))
            ## NEST
            # plot traces for dendritic compartment
            ax_dend = plt.subplot(211)
            ax_dend.set_title('NEST')
            ax_dend.plot(res_pas_nest['times'], res_pas_nest['g_r_AN_AMPA_1'] + res_pas_nest['g_d_AN_AMPA_1'], c='b', label='AMPA passive dend')
            ax_dend.plot(res_pas_nest['times'], res_pas_nest['g_r_AN_NMDA_1'] + res_pas_nest['g_d_AN_NMDA_1'], c='r', label='NMDA passive dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['g_r_AN_AMPA_1'] + res_act_nest['g_d_AN_AMPA_1'], c='b', ls='--', lw=2., label='AMPA active dend')
            ax_dend.plot(res_act_nest['times'], res_act_nest['g_r_AN_NMDA_1'] + res_act_nest['g_d_AN_NMDA_1'], c='r', ls='--', lw=2., label='NMDA active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'$g_{syn1}$ (uS)')
            if w_legends: ax_dend.legend(loc=0)
            # plot traces for dendritic compartment
            ## NESTML
            ax_dend = plt.subplot(212)
            ax_dend.set_title('NESTML')
            ax_dend.plot(res_pas_nestml['times'], res_pas_nestml['g_AN_AMPA1'], c='b', label='AMPA passive dend')
            ax_dend.plot(res_pas_nestml['times'], res_pas_nestml['g_AN_NMDA1'], c='r', label='NMDA passive dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['g_AN_AMPA1'], c='b', ls='--', lw=2., label='AMPA active dend')
            ax_dend.plot(res_act_nestml['times'], res_act_nestml['g_AN_NMDA1'], c='r', ls='--', lw=2., label='NMDA active dend')
            ax_dend.set_xlabel(r'$t$ (ms)')
            ax_dend.set_ylabel(r'$g_{syn1}$ (uS)')
            if w_legends: ax_dend.legend(loc=0)

            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    # cmtest = CMTest()
    # cmtest.get_nestml_model()
    # cmtest.test_compartmental_model()
    unittest.main()
