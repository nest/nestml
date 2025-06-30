# -*- coding: utf-8 -*-
#
# python_standalone_target_tools.py
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
import multiprocessing
import os
import sys
import tempfile

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.frontend.pynestml_frontend import generate_python_standalone_target
from pynestml.meta_model.ast_model import ASTModel
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.model_parser import ModelParser


class PythonStandaloneTargetTools:
    r"""
    Helper functions for the Python standalone target.
    """
    @classmethod
    def _get_model_parameters_and_state(cls, nestml_file_name: str):
        suffix = ""
        module_name = FrontendConfiguration.get_module_name()
        target_path = tempfile.mkdtemp(prefix="nestml_python_target_", suffix="", dir=".")    # dir = "." is necessary for Python import
        # this has to run in a different process, because otherwise the frontend configuration gets overwritten
        process = multiprocessing.Process(target=generate_python_standalone_target, kwargs={"input_path": nestml_file_name,
                                                                                            "target_path": target_path,
                                                                                            "suffix": suffix,
                                                                                            "module_name": module_name,
                                                                                            "logging_level": "ERROR"})
        process.start()
        process.join()    # wait for code generation to complete

        ast_compilation_unit = ModelParser.parse_file(nestml_file_name)
        if ast_compilation_unit is None or len(ast_compilation_unit.get_model_list()) == 0:
            raise Exception("Error(s) occurred during code generation; please check error messages")

        model: ASTModel = ast_compilation_unit.get_model_list()[0]
        model_name = model.get_name()

        py_module_name = os.path.basename(target_path) + "." + model_name
        module = importlib.import_module(py_module_name)
        neuron_name = "Neuron_" + model_name + "(1.0)"   # 1.0 is a dummy value for the timestep
        neuron = eval("module." + neuron_name)

        parameters_list = [p for p in dir(neuron.Parameters_) if not "__" in p]
        parameters = {p: getattr(neuron, "get_" + p)() for p in parameters_list}

        if "ode_state_variable_name_to_index" in dir(neuron.State_):
            state_list = neuron.State_.ode_state_variable_name_to_index.keys()
        else:
            state_list = [p for p in dir(neuron.State_) if not "__" in p]
        state_vars = {p: getattr(neuron, "get_" + p)() for p in state_list}

        return parameters, state_vars

    @classmethod
    def get_neuron_parameters_and_state(cls, nestml_file_name: str) -> tuple[dict, dict]:
        r"""
        Get the parameters for the given neuron model. The code is generated for the model for Python standalone target
        The parameters and state variables are then queried by creating the neuron in Python standalone simulator.
        :param nestml_file_name: File name of the neuron model
        :return: A dictionary of parameters and state variables
        """
        parameters, state = cls._get_model_parameters_and_state(nestml_file_name)

        if not parameters or not state:
            Logger.log_message(None, -1,
                               "An error occurred while creating the neuron for Python standalone target: " + nestml_file_name,
                               None, LoggingLevel.ERROR)
            sys.exit(1)
        else:
            Logger.log_message(None, -1, "The model parameters were successfully queried from Python standalone target.",
                               None, LoggingLevel.INFO)

        return parameters, state
