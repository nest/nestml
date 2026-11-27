# -*- coding: utf-8 -*-
#
# test_set_status_invariants.py
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


class TestSetStatusInvariants:
    r"""
    Test that when setting parameters or state variables on a neuron or synapse in NEST using ``set()`` (``SetStatus()``), either all of the new values are set, or, if any of the new values is invalid (in particular, if any of the invariants (guards) specified in the model, like ``[[C_m > 0 pF]]``, is violated), none of the new values are set and an exception is raised.
    """

    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml"
    synapse_model_name = "stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    @pytest.fixture(autouse=True, scope="module")
    def generate_model_code(self):
        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "stdp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, s)) for s in files]
        codegen_opts = {"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                  "synapses": {"stdp_synapse": {"post_ports": ["post_spikes"]}}}],
                        "weight_variable": {"stdp_synapse": "w"}}
        generate_nest_target(input_path=input_path,
                             target_path="target_set_status_invariants",
                             logging_level="WARNING",
                             module_name="nestml_set_status_invariants_module",
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

    @pytest.fixture(autouse=True)
    def reset_kernel(self):
        nest.ResetKernel()
        nest.Install("nestml_set_status_invariants_module")

    def _create_neuron(self):
        neuron = nest.Create(self.neuron_model_name)
        neuron.set({"C_m": 250., "tau_m": 10., "V_m": -70.})
        return neuron

    def _create_connection(self):
        pre = nest.Create("parrot_neuron")
        post = nest.Create(self.neuron_model_name)
        nest.Connect(pre, post, syn_spec={"synapse_model": self.synapse_model_name, "w": 1., "delay": 1.})
        conn = nest.GetConnections(source=pre, synapse_model=self.synapse_model_name)
        return conn

    def _assert_rejected(self, obj, new_values, unchanged_keys):
        old_values = {key: obj.get(key) for key in unchanged_keys}
        with pytest.raises(nest.NESTError):
            obj.set(new_values)

        for key, old_value in old_values.items():
            assert obj.get(key) == old_value, "Value of \"" + key + "\" was changed by a set() call that was rejected"

    def test_neuron_valid_values_are_set(self):
        neuron = self._create_neuron()
        neuron.set({"C_m": 100., "refr_T": 0., "V_m": -60.})
        assert neuron.get("C_m") == 100.
        assert neuron.get("refr_T") == 0.
        assert neuron.get("V_m") == -60.

    @pytest.mark.parametrize("new_values", [{"C_m": -1.},
                                            {"tau_m": 0.},
                                            {"refr_T": -2.}])
    def test_neuron_invariant_violated(self, new_values):
        neuron = self._create_neuron()
        self._assert_rejected(neuron, new_values, unchanged_keys=new_values.keys())

    def test_neuron_invariant_violated_with_other_valid_values(self):
        r"""If one of several new values violates an invariant, none of them should be set (including the state variable)"""
        neuron = self._create_neuron()
        self._assert_rejected(neuron, {"C_m": 100., "V_m": -60., "tau_m": -1.}, unchanged_keys=["C_m", "V_m", "tau_m"])

    def test_neuron_parent_class_rejects(self):
        r"""If the parent class (ArchivingNode) rejects its properties, none of the NESTML parameters and state variables should be set either"""
        neuron = self._create_neuron()
        self._assert_rejected(neuron, {"C_m": 100., "V_m": -60., "tau_minus": -1.}, unchanged_keys=["C_m", "V_m", "tau_minus"])

    def test_synapse_valid_values_are_set(self):
        conn = self._create_connection()
        conn.set({"w": 5., "Wmax": 50., "delay": 2.})
        assert conn.get("w") == 5.
        assert conn.get("Wmax") == 50.
        assert conn.get("delay") == 2.

    def test_synapse_invariant_violated(self):
        conn = self._create_connection()
        self._assert_rejected(conn, {"w": -1.}, unchanged_keys=["w"])

    def test_synapse_invariant_violated_with_other_valid_values(self):
        r"""If one of several new values violates an invariant, none of them should be set (including the delay, which is stored in the NEST ``Connection`` base class)"""
        conn = self._create_connection()
        self._assert_rejected(conn, {"w": 5., "delay": 2., "Wmax": -1.}, unchanged_keys=["w", "delay", "Wmax"])
