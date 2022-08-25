# -*- coding: utf-8 -*-
#
# stdp_stp_synapse_test.py
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

import nest
import pytest

from pynestml.codegeneration.nest_tools import NESTTools
from pynestml.frontend.pynestml_frontend import generate_nest_target

nest_version = NESTTools.detect_nest_version()


@pytest.mark.skipif(nest_version.startswith("v2"),
                    reason="This test does not support NEST 2")
def test_stdp_stp_synapse():
    """
    This test currently verifies the code generation and compilation when a synapse model has the function ``random_normal()`` defined.

    TODO: The test needs to be improved by adding more functionality and assertions.
    :return:
    """
    input_path = [os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(os.pardir, os.pardir, "models", "neurons", "iaf_psc_delta.nestml"))),
                  os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "stdp_stp_synapse.nestml"))]
    target_path = "/tmp/nestml-stdp-stp"
    module_name = "nestml_module"
    generate_nest_target(input_path=input_path,
                         target_path=target_path,
                         logging_level="INFO",
                         module_name=module_name,
                         suffix="_nestml",
                         codegen_opts={"neuron_parent_class": "StructuralPlasticityNode",
                                       "neuron_parent_class_include": "structural_plasticity_node.h",
                                       "neuron_synapse_pairs": [{"neuron": "iaf_psc_delta",
                                                                 "synapse": "stdp_stp",
                                                                 "post_ports": ["post_spikes"]}]})
    nest.Install(module_name)
