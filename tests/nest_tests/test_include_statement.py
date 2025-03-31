# -*- coding: utf-8 -*-
#
# test_include_statement.py
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
import scipy as sp
import os

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.codegeneration.nest_tools import NESTTools


class TestIncludeStatement:
    def test_include_statement(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "IncludeStatementTest.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.Install("nestmlmodule")

        nrn = nest.Create("include_statement_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["v"]})

        nest.Connect(mm, nrn)

        nest.Simulate(100.)

        v = mm.get("events")["v"]
        np.testing.assert_allclose(v[-1], 2.71)

    def test_include_statement2(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "IncludeStatementTest2.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.resolution = 0.1    # [ms]
        nest.Install("nestmlmodule")

        nrn = nest.Create("include_statement2_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["v"],
                            "interval": nest.resolution})

        nest.Connect(mm, nrn)

        nest.Simulate(101.)

        v = mm.get("events")["v"]
        np.testing.assert_allclose(v[-1], 1042.)

    def test_include_statement3(self):
        r"""check for failure if the included file has wrong unit types"""
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "IncludeStatementTest3.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        from pynestml.utils.logger import Logger, LoggingLevel
        assert len(Logger.get_all_messages_of_level_and_or_node("include_statement3_nestml", LoggingLevel.ERROR)) > 0

    def test_include_statement4(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "IncludeStatementTest4.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.resolution = 0.1    # [ms]
        nest.Install("nestmlmodule")

        nrn = nest.Create("include_statement4_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["v"],
                            "interval": nest.resolution})

        nest.Connect(mm, nrn)

        nest.Simulate(151.)

        v = mm.get("events")["v"]
        np.testing.assert_allclose(v[-1], 3.71)

    def test_include_statement5(self):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "IncludeStatementTest5.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.resolution = 0.1    # [ms]
        nest.Install("nestmlmodule")

        nrn = nest.Create("include_statement5_nestml")
        mm = nest.Create("multimeter")

        nest.SetStatus(mm, {"record_from": ["x", "y"],
                            "interval": nest.resolution})

        nest.Connect(mm, nrn)

        nest.Simulate(151.)

        x = mm.get("events")["x"]
        y = mm.get("events")["y"]

        np.testing.assert_allclose(x[-1], 50.4)
        np.testing.assert_allclose(y[-1], 62.)

    def test_include_statement6(self):
        input_path = os.path.join(
            os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "IncludeStatementTest6.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.Install("nestmlmodule")

    def test_include_refractory_mechanism(self):
        input_path = os.path.join(
            os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "IncludeStatementRefractory.nestml")))
        target_path = "target"
        logging_level = "DEBUG"
        module_name = "nestmlmodule"
        suffix = "_nestml"

        nest.set_verbosity("M_ALL")
        generate_nest_target(input_path,
                             target_path=target_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix=suffix)
        nest.ResetKernel()
        nest.Install("nestmlmodule")
