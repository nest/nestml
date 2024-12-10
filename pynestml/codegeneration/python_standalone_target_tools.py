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
import importlib
import os
import sys

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.frontend.pynestml_frontend import generate_python_standalone_target
from pynestml.utils.logger import LoggingLevel, Logger


class PythonStandaloneTargetTools:
    """
    Helper functions for Python standalone target.
    """
    @classmethod
    def _get_model_parameters_and_state(cls, model_name: str):
        input_path = os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
            os.pardir, os.pardir, "models", "neurons", model_name + ".nestml"))))
        suffix = "_nestml"
        module_name = FrontendConfiguration.get_module_name()
        target_path = FrontendConfiguration.get_module_name()
        generate_python_standalone_target(input_path=input_path,
                                          target_path=target_path,
                                          suffix=suffix,
                                          module_name=module_name,
                                          logging_level="INFO")

        py_module_name = "nest_desktop_module." + model_name + suffix
        module = importlib.import_module(py_module_name)
        neuron_name = "Neuron_" + model_name + suffix + "(1.0)"
        neuron = eval("module." + neuron_name)
        parameters_list = [p for p in dir(neuron.Parameters_) if not "__" in p]
        parameters = {p: eval("neuron.get_" + p + "()") for p in parameters_list}

        state_list = [p for p in dir(neuron.State_) if not "__" in p]
        state_vars = {p: eval("neuron.get_" + p + "()") for p in state_list}

        return parameters, state_vars

    @classmethod
    def get_neuron_parameters_and_state(cls, neuron_model_name: str) -> tuple[dict, dict]:
        r"""
        Get the parameters for the given neuron model. The code is generated for the model for Python standalone target
        The parameters and state variables are then queried by creating the neuron in Python standalone simulator.
        :param neuron_model_name: Name of the neuron model
        :return: A dictionary of parameters and state variables
        """
        parameters, state = cls._get_model_parameters_and_state(neuron_model_name)

        if not parameters or not state:
            Logger.log_message(None, -1,
                               "An error occurred while creating the neuron for python standalone target: " + neuron_model_name,
                               None, LoggingLevel.ERROR)
            sys.exit(1)
        else:
            Logger.log_message(None, -1, "The model parameters were successfully queried from python standalone target.",
                               None, LoggingLevel.INFO)

        return parameters, state
