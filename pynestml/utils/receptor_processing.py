# -*- coding: utf-8 -*-
#
# receptor_processing.py
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

import copy

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_model import ASTModel
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_receptor_information_collector import ASTReceptorInformationCollector
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.mechanism_processing import MechanismProcessing
from pynestml.utils.messages import Messages

import odetoolbox


class ReceptorProcessing(MechanismProcessing):
    """
    This file is part of the compartmental code generation process.

    Receptor mechanism specific processing.
    """
    mechType = "receptor"

    def __init__(self, params):
        super(MechanismProcessing, self).__init__(params)

    @classmethod
    def collect_information_for_specific_mech_types(cls, neuron, mechs_info):
        mechs_info, add_info_collector = cls.collect_additional_base_infos(neuron, mechs_info)
        if len(mechs_info) > 0:
            # only do this if any synapses found
            # otherwise tests may fail
            mechs_info = cls.collect_and_check_inputs_per_synapse(mechs_info)

        return mechs_info

    @classmethod
    def collect_additional_base_infos(cls, neuron, syns_info):
        """
        Collect internals, kernels, inputs and convolutions associated with the synapse.
        """
        info_collector = ASTReceptorInformationCollector()
        neuron.accept(info_collector)
        for synapse_name, synapse_info in syns_info.items():
            synapse_inline = syns_info[synapse_name]["root_expression"]
            syns_info[synapse_name][
                "internals_used_declared"] = info_collector.get_synapse_specific_internal_declarations(synapse_inline)
            syns_info[synapse_name]["total_used_declared"] = info_collector.get_variable_names_of_synapse(
                synapse_inline)

        return syns_info, info_collector

    @classmethod
    def collect_and_check_inputs_per_synapse(
            cls,
            syns_info: dict):
        new_syns_info = copy.copy(syns_info)
        from pynestml.codegeneration.nest_compartmental_code_generator import NESTCompartmentalCodeGenerator
        # collect all buffers used
        for synapse_name, synapse_info in syns_info.items():
            new_syns_info[synapse_name]["buffers_used"] = set()
            for convolution_name, convolution_info in synapse_info["convolutions"].items(
            ):
                input_name = convolution_info["spikes"]["name"]
                if "self_spikes_port" in FrontendConfiguration.get_codegen_opts().keys():
                    self_spikes_port_name = FrontendConfiguration.get_codegen_opts()["self_spikes_port"]
                else:
                    self_spikes_port_name = NESTCompartmentalCodeGenerator._default_options["self_spikes_port"]
                if input_name != self_spikes_port_name:
                    new_syns_info[synapse_name]["buffers_used"].add(input_name)

        # now make sure each synapse is using exactly one buffer except self_spikes
        for synapse_name, synapse_info in syns_info.items():
            buffers = new_syns_info[synapse_name]["buffers_used"]
            if len(buffers) != 1:
                code, message = Messages.get_syns_bad_buffer_count(
                    buffers, synapse_name)
                causing_object = synapse_info["root_expression"]
                Logger.log_message(
                    code=code,
                    message=message,
                    error_position=causing_object.get_source_position(),
                    log_level=LoggingLevel.ERROR,
                    node=causing_object)

        return new_syns_info

    @classmethod
    def ode_solve_convolution(cls,
                              neuron: ASTModel,
                              parameters_block: ASTBlockWithVariables,
                              kernel_buffer):
        odetoolbox_indict = cls.create_ode_indict(
            neuron, parameters_block, kernel_buffer)
        full_solver_result = odetoolbox.analysis(
            odetoolbox_indict,
            disable_stiffness_check=True,
            disable_singularity_detection=True,
            log_level=FrontendConfiguration.logging_level)
        analytic_solver = None
        analytic_solvers = [
            x for x in full_solver_result if x["solver"] == "analytical"]
        assert len(
            analytic_solvers) <= 1, "More than one analytic solver not presently supported"
        if len(analytic_solvers) > 0:
            analytic_solver = analytic_solvers[0]

        return analytic_solver

    @classmethod
    def create_ode_indict(cls,
                          neuron: ASTModel,
                          parameters_block: ASTBlockWithVariables,
                          kernel_buffer):
        kernel_buffers = {tuple(kernel_buffer)}
        odetoolbox_indict = ASTUtils.transform_ode_and_kernels_to_json(neuron, [parameters_block], kernel_buffers, printer=cls._ode_toolbox_printer, include_ODEs=False)
        odetoolbox_indict["options"] = {}
        odetoolbox_indict["options"]["output_timestep_symbol"] = "__h"
        return odetoolbox_indict
