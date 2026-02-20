# -*- coding: utf-8 -*-
#
# test_neuron_with_multiple_different_plastic_synapses_vt.py
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
import pytest
import shutil
import tempfile

import nest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.ticker
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except Exception:
    TEST_PLOTS = False

sim_mdl = True
sim_ref = True


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestNeuronWithMultipleDifferentSynapsesVt:
    r"""Test that code can be generated when a postsynaptic neuron is connected to by several different synapse models, as well as a volume transmitter connecting to the synapses"""
    neuron_model_name = "iaf_psc_exp_neuron_nestml__with_stdp_nn_symm_synapse_nestml_and_stdp_nn_restr_symm_synapse_nestml"
    synapse1_model_name = "stdp_nn_symm_synapse_nestml__with_iaf_psc_exp_neuron_nestml"
    synapse2_model_name = "stdp_nn_restr_symm_synapse_nestml__with_iaf_psc_exp_neuron_nestml"

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        r"""Generate the model code.

        Add an extra dummy input port "mod_spikes" to the synapse models and write back to a temporary file so the neuromodulation can be tested.
        """
        # Original model paths
        model_files = {
            "neuron": os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
            "synapse1": os.path.join("models", "synapses", "stdp_nn_symm_synapse.nestml"),
            "synapse2": os.path.join("models", "synapses", "stdp_nn_restr_symm_synapse.nestml")
        }

        # Resolve absolute paths
        base_path = os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))
        neuron_path = os.path.join(base_path, model_files["neuron"])
        syn1_path = os.path.join(base_path, model_files["synapse1"])
        syn2_path = os.path.join(base_path, model_files["synapse2"])

        # Create temporary files for the edited synapses
        tmp_syn1 = tempfile.NamedTemporaryFile(suffix="_symm.nestml", mode='w', delete=False)
        tmp_syn2 = tempfile.NamedTemporaryFile(suffix="_restr_symm.nestml", mode='w', delete=False)

        tmp_paths = [tmp_syn1.name, tmp_syn2.name]

        def edit_nestml(src_path, dest_file):
            with open(src_path, 'r') as f:
                for line in f:
                    dest_file.write(line)
                    if "input:" in line:
                        dest_file.write("        mod_spikes <- spike\n")
            dest_file.close()

        try:
            # Perform the edits
            edit_nestml(syn1_path, tmp_syn1)
            edit_nestml(syn2_path, tmp_syn2)

            # Final input list for PyNESTML
            input_path = [neuron_path, tmp_syn1.name, tmp_syn2.name]
            generate_nest_target(input_path=input_path,
                                logging_level="DEBUG",
                                module_name="nestmlmodule",
                                suffix="_nestml",
                                codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                        "synapses": {"stdp_nn_symm_synapse": {"post_ports": ["post_spikes"],
                                                                                                            "vt_ports": ["mod_spikes"]},
                                                                                     "stdp_nn_restr_symm_synapse": {"post_ports": ["post_spikes"],
                                                                                                                    "vt_ports": ["mod_spikes"]}}}],
                                            "delay_variable": {"stdp_nn_symm_synapse": "d",
                                                                "stdp_nn_restr_symm_synapse": "d"},
                                            "weight_variable": {"stdp_nn_symm_synapse": "w",
                                                                "stdp_nn_restr_symm_synapse": "w"}})
        finally:
            # # Clean up temporary files
            # for p in tmp_paths:
            #     if os.path.exists(p):
            #         os.remove(p)
            pass

    def test_neuron_with_multiple_different_synapses_vt(self):
        # Helper to read the single connection weight between a given pre and the post neuron
        def read_weight(pre, post):
            conns = nest.GetConnections(source=pre, target=post)
            if len(conns) == 0:
                return None
            return nest.GetStatus(conns, 'weight')[0]

        # Run two independent experiments: only pre_neuron1 active, then only pre_neuron2 active.
        sim_time = 1000.0  # ms
        pre_rate = 100.0  # Hz, strong enough to drive plasticity
        post_rate = 50.0  # Hz background to make the post neuron spike

        # Experiment A: only pre_neuron1 fires
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")
        vt = nest.Create("volume_transmitter")
        post = nest.Create(TestNeuronWithMultipleDifferentSynapsesVt.neuron_model_name)
        p1 = nest.Create("parrot_neuron")
        p2 = nest.Create("parrot_neuron")

        nest.CopyModel(TestNeuronWithMultipleDifferentSynapsesVt.synapse1_model_name, "synapse1", {"volume_transmitter": vt})
        nest.CopyModel(TestNeuronWithMultipleDifferentSynapsesVt.synapse2_model_name, "synapse2", {"volume_transmitter": vt})

        nest.Connect(p1, post, syn_spec={"synapse_model": "synapse1"})
        nest.Connect(p2, post, syn_spec={"synapse_model": "synapse2"})

        # Create spike recorders for Experiment A
        sr_p1_A = nest.Create("spike_recorder")
        sr_p2_A = nest.Create("spike_recorder")
        sr_post_A = nest.Create("spike_recorder")
        nest.Connect(p1, sr_p1_A)
        nest.Connect(p2, sr_p2_A)
        nest.Connect(post, sr_post_A)

        # Poisson generator to drive pre_neuron1 only
        pg_pre1 = nest.Create("poisson_generator", params={'rate': pre_rate, 'start': 0.0, 'stop': sim_time})
        nest.Connect(pg_pre1, p1, syn_spec={'weight': 1.0, 'delay': 1.0})

        # Background drive to make post neuron spike
        pg_post = nest.Create("poisson_generator", params={'rate': post_rate, 'start': 0.0, 'stop': sim_time})
        nest.Connect(pg_post, post, syn_spec={'weight': 10000.0, 'delay': 1.0})

        # Read initial weights
        w1_before = read_weight(p1, post)
        w2_before = read_weight(p2, post)

        nest.Simulate(sim_time)

        w1_after_A = read_weight(p1, post)
        w2_after_A = read_weight(p2, post)

        # Plot Experiment A
        if TEST_PLOTS:
            self._plot_raster("Experiment A: pre_neuron1 active", sr_p1_A, sr_p2_A, sr_post_A)

        # Expectation: only connection from pre_neuron1 changes
        assert w1_before is not None and w1_after_A is not None
        assert w2_before is not None and w2_after_A is not None
        assert abs(w1_after_A - w1_before) > 1e-6, "weight for pre_neuron1 should have changed"
        assert abs(w2_after_A - w2_before) < 1e-6, "weight for pre_neuron2 should NOT have changed"

        # Experiment B: only pre_neuron2 fires
        nest.ResetKernel()
        nest.set_verbosity("M_ALL")
        nest.Install("nestmlmodule")
        vt = nest.Create("volume_transmitter")

        nest.CopyModel(TestNeuronWithMultipleDifferentSynapsesVt.synapse1_model_name, "synapse1", {"volume_transmitter": vt})
        nest.CopyModel(TestNeuronWithMultipleDifferentSynapsesVt.synapse2_model_name, "synapse2", {"volume_transmitter": vt})

        post = nest.Create(TestNeuronWithMultipleDifferentSynapsesVt.neuron_model_name)
        p1 = nest.Create("parrot_neuron")
        p2 = nest.Create("parrot_neuron")
        nest.Connect(p1, post, syn_spec={"synapse_model": "synapse1"})
        nest.Connect(p2, post, syn_spec={"synapse_model": "synapse2"})

        # Create spike recorders for Experiment B
        sr_p1_B = nest.Create("spike_recorder")
        sr_p2_B = nest.Create("spike_recorder")
        sr_post_B = nest.Create("spike_recorder")
        nest.Connect(p1, sr_p1_B)
        nest.Connect(p2, sr_p2_B)
        nest.Connect(post, sr_post_B)

        # Poisson generator to drive pre_neuron2 only
        pg_pre2 = nest.Create("poisson_generator", params={'rate': pre_rate, 'start': 0.0, 'stop': sim_time})
        nest.Connect(pg_pre2, p2, syn_spec={'weight': 1.0, 'delay': 1.0})

        # Background drive to make post neuron spike
        pg_post = nest.Create("poisson_generator", params={'rate': post_rate, 'start': 0.0, 'stop': sim_time})
        nest.Connect(pg_post, post, syn_spec={'weight': 10000.0, 'delay': 1.0})

        # Read initial weights
        w1_before = read_weight(p1, post)
        w2_before = read_weight(p2, post)

        nest.Simulate(sim_time)

        w1_after_B = read_weight(p1, post)
        w2_after_B = read_weight(p2, post)

        # Plot Experiment B
        if TEST_PLOTS:
            self._plot_raster("Experiment B: pre_neuron2 active", sr_p1_B, sr_p2_B, sr_post_B)

        # Expectation: only connection from pre_neuron2 changes
        assert w1_before is not None and w1_after_B is not None
        assert w2_before is not None and w2_after_B is not None
        assert abs(w2_after_B - w2_before) > 1e-6, "weight for pre_neuron2 should have changed"
        assert abs(w1_after_B - w1_before) < 1e-6, "weight for pre_neuron1 should NOT have changed"

    def _plot_raster(self, title, sr_p1, sr_p2, sr_post):
        """Helper function to plot spike raster"""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Get spike data
        data_p1 = nest.GetStatus(sr_p1, 'events')[0]
        data_p2 = nest.GetStatus(sr_p2, 'events')[0]
        data_post = nest.GetStatus(sr_post, 'events')[0]

        # Plot spikes
        ax.scatter(data_p1['times'], np.ones(len(data_p1['times'])), c='blue', label='p1', s=20)
        ax.scatter(data_p2['times'], 2 * np.ones(len(data_p2['times'])), c='green', label='p2', s=20)
        ax.scatter(data_post['times'], 3 * np.ones(len(data_post['times'])), c='red', label='post', s=20)

        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(['p1', 'p2', 'post'])
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Neuron')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'/tmp/raster_{title.replace(" ", "_").replace(":", "")}.png')
        plt.close()
