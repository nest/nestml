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


class TestSelfSpikeConvolutions:
    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(
            tests_path,
            "resources",
            "self_spike_convolutions.nestml"
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
                module_name="self_spike_convolutions_module",
                suffix="_nestml",
                logging_level="DEBUG"
            )

        nest.Install("self_spike_convolutions_module.so")

    def test_self_spike_convolutions(self):
        """We test the concentration mechanism by comparing the concentration value at a certain critical point in
        time to a previously achieved value at this point"""
        cm = nest.Create('self_spikes_convolutions_nestml')

        cm.compartments = [
            {"parent_idx": -1}
        ]

        cm.receptors = [
            {"comp_idx": 0, "receptor_type": "rec_primary"},
            {"comp_idx": 0, "receptor_type": "rec_secondary"},
            {"comp_idx": 0, "receptor_type": "con_in_primary"},
            {"comp_idx": 0, "receptor_type": "con_in_secondary"},
        ]

        sg1 = nest.Create('spike_generator', 1, {'spike_times': [50.]})
        dcg = nest.Create("dc_generator", {"amplitude": 2.0, "start": 40, "stop": 60})

        nest.Connect(sg1, cm,
                     syn_spec={'synapse_model': 'static_synapse', 'weight': 4.0, 'delay': 0.5, 'receptor_type': 0})
        nest.Connect(sg1, cm,
                     syn_spec={'synapse_model': 'static_synapse', 'weight': 4.0, 'delay': 0.5, 'receptor_type': 1})
        nest.Connect(dcg, cm,
                     syn_spec={'synapse_model': 'static_synapse', 'weight': 1.0, 'delay': 0.1, 'receptor_type': 2})
        nest.Connect(dcg, cm,
                     syn_spec={'synapse_model': 'static_synapse', 'weight': 1.0, 'delay': 0.1, 'receptor_type': 3})

        mm = nest.Create('multimeter', 1, {'record_from': ['v_comp0', 'chan_primary0', 'chan_secondary0',
                                                           'rec_primary0', 'rec_secondary1',
                                                           'con_in_primary2', 'con_in_secondary3',
                                                           'concentration0'], 'interval': .1})

        nest.Connect(mm, cm)

        spikedet = nest.Create("spike_recorder")
        nest.Connect(cm, spikedet)
        spikes_rec = nest.GetStatus(spikedet, 'events')[0]

        nest.Simulate(200.)

        res = nest.GetStatus(mm, 'events')[0]

        fig, axs = plt.subplots(8)

        axs[0].plot(res['times'], res['v_comp0'], c='r', label='V_m_0')
        axs[1].plot(res['times'], res['chan_primary0'], c='g', label='chan_primary')
        axs[2].plot(res['times'], res['chan_secondary0'], c='g', label='chan_secondary')
        axs[3].plot(res['times'], res['rec_primary0'], c='orange', label='input0')
        axs[4].plot(res['times'], res['rec_secondary1'], c='orange', label='input1')
        axs[5].plot(res['times'], res['con_in_primary2'], c='orange', label='input2')
        axs[6].plot(res['times'], res['con_in_secondary3'], c='orange', label='input3')
        axs[7].plot(res['times'], res['concentration0'], c='b', label='concentration')

        label_set = False
        for spike in spikes_rec['times']:
            for ax in axs:
                if (label_set):
                    ax.axvline(x=spike, color='purple', linestyle='--', linewidth=1)
                else:
                    ax.axvline(x=spike, color='purple', linestyle='--', linewidth=1, label="self_spikes")
                    label_set = True

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()
        axs[3].legend()
        axs[4].legend()
        axs[5].legend()
        axs[6].legend()
        axs[7].legend()

        plt.savefig("self_spike_convolutions.png")

        plt.show()
