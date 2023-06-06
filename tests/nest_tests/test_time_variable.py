# -*- coding: utf-8 -*-
#
# test_time_variable.py
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

import nest
import numpy as np
import os
import pytest

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


@pytest.mark.skipif(NESTTools.detect_nest_version().startswith("v2"),
                    reason="This test does not support NEST 2")
class TestTimeVariable:
    """Sanity test for the predefined variable ``t``, which represents simulation time"""

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        input_path = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "TimeVariableNeuron.nestml"))),
                      os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "TimeVariableSynapse.nestml")))]
        target_path = "target"
        logging_level = "INFO"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.Install(module_name)

    def test_time_variable_neuron(self):
        nest.ResetKernel()
        nrn = nest.Create("time_variable_neuron_nestml")
        mm = nest.Create("multimeter")
        nest.SetStatus(mm, {"record_from": ["x", "y"]})
        nest.Connect(mm, nrn)

        nest.Simulate(100.0)

        timevec = mm.get("events")["times"]
        x = mm.get("events")["x"]
        y = mm.get("events")["y"]

        np.testing.assert_allclose(x, timevec)
        np.testing.assert_allclose(1E-3 * x, y)

    def test_time_variable_synapse(self):
        """a synapse is only updated when presynaptic spikes arrive"""
        nest.ResetKernel()
        nrn = nest.Create("iaf_psc_delta", 2)
        nrn[0].I_e = 1000.  # [pA]
        sr = nest.Create("spike_recorder")
        nest.Connect(nrn[0], sr)
        nest.Connect(nrn[0], nrn[1], syn_spec={"synapse_model": "time_variable_synapse_nestml"})
        syn = nest.GetConnections(nrn[0], nrn[1])
        assert len(syn) == 1

        nest.Simulate(50.)

        assert len(sr.get("events")["times"]) > 2, "Was expecting some more presynaptic spikes"

        x = syn[0].get("x")
        y = syn[0].get("y")

        np.testing.assert_allclose(x, sr.get("events")["times"][-2])
        np.testing.assert_allclose(y, sr.get("events")["times"][-1])
