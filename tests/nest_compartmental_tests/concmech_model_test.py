# -*- coding: utf-8 -*-
#
# concmech_model_test.py
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
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=.1))

        generate_nest_compartmental_target(input_path=os.path.join(os.path.realpath(os.path.dirname(__file__)), "resources", "concmech.nestml"),
                                           suffix="_nestml",
                                           logging_level="DEBUG",
                                           module_name="concmech_mockup_module")
        nest.Install("concmech_mockup_module")

    def test_concmech(self):
        cm = nest.Create('multichannel_test_model_nestml')

        soma_params = {'C_m': 10.0, 'g_c': 0.0, 'g_L': 1.5, 'e_L': -70.0, 'gbar_Ca_HVA': 1.0, 'gbar_Ca_LVAst': 0.0}
        dend_params = {'C_m': 0.1, 'g_c': 0.1, 'g_L': 0.1, 'e_L': -70.0}

        # nest.AddCompartment(cm, 0, -1, soma_params)
        cm.compartments = [
            {"parent_idx": -1, "params": soma_params}
            # {"parent_idx": 0, "params": dend_params},
            # {"parent_idx": 0, "params": dend_params}
        ]
        # nest.AddCompartment(cm, 1, 0, dend_params)
        # nest.AddCompartment(cm, 2, 0, dend_params)

        # cm.V_th = -50.

        cm.receptors = [
            {"comp_idx": 0, "receptor_type": "AMPA"}
            # {"comp_idx": 1, "receptor_type": "AMPA"},
            # {"comp_idx": 2, "receptor_type": "AMPA"}
        ]

        # syn_idx_GABA = 0
        # syn_idx_AMPA = 1
        # syn_idx_NMDA = 2

        # sg1 = nest.Create('spike_generator', 1, {'spike_times': [50., 100., 125., 137., 143., 146., 600.]})
        sg1 = nest.Create('spike_generator', 1, {'spike_times': [100., 1000., 1100., 1200., 1300., 1400., 1500., 1600., 1700., 1800., 1900., 2000., 5000.]})
        # sg1 = nest.Create('spike_generator', 1, {'spike_times': [(item*6000) for item in range(1, 20)]})
        # sg2 = nest.Create('spike_generator', 1, {'spike_times': [115., 155., 160., 162., 170., 254., 260., 272., 278.]})
        # sg3 = nest.Create('spike_generator', 1, {'spike_times': [250., 255., 260., 262., 270.]})

        nest.Connect(sg1, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': 4.0, 'delay': 0.5, 'receptor_type': 0})
        # nest.Connect(sg2, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': .2, 'delay': 0.5, 'receptor_type': 1})
        # nest.Connect(sg3, cm, syn_spec={'synapse_model': 'static_synapse', 'weight': .3, 'delay': 0.5, 'receptor_type': 2})

        mm = nest.Create('multimeter', 1, {'record_from': ['v_comp0', 'c_Ca0', 'i_tot_Ca_LVAst0', 'i_tot_Ca_HVA0'], 'interval': .1})

        nest.Connect(mm, cm)

        nest.Simulate(6000.)

        res = nest.GetStatus(mm, 'events')[0]

        fig, axs = plt.subplots(5)

        axs[0].plot(res['times'], res['v_comp0'], c='b', label='V_m_0')
        axs[1].plot(res['times'], res['i_tot_Ca_LVAst0'], c='r', label='i_Ca_LVAst_0')
        axs[1].plot(res['times'], res['i_tot_Ca_HVA0'], c='g', label='i_Ca_HVA_0')
        axs[2].plot(res['times'], res['c_Ca0'], c='r', label='c_Ca_0')

        axs[0].set_title('V_m_0')
        axs[1].set_title('i_Ca_HVA/LVA_0')
        axs[2].set_title('c_Ca_0')
        # plt.plot(res['times'], res['v_comp2'], c='g', label='V_m_2')

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()

        plt.savefig("concmech_test.png")
