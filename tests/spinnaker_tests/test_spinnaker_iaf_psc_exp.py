# -*- coding: utf-8 -*-
#
# test_spinnaker_iaf_psc_exp.py
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

from pynestml.frontend.pynestml_frontend import generate_spinnaker_target


class TestSpiNNakerIafPscExp:
    """SpiNNaker code generation tests"""

    @pytest.fixture(autouse=True,
                    scope="module")
    def generate_code(self):
        # input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "models", "neurons",  "iaf_psc_exp.nestml"))),
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "models", "synapses",  "static_synapse.nestml"))),
        target_path = "spinnaker-target"
        install_path = "spinnaker-install"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"
        generate_spinnaker_target(input_path,
                                  target_path=target_path,
                                  install_path=install_path,
                                  logging_level=logging_level,
                                  module_name=module_name,
                                  suffix=suffix)

    def test_logarithmic_function(self):
        pass    # XXX: TODO
