# -*- coding: utf-8 -*-
#
# synapse_processing.py
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

from pynestml.utils.mechanism_processing import MechanismProcessing
from pynestml.utils.ast_synapse_information_collector import ASTSynapseInformationCollector

from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.utils.ast_utils import ASTUtils
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages

from odetoolbox import analysis
from collections import defaultdict
import copy


class SynapseProcessing(MechanismProcessing):
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

        mechs_info = cls.convolution_ode_toolbox_processing(neuron, mechs_info)

        return mechs_info

    @classmethod
    def collect_additional_base_infos(cls, neuron, syns_info):
        """
        Collect internals, kernels, inputs and convolutions associated with the synapse.
        """
        info_collector = ASTSynapseInformationCollector()
        neuron.accept(info_collector)
        for synapse_name, synapse_info in syns_info.items():
            synapse_inline = syns_info[synapse_name]["root_expression"]
            syns_info[synapse_name][
                "internals_used_declared"] = info_collector.get_synapse_specific_internal_declarations(synapse_inline)
            syns_info[synapse_name]["total_used_declared"] = info_collector.get_variable_names_of_synapse(
                synapse_inline)
            syns_info[synapse_name]["convolutions"] = defaultdict()

            kernel_arg_pairs = info_collector.get_extracted_kernel_args(
                synapse_inline)
            for kernel_var, spikes_var in kernel_arg_pairs:
                kernel_name = kernel_var.get_name()
                spikes_name = spikes_var.get_name()
                convolution_name = info_collector.construct_kernel_X_spike_buf_name(
                    kernel_name, spikes_name, 0)
                syns_info[synapse_name]["convolutions"][convolution_name] = {
                    "kernel": {
                        "name": kernel_name,
                        "ASTKernel": info_collector.get_kernel_by_name(kernel_name),
                    },
                    "spikes": {
                        "name": spikes_name,
                        "ASTInputPort": info_collector.get_input_port_by_name(spikes_name),
                    },
                }
        return syns_info, info_collector

    @classmethod
    def collect_and_check_inputs_per_synapse(
            cls,
            syns_info: dict):
        new_syns_info = copy.copy(syns_info)

        # collect all buffers used
        for synapse_name, synapse_info in syns_info.items():
            new_syns_info[synapse_name]["buffers_used"] = set()
            for convolution_name, convolution_info in synapse_info["convolutions"].items(
            ):
                input_name = convolution_info["spikes"]["name"]
                new_syns_info[synapse_name]["buffers_used"].add(input_name)

        # now make sure each synapse is using exactly one buffer
        for synapse_name, synapse_info in syns_info.items():
            buffers = new_syns_info[synapse_name]["buffers_used"]
            if len(buffers) != 1:
                code, message = Messages.get_syns_bad_buffer_count(
                    buffers, synapse_name)
                causing_object = synapse_info["inline_expression"]
                Logger.log_message(
                    code=code,
                    message=message,
                    error_position=causing_object.get_source_position(),
                    log_level=LoggingLevel.ERROR,
                    node=causing_object)

        return new_syns_info

    @classmethod
    def convolution_ode_toolbox_processing(cls, neuron, syns_info):
        if not neuron.get_parameters_blocks():
            return syns_info

        parameters_block = neuron.get_parameters_blocks()[0]

        for synapse_name, synapse_info in syns_info.items():
            for convolution_name, convolution_info in synapse_info["convolutions"].items():
                kernel_buffer = (convolution_info["kernel"]["ASTKernel"], convolution_info["spikes"]["ASTInputPort"])
                convolution_solution = cls.ode_solve_convolution(neuron, parameters_block, kernel_buffer)
                syns_info[synapse_name]["convolutions"][convolution_name]["analytic_solution"] = convolution_solution
        return syns_info

    @classmethod
    def ode_solve_convolution(cls,
                              neuron: ASTNeuron,
                              parameters_block: ASTBlockWithVariables,
                              kernel_buffer):
        odetoolbox_indict = cls.create_ode_indict(
            neuron, parameters_block, kernel_buffer)
        full_solver_result = analysis(
            odetoolbox_indict,
            disable_stiffness_check=True,
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
                          neuron: ASTNeuron,
                          parameters_block: ASTBlockWithVariables,
                          kernel_buffer):
        kernel_buffers = {tuple(kernel_buffer)}
        odetoolbox_indict = cls.transform_ode_and_kernels_to_json(
            neuron, parameters_block, kernel_buffers)
        odetoolbox_indict["options"] = {}
        odetoolbox_indict["options"]["output_timestep_symbol"] = "__h"
        return odetoolbox_indict

    @classmethod
    def transform_ode_and_kernels_to_json(
            cls,
            neuron: ASTNeuron,
            parameters_block,
            kernel_buffers):
        """
        Converts AST node to a JSON representation suitable for passing to ode-toolbox.

        Each kernel has to be generated for each spike buffer convolve in which it occurs, e.g. if the NESTML model code contains the statements

            convolve(G, ex_spikes)
            convolve(G, in_spikes)

        then `kernel_buffers` will contain the pairs `(G, ex_spikes)` and `(G, in_spikes)`, from which two ODEs will be generated, with dynamical state (variable) names `G__X__ex_spikes` and `G__X__in_spikes`.

        :param parameters_block: ASTBlockWithVariables
        :return: Dict
        """
        odetoolbox_indict = {"dynamics": []}

        equations_block = neuron.get_equations_blocks()[0]

        for kernel, spike_input_port in kernel_buffers:
            if ASTUtils.is_delta_kernel(kernel):
                continue
            # delta function -- skip passing this to ode-toolbox

            for kernel_var in kernel.get_variables():
                expr = ASTUtils.get_expr_from_kernel_var(
                    kernel, kernel_var.get_complete_name())
                kernel_order = kernel_var.get_differential_order()
                kernel_X_spike_buf_name_ticks = ASTUtils.construct_kernel_X_spike_buf_name(
                    kernel_var.get_name(), spike_input_port.get_name(), kernel_order, diff_order_symbol="'")

                ASTUtils.replace_rhs_variables(expr, kernel_buffers)

                entry = {"expression": kernel_X_spike_buf_name_ticks + " = " + str(expr), "initial_values": {}}

                # initial values need to be declared for order 1 up to kernel
                # order (e.g. none for kernel function f(t) = ...; 1 for kernel
                # ODE f'(t) = ...; 2 for f''(t) = ... and so on)
                for order in range(kernel_order):
                    iv_sym_name_ode_toolbox = ASTUtils.construct_kernel_X_spike_buf_name(
                        kernel_var.get_name(), spike_input_port, order, diff_order_symbol="'")
                    symbol_name_ = kernel_var.get_name() + "'" * order
                    symbol = equations_block.get_scope().resolve_to_symbol(
                        symbol_name_, SymbolKind.VARIABLE)
                    assert symbol is not None, "Could not find initial value for variable " + symbol_name_
                    initial_value_expr = symbol.get_declaring_expression()
                    assert initial_value_expr is not None, "No initial value found for variable name " + symbol_name_
                    entry["initial_values"][iv_sym_name_ode_toolbox] = cls._ode_toolbox_printer.print(
                        initial_value_expr)

                odetoolbox_indict["dynamics"].append(entry)

        odetoolbox_indict["parameters"] = {}
        if parameters_block is not None:
            for decl in parameters_block.get_declarations():
                for var in decl.variables:
                    odetoolbox_indict["parameters"][var.get_complete_name(
                    )] = cls._ode_toolbox_printer.print(decl.get_expression())

        return odetoolbox_indict
