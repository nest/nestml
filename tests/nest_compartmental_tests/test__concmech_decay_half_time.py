# -*- coding: utf-8 -*-
#
# test__concmech_decay_half_time.py
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

import math
import os

import pytest

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_compartmental_target

# try to import matplotlib; set the result in the flag TEST_PLOTS
try:
    import matplotlib as mpl
    mpl.use("agg")
    import matplotlib.pyplot as plt
    TEST_PLOTS = True
except BaseException:
    TEST_PLOTS = False


class TestCompartmentalConcmechDecayHalfTime:
    @pytest.fixture(scope="module", autouse=True)
    def setup(self):
        tests_path = os.path.realpath(os.path.dirname(__file__))
        input_path = os.path.join(tests_path, "resources", "concmech.nestml")
        target_path = os.path.join(tests_path, "target", "concmech_decay_half_time")

        os.makedirs(target_path, exist_ok=True)

        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=0.1))

        generate_nest_compartmental_target(
            input_path=input_path,
            target_path=target_path,
            module_name="concmech_decay_half_time_module",
            suffix="_nestml",
            logging_level="INFO"
        )

        nest.Install("concmech_decay_half_time_module.so")

    def test_concentration_decay_half_time(self):
        """Check the concentration decay half-time without channel-driven calcium influx."""
        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=0.1))
        nest.Install("concmech_decay_half_time_module.so")

        initial_concentration = 1.0
        inf_concentration = 0.0001
        tau_ca = 605.03
        expected_half_time = tau_ca * math.log(2.0)
        half_concentration = inf_concentration + 0.5 * (initial_concentration - inf_concentration)

        cm = nest.Create("multichannel_test_model_nestml")
        cm.compartments = [
            {
                "parent_idx": -1,
                "params": {
                    "C_m": 10.0,
                    "g_C": 0.0,
                    "g_L": 1.5,
                    "e_L": -70.0,
                    "c_Ca": initial_concentration,
                    "inf_Ca": inf_concentration,
                    "tau_Ca": tau_ca,
                },
            }
        ]

        mm = nest.Create("multimeter", 1, {"record_from": ["c_Ca0"], "interval": 0.1})
        nest.Connect(mm, cm)

        nest.Simulate((round(expected_half_time * 10) / 10) + 5.0)

        res = nest.GetStatus(mm, "events")[0]
        measured_half_time = self._interpolated_crossing_time(
            res["times"],
            res["c_Ca0"],
            half_concentration
        )

        if TEST_PLOTS:
            fig, ax = plt.subplots()

            ax.plot(res["times"], res["c_Ca0"], c="y", label="c_Ca0")
            ax.axhline(y=half_concentration, color="b", linestyle="--", label="half concentration")
            ax.axvline(x=expected_half_time, color="r", linestyle="--", label="theoretical half-time")
            ax.axvline(x=measured_half_time, color="g", linestyle=":", label="measured half-time")

            ax.set_title("c_Ca0 decay")
            ax.legend()

            plt.savefig("concmech decay half time.png")
            plt.close(fig)

        assert measured_half_time == pytest.approx(expected_half_time, abs=0.2)

    @staticmethod
    def _interpolated_crossing_time(times, values, target_value):
        for idx in range(1, len(values)):
            previous_value = values[idx - 1]
            current_value = values[idx]

            if previous_value >= target_value >= current_value:
                previous_time = times[idx - 1]
                current_time = times[idx]
                fraction = (previous_value - target_value) / (previous_value - current_value)
                return previous_time + fraction * (current_time - previous_time)

        raise AssertionError("Concentration trace did not cross the expected half-concentration.")
