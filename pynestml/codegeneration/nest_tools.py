# -*- coding: utf-8 -*-
#
# nest_tools.py
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

import subprocess
import os
import sys
import tempfile
import multiprocessing as mp

from pynestml.frontend.pynestml_frontend import generate_nest_target
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel


class NESTTools:
    r"""Helper functions for NEST Simulator"""

    @classmethod
    def detect_nest_version(cls) -> str:
        r"""Auto-detect NEST Simulator installed version. The returned string corresponds to a git tag or git branch name.

        Do this in a separate process to avoid potential side-effects of import the ``nest`` Python module.

        .. admonition::

           NEST version detection needs improvement. See https://github.com/nest/nest-simulator/issues/2116
        """

        script = """\"\"\"Auto-detect NEST Simulator installed version and print the version string to stderr.\"\"\"

import sys

try:
    import nest

    vt = nest.Create("volume_transmitter")

    try:
        neuron = nest.Create("hh_psc_alpha_clopath")
        neurons = nest.Create("iaf_psc_exp", 2)
        nest.Connect(neurons[0], neurons[1], syn_spec={"synapse_model": "stdp_synapse",
                                            "weight": 1., "delay": 1.})
        syn = nest.GetConnections(target=neurons[1], synapse_model="stdp_synapse")
    except Exception:
        pass

    if "DataConnect" in dir(nest):
            nest_version = "v2.20.2"
    else:
        nest_version = "v" + nest.__version__
        if nest_version.startswith("v3.5") or nest_version.startswith("v3.6") or nest_version.startswith("v3.7") or nest_version.startswith("v3.8"):
            if "post0.dev0" in nest_version:
                nest_version = "master"
        else:
            if "kernel_status" not in dir(nest):  # added in v3.1
                nest_version = "v3.0"
            elif "prepared" in nest.GetKernelStatus().keys():  # "prepared" key was added after v3.3 release
                nest_version = "v3.4"
            elif "tau_u_bar_minus" in neuron.get().keys():   # added in v3.3
                nest_version = "v3.3"
            elif "tau_Ca" in vt.get().keys():   # removed in v3.2
                nest_version = "v3.1"
            else:
                nest_version = "v3.2"
except ModuleNotFoundError:
    nest_version = ""

print(nest_version, file=sys.stderr)
"""

        with tempfile.NamedTemporaryFile() as f:
            f.write(bytes(script, encoding="UTF-8"))
            f.seek(0)
            cmd = [sys.executable, f.name]

            process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            nest_version = stderr.decode("UTF-8").strip()

        if nest_version == "":
            Logger.log_message(None, -1, "An error occurred while importing the `nest` module in Python. Please check your NEST installation-related environment variables and paths, or specify ``nest_version`` manually in the code generator options.", None, LoggingLevel.ERROR)
            sys.exit(1)

        Logger.log_message(None, -1, "The NEST Simulator version was automatically detected as: " + nest_version, None, LoggingLevel.INFO)

        return nest_version

    @classmethod
    def _get_model_parameters(cls, model_name: str, queue: mp.Queue):
        try:
            import nest
            input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
                os.pardir, os.pardir, "models", "neurons", model_name + ".nestml"))))
            target_path = "target"
            suffix = "_nestml"
            module_name = "nest_desktop_module"
            generate_nest_target(input_path=input_path,
                                 target_path=target_path,
                                 suffix=suffix,
                                 module_name=module_name,
                                 logging_level="INFO")
            # Install the nest module and query all the parameters
            nest.Install(module_name)
            n = nest.Create(model_name + suffix)
            parameters = n.get()

        except ModuleNotFoundError:
            parameters = {}

        queue.put(parameters)

    @classmethod
    def get_neuron_parameters(cls, neuron_model_name: str) -> dict:
        r"""
        Get the parameters for the given neuron model. The code is generated for the model and installed into NEST.
        The parameters are then queried by creating the neuron in NEST.
        :param neuron_model_name: Name of the neuron model
        :return: A dictionary of parameters
        """
        # This function internally calls the nest_code_generator which calls the detect_nest_version() function that
        # uses mp.Pool. If a Pool is used here instead of a Process, it gives the error "daemonic processes are not
        # allowed to have children". Since creating a Pool inside a Pool is not allowed, we create a Process
        # object here instead.
        _queue = mp.Queue()
        p = mp.Process(target=cls._get_model_parameters, args=(neuron_model_name, _queue))
        p.start()
        p.join()
        parameters = _queue.get()
        p.close()

        if not parameters:
            Logger.log_message(None, -1,
                               "An error occurred while importing the `nest` module in Python. Please check your NEST "
                               "installation-related environment variables and paths, or specify ``nest_version`` "
                               "manually in the code generator options.",
                               None, LoggingLevel.ERROR)
            sys.exit(1)
        else:
            Logger.log_message(None, -1, "The model parameters were successfully queried from NEST simulator",
                               None, LoggingLevel.INFO)

        return parameters
