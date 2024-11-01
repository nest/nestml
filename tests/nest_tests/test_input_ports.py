# -*- coding: utf-8 -*-
#
# test_input_ports.py
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

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


class TestInputPorts:
    """
    Tests the different kind of input ports supported in NESTML.
    """

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_input_ports(self):
        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "resources", "input_ports.nestml")))
        target_path = "target"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.Install(module_name)

        neuron = nest.Create("input_ports_nestml")

        # List of receptor types for the spiking input ports
        receptor_types = nest.GetStatus(neuron, "receptor_types")[0]

        spike_times = [
            [10., 44.],  # NMDA_SPIKES
            [12., 42.],  # AMPA_SPIKES
            [14., 40.],  # GABA_SPIKES
            [16., 38.],  # FOO_VEC_IDX_0
            [18., 36.],  # FOO_VEC_IDX_1
            [20., 34.],  # MY_SPIKES_VEC_IDX_0
            [22., 32.],  # MY_SPIKES_VEC_IDX_1
            [24., 30.],  # MY_SPIKES2_VEC_IDX_1
        ]
        sgs = nest.Create("spike_generator", len(spike_times))
        for i, sg in enumerate(sgs):
            sg.spike_times = spike_times[i]

        nest.Connect(sgs[0], neuron, syn_spec={"receptor_type": receptor_types["NMDA_SPIKES"], "weight": -1.0, "delay": 1.0})
        nest.Connect(sgs[1], neuron, syn_spec={"receptor_type": receptor_types["AMPA_SPIKES"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[2], neuron, syn_spec={"receptor_type": receptor_types["GABA_SPIKES"], "weight": -1.0, "delay": 1.0})
        nest.Connect(sgs[3], neuron, syn_spec={"receptor_type": receptor_types["FOO_VEC_IDX_0"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[4], neuron, syn_spec={"receptor_type": receptor_types["FOO_VEC_IDX_1"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[5], neuron, syn_spec={"receptor_type": receptor_types["MY_SPIKES_VEC_IDX_0"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[6], neuron, syn_spec={"receptor_type": receptor_types["MY_SPIKES_VEC_IDX_1"], "weight": 2.0, "delay": 1.0})
        nest.Connect(sgs[7], neuron, syn_spec={"receptor_type": receptor_types["MY_SPIKES2_VEC_IDX_1"], "weight": -3.0, "delay": 1.0})

        mm = nest.Create("multimeter", {"record_from": ["bar", "foo_spikes", "my_spikes_ip"]})
        nest.Connect(mm, neuron)

        nest.Simulate(50.)

        events = mm.get("events")
        connections = nest.GetConnections(target=neuron)

        # corresponds to ``bar += NMDA_spikes + 2 * AMPA_spikes - 3 * GABA_spikes`` in the update block
        assert events["bar"][-1] == len(spike_times[0]) * abs(connections.get("weight")[0]) \
               + 2 * len(spike_times[1]) * abs(connections.get("weight")[1]) \
               - 3 * len(spike_times[2]) * abs(connections.get("weight")[2])

        # corresponds to ``foo_spikes += foo[0] + 5.5 * foo[1]`` in the update block
        assert events["foo_spikes"][-1] == len(spike_times[3]) * abs(connections.get("weight")[3]) \
               + 5.5 * len(spike_times[4]) * abs(connections.get("weight")[4])

        # corresponds to ``my_spikes_ip += my_spikes[0] + my_spikes[1] - my_spikes2[1]`` in the update block
        assert events["my_spikes_ip"][-1] == len(spike_times[5]) * abs(connections.get("weight")[5]) \
               + len(spike_times[6]) * abs(connections.get("weight")[6]) \
               - len(spike_times[7]) * abs(connections.get("weight")[7])

    @pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                        reason="This test does not support NEST 2")
    def test_input_ports_in_loop(self):
        input_path = os.path.join(os.path.realpath(os.path.join(
            os.path.dirname(__file__), "resources", "input_ports_in_loop.nestml")))
        target_path = "target"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.Install(module_name)

        neuron = nest.Create("input_ports_loop_nestml")

        # List of receptor types for the spiking input ports
        receptor_types = nest.GetStatus(neuron, "receptor_types")[0]

        spike_times = [
            [10., 39.],  # NMDA_SPIKES
            [12., 37.],  # FOO_0
            [14., 35.],  # FOO_1
            [16., 33.],  # SPIKE_BUF_0
            [18., 31.],  # SPIKE_BUF_1
            [20., 29.],  # SPIKE_BUF_2
            [22., 27.],  # SPIKE_BUF_3
            [24., 25.],  # SPIKE_BUF_4
        ]
        sgs = nest.Create("spike_generator", len(spike_times))
        for i, sg in enumerate(sgs):
            sg.spike_times = spike_times[i]

        nest.Connect(sgs[0], neuron,
                     syn_spec={"receptor_type": receptor_types["NMDA_SPIKES"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[1], neuron,
                     syn_spec={"receptor_type": receptor_types["FOO_0"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[2], neuron,
                     syn_spec={"receptor_type": receptor_types["FOO_1"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[3], neuron, syn_spec={"receptor_type": receptor_types["SPIKE_BUF_0"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[4], neuron, syn_spec={"receptor_type": receptor_types["SPIKE_BUF_1"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[5], neuron,
                     syn_spec={"receptor_type": receptor_types["SPIKE_BUF_2"], "weight": 1.0, "delay": 1.0})
        nest.Connect(sgs[6], neuron,
                     syn_spec={"receptor_type": receptor_types["SPIKE_BUF_3"], "weight": 2.0, "delay": 1.0})
        nest.Connect(sgs[7], neuron,
                     syn_spec={"receptor_type": receptor_types["SPIKE_BUF_4"], "weight": 3.0, "delay": 1.0})

        mm = nest.Create("multimeter", {"record_from": ["bar", "foo_spikes", "MY_SPIKES_IP_2", "MY_SPIKES_IP_3", "MY_SPIKES_IP_4", "MY_SPIKES_IP_5", "MY_SPIKES_IP_6"]})
        nest.Connect(mm, neuron)

        nest.Simulate(41.)

        events = mm.get("events")
        assert events["bar"][-1] == 2.0
        assert events["foo_spikes"][-1] == 25.0
        assert events["MY_SPIKES_IP_2"][-1] == 2.0
        assert events["MY_SPIKES_IP_5"][-1] == 4.0
        assert events["MY_SPIKES_IP_6"][-1] == 6.0
