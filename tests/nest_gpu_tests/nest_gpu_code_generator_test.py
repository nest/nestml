# -*- coding: utf-8 -*-
#
# nest_gpu_code_generator_test.py
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
from pynestml.frontend.pynestml_frontend import generate_nest_gpu_target


class TestNESTGPUCodeGenerator:
    """
    Tests code generation for the NEST GPU target.
    """

    def test_nest_gpu_code_generator_analytic(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", "iaf_psc_exp_neuron.nestml"))))
        target_path = "target_gpu"
        logging_level = "INFO"
        suffix = "_nestml"
        generate_nest_gpu_target(input_path, target_path,
                                 logging_level=logging_level,
                                 suffix=suffix)

    def test_nest_gpu_code_generator_numeric(self):
        # model_files = ["aeif_psc_exp_neuron.nestml"]
        model_files = ["aeif_cond_alpha_alt_neuron.nestml"]
        input_path = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", model)))) for model in model_files]
        target_path = "target_gpu_numeric"
        logging_level = "INFO"
        suffix = "_nestml"
        codegen_opts = {"solver": "numeric"}
        generate_nest_gpu_target(input_path, target_path,
                                 logging_level=logging_level,
                                 suffix=suffix,
                                 codegen_opts=codegen_opts)
