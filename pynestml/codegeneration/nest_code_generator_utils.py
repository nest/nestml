# -*- coding: utf-8 -*-
#
# nest_code_generator_utils.py
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

from typing import List, Optional

import re
import tempfile
import uuid

from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.variable_symbol import BlockType
from pynestml.symbols.variable_symbol import VariableSymbol


class NESTCodeGeneratorUtils:

    @classmethod
    def print_symbol_origin(cls, variable_symbol: VariableSymbol, variable: ASTVariable) -> str:
        r"""
        Returns a prefix corresponding to the origin of the variable symbol.
        :param variable_symbol: a single variable symbol.
        :return: the corresponding prefix
        """
        if variable_symbol.block_type in [BlockType.STATE, BlockType.EQUATION]:
            if "_is_numeric" in dir(variable) and variable._is_numeric:
                return "S_.ode_state[State_::%s]"

            return "S_.%s"

        if variable_symbol.block_type == BlockType.PARAMETERS:
            return "P_.%s"

        if variable_symbol.block_type == BlockType.COMMON_PARAMETERS:
            return "cp.%s"

        if variable_symbol.block_type == BlockType.INTERNALS:
            return "V_.%s"

        if variable_symbol.block_type == BlockType.INPUT:
            return "B_.%s"

        return ""

    @classmethod
    def generate_code_for(cls,
                          nestml_neuron_model: str,
                          nestml_synapse_model: Optional[str] = None,
                          post_ports: Optional[List[str]] = None,
                          mod_ports: Optional[List[str]] = None,
                          uniq_id: Optional[str] = None,
                          logging_level: str = "WARNING"):
        """Generate code for a given neuron and synapse model, passed as a string.
        NEST cannot yet unload or reload modules. This function implements a workaround using UUIDs to generate unique names.
        The neuron and synapse models can be passed directly as strings in NESTML syntax, or as filenames, in which case the NESTML model is loaded from the given filename.

        Returns
        -------
        If a synapse is specified, returns a tuple (module_name, mangled_neuron_name, mangled_synapse_name) containing the names that can be used in ``nest.Install()``, ``nest.Create()`` and ``nest.Connect()`` calls. If no synapse is specified, returns a tuple (module_name, mangled_neuron_name).
        """

        from pynestml.frontend.pynestml_frontend import generate_nest_target

        # generate temporary install directory
        install_path = tempfile.mkdtemp(prefix="nestml_target_")

        # generate unique ID
        if uniq_id is None:
            uniq_id = str(uuid.uuid4().hex)

        # read neuron model from file?
        if not "\n" in nestml_neuron_model and ".nestml" in nestml_neuron_model:
            with open(nestml_neuron_model, "r") as nestml_model_file:
                nestml_neuron_model = nestml_model_file.read()

        # update neuron model name inside the file
        neuron_model_name_orig = re.findall(r"neuron\ [^:\s]*:", nestml_neuron_model)[0][7:-1]
        neuron_model_name_uniq = neuron_model_name_orig + uniq_id
        nestml_model = re.sub(r"neuron\ [^:\s]*:",
                              "neuron " + neuron_model_name_uniq + ":", nestml_neuron_model)
        neuron_uniq_fn = neuron_model_name_uniq + ".nestml"
        with open(neuron_uniq_fn, "w") as f:
            print(nestml_model, file=f)

        if nestml_synapse_model:
            # read synapse model from file?
            if not "\n" in nestml_synapse_model and ".nestml" in nestml_synapse_model:
                with open(nestml_synapse_model, "r") as nestml_model_file:
                    nestml_synapse_model = nestml_model_file.read()

            # update synapse model name inside the file
            synapse_model_name_orig = re.findall(r"synapse\ [^:\s]*:", nestml_synapse_model)[0][8:-1]
            synapse_model_name_uniq = synapse_model_name_orig + uniq_id
            nestml_model = re.sub(r"synapse\ [^:\s]*:",
                                  "synapse " + synapse_model_name_uniq + ":", nestml_synapse_model)
            synapse_uniq_fn = synapse_model_name_uniq + ".nestml"
            with open(synapse_uniq_fn, "w") as f:
                print(nestml_model, file=f)

        # generate the code for neuron and optionally synapse
        module_name = "nestml_" + uniq_id + "_module"
        input_fns = [neuron_uniq_fn]
        codegen_opts = {"neuron_parent_class": "StructuralPlasticityNode",
                        "neuron_parent_class_include": "structural_plasticity_node.h"}

        mangled_neuron_name = neuron_model_name_uniq + "_nestml"
        if nestml_synapse_model:
            input_fns += [synapse_uniq_fn]
            codegen_opts["neuron_synapse_pairs"] = [{"neuron": neuron_model_name_uniq,
                                                     "synapse": synapse_model_name_uniq,
                                                     "post_ports": post_ports,
                                                     "vt_ports": mod_ports}]
            mangled_neuron_name = neuron_model_name_uniq + "_nestml__with_" + synapse_model_name_uniq + "_nestml"
            mangled_synapse_name = synapse_model_name_uniq + "_nestml__with_" + neuron_model_name_uniq + "_nestml"

        generate_nest_target(input_path=input_fns,
                             install_path=install_path,
                             logging_level=logging_level,
                             module_name=module_name,
                             suffix="_nestml",
                             codegen_opts=codegen_opts)

        if nestml_synapse_model:
            return module_name, mangled_neuron_name, mangled_synapse_name
        else:
            return module_name, mangled_neuron_name
