# -*- coding: utf-8 -*-
#
# generate_nest_reference_values.py
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

r"""
Generate the reference values used in the Python-standalone tests (``tests/python_standalone_tests/test_*.py``) by running the same models and simulation protocol in NEST Simulator.

The simulation protocol mirrors ``TestSimulator.test_simulator()`` in ``pynestml/codegeneration/resources_python_standalone/point_neuron/test_python_standalone_module.py.jinja2``:

- resolution 0.1 ms, simulation time 100 ms
- an excitatory spike generator emitting every 10 ms, connected with weight 1000
- an inhibitory spike generator emitting every 50 ms, connected with weight -4000 (not connected for the Izhikevich model)

The Python-standalone simulator has a fixed connection delay of one timestep, so the NEST connections use a delay equal to the simulation resolution.

For each model, the membrane potential timeseries is written to a CSV file ``<model_name>.csv`` in the same directory as this script, with columns ``t`` (in ms) and ``V_m`` (in mV). The rows correspond to the end of each simulation timestep (t = 0.1, 0.2, ..., 100 ms), matching the log of the Python-standalone simulator.

Usage (requires NEST Simulator to be installed and importable):

.. code-block:: bash

   python3 tests/python_standalone_tests/resources/generate_nest_reference_values.py [target_path]
"""

from typing import Tuple

import os
import sys

import numpy as np

import nest

from pynestml.frontend.pynestml_frontend import generate_nest_target


MODELS = ["iaf_psc_exp_neuron", "aeif_cond_exp_neuron", "izhikevich_neuron"]
MODULE_NAME = "nestml_python_standalone_reference_module"
SUFFIX = "_nestml"

RESOLUTION = .1    # [ms]; must be equal to ``Simulator.timestep`` in the Python-standalone simulator
DELAY = RESOLUTION    # [ms]; the Python-standalone simulator has a fixed connection delay of one timestep
T_STOP = 100.    # [ms]
EXC_INTERVAL = 10.    # [ms]
INH_INTERVAL = 50.    # [ms]


def generate_code(target_path: str) -> None:
    models_path = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, "models", "neurons"))
    generate_nest_target([os.path.join(models_path, model + ".nestml") for model in MODELS],
                         target_path=target_path,
                         module_name=MODULE_NAME,
                         logging_level="WARNING",
                         suffix=SUFFIX)


def run_simulation(model: str) -> Tuple[np.ndarray, np.ndarray]:
    r"""Run the simulation for the given model and return the times and membrane potential at the end of each timestep."""
    nest.ResetKernel()
    nest.resolution = RESOLUTION
    try:
        nest.Install(MODULE_NAME)
    except Exception:
        # ResetKernel() does not unload modules for NEST Simulator < v3.7; ignore exception if module is already loaded on earlier versions
        pass

    # the Python-standalone ``SpikeGenerator(interval)`` emits spikes at times ``interval``, ``2 * interval``, ..., up to and including ``T_STOP``
    sg_exc = nest.Create("spike_generator", params={"spike_times": np.arange(1, int(round(T_STOP / EXC_INTERVAL)) + 1) * EXC_INTERVAL})
    sg_inh = nest.Create("spike_generator", params={"spike_times": np.arange(1, int(round(T_STOP / INH_INTERVAL)) + 1) * INH_INTERVAL})

    neuron = nest.Create(model + SUFFIX)
    nest.Connect(sg_exc, neuron, syn_spec={"weight": 1000., "delay": DELAY})
    if "izhikevich" not in model:
        nest.Connect(sg_inh, neuron, syn_spec={"weight": -4000., "delay": DELAY})

    # step through the simulation one timestep at a time, reading out the membrane potential after each step. A multimeter is not used here, because it does not record the last ``min_delay`` of the simulation.
    n_steps = int(round(T_STOP / RESOLUTION))
    times = np.empty(n_steps)
    V_m = np.empty(n_steps)
    nest.Prepare()
    for i in range(n_steps):
        nest.Run(RESOLUTION)
        times[i] = nest.biological_time
        V_m[i] = neuron.V_m
    nest.Cleanup()

    return times, V_m


if __name__ == "__main__":
    target_path = sys.argv[1] if len(sys.argv) > 1 else "nestml_python_standalone_reference_target"
    generate_code(target_path)

    for model in MODELS:
        times, V_m = run_simulation(model)
        fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), model + ".csv")
        np.savetxt(fname, np.stack([times, V_m]).T, delimiter=",", header="t,V_m", comments="", fmt="%.17g")
        print(model + ": V_m at t = " + str(times[-1]) + " ms: " + repr(V_m[-1]) + "; timeseries written to " + fname)
