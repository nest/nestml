# -*- coding: utf-8 -*-
#
# test_weight_variable_specified.py
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

import nest
from nest.lib.hl_api_exceptions import NESTErrors

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


class TestWeightVariableSpecified:
    r"""Test that forgetting to specify the ``weight_variable`` when using a synapse results in failure to generate code."""

    @pytest.mark.xfail(strict=True)
    def test_weight_variable_not_specified_results_in_failure(self):
        r"""Generate the model code"""

        files = [os.path.join("models", "neurons", "iaf_psc_exp_neuron.nestml"),
                 os.path.join("models", "synapses", "stdp_synapse.nestml")]
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, s))) for s in files]
        generate_nest_target(input_path=input_path,
                             logging_level="DEBUG",
                             suffix="_nestml",
                             codegen_opts={"neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapse": "stdp_synapse",
                                                                     "post_ports": ["post_spikes"]}],
                                           "delay_variable": {"stdp_synapse": "d"}})


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestSynapseWeightGetSet:
    """Check that we can get and set the weight parameter of a synapse"""

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))),
                      os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, "models", "synapses", "stdp_synapse.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "weight_test_assigned_synapse.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "weight_test_plastic_synapse.nestml")))]
        logging_level = "DEBUG"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")

        generate_nest_target(input_path,
                             logging_level=logging_level,
                             suffix=suffix,
                             codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                           "neuron_parent_class_include": "structural_plasticity_node.h",
                                           "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp_neuron",
                                                                     "synapse": "stdp_synapse",
                                                                     "post_ports": ["post_spikes"]}],
                                           "delay_variable": {"weight_test_plastic_synapse": "d",
                                                              "weight_test_assigned_synapse": "d",
                                                              "stdp_synapse": "d"},
                                           "weight_variable": {"weight_test_plastic_synapse": "w",
                                                               "weight_test_assigned_synapse": "w",
                                                               "stdp_synapse": "w"}})

    @pytest.mark.xfail(strict=True, raises=NESTErrors.BadProperty)
    def test_synapse_weight_set_status1(self):
        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml")
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": "stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml", "weight": 42., "w": 123.})

    @pytest.mark.xfail(strict=True)
    def test_synapse_weight_set_status1(self):
        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml")
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": "stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml"})
        syn = nest.GetConnections(nrn, nrn)
        assert len(syn) == 1
        nest.SetStatus(syn, {"w": 42., "weight": 123.})

    def test_synapse_weight_set_status(self):
        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml")
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": "stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml", "weight": 42.})
        syn = nest.GetConnections(nrn, nrn)
        assert len(syn) == 1
        np.testing.assert_allclose(syn[0].get("w"), 42.)
        np.testing.assert_allclose(syn[0].get("weight"), 42.)
        syn.w = 123.
        np.testing.assert_allclose(syn[0].get("w"), 123.)
        np.testing.assert_allclose(syn[0].get("weight"), 123.)
        syn.weight = 3.14159
        np.testing.assert_allclose(syn[0].get("w"), 3.14159)
        np.testing.assert_allclose(syn[0].get("weight"), 3.14159)

    def test_synapse_weight_set_status_alt(self):
        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("iaf_psc_exp_neuron_nestml__with_stdp_synapse_nestml")
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": "stdp_synapse_nestml__with_iaf_psc_exp_neuron_nestml", "w": 42.})
        syn = nest.GetConnections(nrn, nrn)
        assert len(syn) == 1
        np.testing.assert_allclose(syn[0].get("w"), 42.)
        np.testing.assert_allclose(syn[0].get("weight"), 42.)
        syn.w = 123.
        np.testing.assert_allclose(syn[0].get("w"), 123.)
        np.testing.assert_allclose(syn[0].get("weight"), 123.)
        syn.weight = 3.14159
        np.testing.assert_allclose(syn[0].get("w"), 3.14159)
        np.testing.assert_allclose(syn[0].get("weight"), 3.14159)

    @pytest.mark.parametrize("synapse_model_name", ["weight_test_plastic_synapse_nestml"])
    def test_synapse_weight(self, synapse_model_name: str):
        """Check that the synapse can itself access the set weight value properly"""
        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("iaf_psc_exp")
        nrn.I_e = 1000.   # [pA] -- assure there are pre spikes to trigger synapse update
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": synapse_model_name})
        syn = nest.GetConnections(nrn, nrn)
        assert len(syn) == 1
        syn[0].weight = 42.
        nest.Simulate(100.)
        np.testing.assert_allclose(syn[0].get("weight"), 42.)
        np.testing.assert_allclose(syn[0].get("x"), 42.)
        syn.weight = 21.
        nest.Simulate(100.)
        np.testing.assert_allclose(syn[0].get("weight"), 21.)
        np.testing.assert_allclose(syn[0].get("x"), 21.)

    @pytest.mark.parametrize("synapse_model_name", ["weight_test_plastic_synapse_nestml"])
    def test_synapse_weight_default(self, synapse_model_name: str):
        """Check that the default value is there and correct"""
        nest.ResetKernel()
        nest.Install("nestmlmodule")
        nrn = nest.Create("iaf_psc_exp")
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": synapse_model_name})
        syn = nest.GetConnections(nrn, nrn)
        assert len(syn) == 1
        np.testing.assert_allclose(syn[0].get("weight"), 1.)
