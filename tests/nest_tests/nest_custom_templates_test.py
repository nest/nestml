# -*- coding: utf-8 -*-
#
# nest_custom_templates_test.py
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
import unittest

import nest

from pynestml.frontend.pynestml_frontend import to_nest
from pynestml.utils.model_installer import install_nest


class NestCustomTemplatesTest(unittest.TestCase):
    """
    Tests the code generation and installation with custom NESTML templates for NEST
    """

    def test_custom_templates(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "iaf_psc_exp.nestml"))))
        nest_path = nest.ll_api.sli_func("statusdict/prefix ::")
        target_path = 'target'
        logging_level = 'INFO'
        module_name = 'nestmlmodule'
        store_log = False
        suffix = '_nestml'
        dev = True

        codegen_opts = {"templates": {
            "path": 'point_neuron',
            "model_templates": {
                "neuron": ['NeuronClass.cpp.jinja2', 'NeuronHeader.h.jinja2'],
                "synapse": ['SynapseHeader.h.jinja2']
            },
            "module_templates": ['setup/CMakeLists.txt.jinja2',
                                 'setup/ModuleHeader.h.jinja2', 'setup/ModuleClass.cpp.jinja2']
        }}

        to_nest(input_path, target_path, logging_level, module_name, store_log, suffix, dev, codegen_opts)
        install_nest(target_path, nest_path)
        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("iaf_psc_exp_nestml")
        mm = nest.Create('multimeter')
        mm.set({"record_from": ["V_m"]})

        nest.Connect(mm, nrn)

        nest.Simulate(5.0)

    def test_custom_templates_with_synapse(self):
        models = ["iaf_psc_delta.nestml", "stdp_triplet_naive.nestml"]
        input_paths = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", fn)))) for fn in models]
        nest_path = nest.ll_api.sli_func("statusdict/prefix ::")
        target_path = 'target'
        logging_level = 'INFO'
        module_name = 'nestmlmodule'
        store_log = False
        suffix = '_nestml'
        dev = True

        codegen_opts = {
            "neuron_parent_class": "StructuralPlasticityNode",
            "neuron_parent_class_include": "structural_plasticity_node.h",
            "neuron_synapse_pairs": [{"neuron": "iaf_psc_delta",
                                      "synapse": "stdp_triplet",
                                      "post_ports": ["post_spikes"]}],
            "templates": {
                "path": 'point_neuron',
                "model_templates": {
                    "neuron": ['NeuronClass.cpp.jinja2', 'NeuronHeader.h.jinja2'],
                    "synapse": ['SynapseHeader.h.jinja2']
                },
                "module_templates": ['setup/CMakeLists.txt.jinja2',
                                     'setup/ModuleHeader.h.jinja2', 'setup/ModuleClass.cpp.jinja2']
            }
        }

        neuron_model_name = "iaf_psc_delta_nestml__with_stdp_triplet_nestml"
        synapse_model_name = "stdp_triplet_nestml__with_iaf_psc_delta_nestml"

        to_nest(input_paths, target_path, logging_level, module_name, store_log, suffix, dev, codegen_opts)
        install_nest(target_path, nest_path)
        nest.set_verbosity("M_ALL")

        nest.ResetKernel()
        nest.Install("nestmlmodule")

        neurons = nest.Create(neuron_model_name, 2)
        weight_recorder = nest.Create('weight_recorder')
        nest.CopyModel(synapse_model_name,
                       synapse_model_name + "_rec",
                       {'weight_recorder': weight_recorder[0]})
        mm = nest.Create('multimeter')
        mm.set({"record_from": ["V_m"]})

        nest.Connect(neurons[0], neurons[1], syn_spec={'synapse_model': synapse_model_name + "_rec"})
        nest.Connect(mm, neurons[0])

        nest.Simulate(5.0)
