# -*- coding: utf-8 -*-
#
# test_synapse_delay.py
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


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestSynapseDelayGetSet:
    """Check that we can get and set the delay parameter of a synapse"""

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp.nestml"))),
                      os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, "models", "synapses", "stdp_synapse.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "delay_test_synapse.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "delay_test_synapse_plastic.nestml")))]
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")

        generate_nest_target(input_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix,
                             codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                           "neuron_parent_class_include": "structural_plasticity_node.h",
                                           "neuron_synapse_pairs": [{"neuron": "iaf_psc_exp",
                                                                     "synapse": "stdp",
                                                                     "post_ports": ["post_spikes"]}]})

        nest.ResetKernel()
        nest.Install(module_name)

    def test_synapse_delay_set_status(self):
        nrn = nest.Create("iaf_psc_exp_nestml__with_stdp_nestml")
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": "stdp_nestml__with_iaf_psc_exp_nestml", "delay": 42.})
        syn = nest.GetConnections(nrn, nrn)
        assert len(syn) == 1
        np.testing.assert_allclose(syn[0].get("delay"), 42.)
        syn.delay = 123.
        np.testing.assert_allclose(syn[0].get("delay"), 123.)

    @pytest.mark.xfail(strict=True, raises=KeyError)
    def test_synapse_delay_creation(self):
        nrn = nest.Create("iaf_psc_exp_nestml__with_stdp_nestml")
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": "stdp_nestml__with_iaf_psc_exp_nestml"})
        syn = nest.GetConnections(nrn, nrn)
        assert len(syn) == 1
        syn[0].d  # getting should fail

    @pytest.mark.xfail(strict=True, raises=NESTErrors.DictError)
    def test_synapse_delay_creation_alt1(self):
        nrn = nest.Create("iaf_psc_exp_nestml__with_stdp_nestml")
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": "stdp_nestml__with_iaf_psc_exp_nestml", "d": 42.})  # setting during construction should fail

    @pytest.mark.xfail(strict=True, raises=NESTErrors.BadProperty)
    def test_synapse_delay_creation_alt2(self):
        nrn = nest.Create("iaf_psc_exp_nestml__with_stdp_nestml")
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": "stdp_nestml__with_iaf_psc_exp_nestml"})
        syn = nest.GetConnections(nrn, nrn)
        assert len(syn) == 1
        syn.d = 42.  # setting should fail

    @pytest.mark.parametrize("synapse_model_name", ["delay_test_synapse_nestml", "delay_test_synapse_plastic_nestml"])
    def test_synapse_delay(self, synapse_model_name: str):
        """Check that the synapse can itself access the set delay value properly"""
        nrn = nest.Create("iaf_psc_exp")
        nrn.I_e = 1000.   # [pA] -- assure there are pre spikes to trigger synapse update
        nest.Connect(nrn, nrn, syn_spec={"synapse_model": synapse_model_name})
        syn = nest.GetConnections(nrn, nrn)
        syn[0].delay = 42.
        syn = nest.GetConnections(nrn, nrn)
        assert len(syn) == 1
        nest.Simulate(100.)
        np.testing.assert_allclose(syn[0].get("delay"), 42.)
        np.testing.assert_allclose(syn[0].get("x"), 42.)
        syn.delay = 21.
        nest.Simulate(100.)
        np.testing.assert_allclose(syn[0].get("delay"), 21.)
        np.testing.assert_allclose(syn[0].get("x"), 21.)
