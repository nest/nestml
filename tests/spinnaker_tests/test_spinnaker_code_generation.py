# -*- coding: utf-8 -*-
#
# test_spinnaker_code_generation.py
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
import unittest

import nest

from pynestml.frontend.pynestml_frontend import generate_target


class TestSpiNNakerCodeGeneration(unittest.TestCase):
    """
    Tests the code generation for SpiNNaker
    """

    def test_python_standalone_neuron_build_and_sim_analytic(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "iaf_psc_alpha.nestml"))))
        target_path = "/tmp/nestml-spinnaker"
        logging_level = "INFO"
        suffix = ""
        module_name = "nestmlmodule"
        codegen_opts = {}

        generate_target(input_path=input_path,
                        target_platform="SpiNNaker",
                        target_path=target_path,
                        module_name=module_name,
                        logging_level=logging_level,
                        suffix=suffix,
                        codegen_opts=codegen_opts)
