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

from collections import defaultdict

import copy

from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter
from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter
from pynestml.codegeneration.printers.ode_toolbox_function_call_printer import ODEToolboxFunctionCallPrinter
from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter

from pynestml.codegeneration.printers.sympy_simple_expression_printer import SympySimpleExpressionPrinter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_synapse_information_collector import ASTSynapseInformationCollector, \
    ASTKernelInformationCollectorVisitor
from pynestml.utils.ast_utils import ASTUtils

from odetoolbox import analysis

from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages


class SynapseProcessing:
    """
    This file is part of the compartmental code generation process.

    Synapse information processing.
    """

    # used to keep track of whenever check_co_co was already called
    # see inside check_co_co
    first_time_run = defaultdict(lambda: True)
    # stores synapse from the first call of check_co_co
    syn_info = defaultdict()

    # ODE-toolbox printers
    _constant_printer = ConstantPrinter()
    _ode_toolbox_variable_printer = ODEToolboxVariablePrinter(None)
    _ode_toolbox_function_call_printer = ODEToolboxFunctionCallPrinter(None)
    _ode_toolbox_printer = ODEToolboxExpressionPrinter(
        simple_expression_printer=SympySimpleExpressionPrinter(
            variable_printer=_ode_toolbox_variable_printer,
            constant_printer=_constant_printer,
            function_call_printer=_ode_toolbox_function_call_printer))

    _ode_toolbox_variable_printer._expression_printer = _ode_toolbox_printer
    _ode_toolbox_function_call_printer._expression_printer = _ode_toolbox_printer

    @classmethod
    def prepare_equations_for_ode_toolbox(cls, synapse, syn_info):
        """Transforms the collected ode equations to the required input format of ode-toolbox and adds it to the
        syn_info dictionary"""

        mechanism_odes = defaultdict()
        for ode in syn_info["ODEs"]:
            nestml_printer = NESTMLPrinter()
            ode_nestml_expression = nestml_printer.print_ode_equation(ode)
            mechanism_odes[ode.lhs.name] = defaultdict()
            mechanism_odes[ode.lhs.name]["ASTOdeEquation"] = ode
            mechanism_odes[ode.lhs.name]["ODENestmlExpression"] = ode_nestml_expression
        syn_info["ODEs"] = mechanism_odes

        for ode_variable_name, ode_info in syn_info["ODEs"].items():
            # Expression:
            odetoolbox_indict = {"dynamics": []}
            lhs = ASTUtils.to_ode_toolbox_name(ode_info["ASTOdeEquation"].get_lhs().get_complete_name())
            rhs = cls._ode_toolbox_printer.print(ode_info["ASTOdeEquation"].get_rhs())
            entry = {"expression": lhs + " = " + rhs, "initial_values": {}}

            # Initial values:
            symbol_order = ode_info["ASTOdeEquation"].get_lhs().get_differential_order()
            for order in range(symbol_order):
                iv_symbol_name = ode_info["ASTOdeEquation"].get_lhs().get_name() + "'" * order
                initial_value_expr = synapse.get_initial_value(iv_symbol_name)
                entry["initial_values"][
                    ASTUtils.to_ode_toolbox_name(iv_symbol_name)] = cls._ode_toolbox_printer.print(
                    initial_value_expr)

            odetoolbox_indict["dynamics"].append(entry)
            syn_info["ODEs"][ode_variable_name]["ode_toolbox_input"] = odetoolbox_indict

        return syn_info

    @classmethod
    def collect_raw_odetoolbox_output(cls, syn_info):
        """calls ode-toolbox for each ode individually and collects the raw output"""
        for ode_variable_name, ode_info in syn_info["ODEs"].items():
            solver_result = analysis(ode_info["ode_toolbox_input"], disable_stiffness_check=True)
            syn_info["ODEs"][ode_variable_name]["ode_toolbox_output"] = solver_result

        return syn_info

    @classmethod
    def ode_toolbox_processing(cls, synapse, syn_info):
        syn_info = cls.prepare_equations_for_ode_toolbox(synapse, syn_info)
        syn_info = cls.collect_raw_odetoolbox_output(syn_info)
        return syn_info

    @classmethod
    def collect_information_for_specific_mech_types(cls, synapse, syn_info):
        # to be implemented for specific mechanisms by child class (concentration, synapse, channel)
        pass

    @classmethod
    def determine_dependencies(cls, syn_info):
        for mechanism_name, mechanism_info in syn_info.items():
            dependencies = list()
            for inline in mechanism_info["Inlines"]:
                if isinstance(inline.get_decorators(), list):
                    if "mechanism" in [e.namespace for e in inline.get_decorators()]:
                        dependencies.append(inline)
            for ode in mechanism_info["ODEs"]:
                if isinstance(ode.get_decorators(), list):
                    if "mechanism" in [e.namespace for e in ode.get_decorators()]:
                        dependencies.append(ode)
            syn_info[mechanism_name]["dependencies"] = dependencies
        return syn_info

    @classmethod
    def get_port_names(cls, syn_info):
        spiking_port_names = list()
        continuous_port_names = list()
        for port in syn_info["SpikingPorts"]:
            spiking_port_names.append(port.get_name())
        for port in syn_info["ContinuousPorts"]:
            continuous_port_names.append(port.get_name())

        return spiking_port_names, continuous_port_names

    @classmethod
    def collect_kernels(cls, neuron, syn_info, neuron_synapse_pairs):
        """
        Collect internals, kernels, inputs and convolutions associated with the synapse.
        """
        syn_info["convolutions"] = defaultdict()
        info_collector = ASTKernelInformationCollectorVisitor()
        neuron.accept(info_collector)
        for inline in syn_info["Inlines"]:
            synapse_inline = inline
            syn_info[
                "internals_used_declared"] = info_collector.get_synapse_specific_internal_declarations(synapse_inline)
            syn_info["total_used_declared"] = info_collector.get_variable_names_of_synapse(
                synapse_inline)

            kernel_arg_pairs = info_collector.get_extracted_kernel_args_by_name(
                inline.get_variable_name())
            for kernel_var, spikes_var in kernel_arg_pairs:
                kernel_name = kernel_var.get_name()
                spikes_name = spikes_var.get_name()
                if spikes_name != "self_spikes":
                    convolution_name = info_collector.construct_kernel_X_spike_buf_name(
                        kernel_name, spikes_name, 0)
                    syn_info["convolutions"][convolution_name] = {
                        "kernel": {
                            "name": kernel_name,
                            "ASTKernel": info_collector.get_kernel_by_name(kernel_name),
                        },
                        "spikes": {
                            "name": spikes_name,
                            "ASTInputPort": info_collector.get_input_port_by_name(spikes_name),
                        },
                        "post_port": (len([dict for dict in neuron_synapse_pairs if
                                           dict["synapse"] + "_nestml" == neuron.name and spikes_name in dict[
                                               "post_ports"]]) > 0),
                    }
        return syn_info

    @classmethod
    def collect_and_check_inputs_per_synapse(
            cls,
            syn_info: dict):
        new_syn_info = copy.copy(syn_info)

        # collect all buffers used
        new_syn_info["buffers_used"] = set()
        for convolution_name, convolution_info in syn_info["convolutions"].items(
        ):
            input_name = convolution_info["spikes"]["name"]
            new_syn_info["buffers_used"].add(input_name)

        return new_syn_info

    @classmethod
    def convolution_ode_toolbox_processing(cls, neuron, syn_info):
        if not neuron.get_parameters_blocks():
            return syn_info

        parameters_block = neuron.get_parameters_blocks()[0]

        for convolution_name, convolution_info in syn_info["convolutions"].items():
            kernel_buffer = (convolution_info["kernel"]["ASTKernel"], convolution_info["spikes"]["ASTInputPort"])
            convolution_solution = cls.ode_solve_convolution(neuron, parameters_block, kernel_buffer)
            syn_info["convolutions"][convolution_name]["analytic_solution"] = convolution_solution
        return syn_info

    @classmethod
    def ode_solve_convolution(cls,
                              neuron: ASTModel,
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
                          neuron: ASTModel,
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
            neuron: ASTModel,
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

    @classmethod
    def get_syn_info(cls, synapse: ASTModel):
        """
        returns previously generated syn_info
        as a deep copy so it can't be changed externally
        via object references
        :param synapse: a single synapse instance.
        """
        return copy.deepcopy(cls.syn_info)

    @classmethod
    def process(cls, synapse: ASTModel, neuron_synapse_pairs):
        """
        Checks if mechanism conditions apply for the handed over synapse.
        :param synapse: a single synapse instance.
        """

        # make sure we only run this a single time
        # subsequent calls will be after AST has been transformed
        # and there would be no kernels or inlines any more
        if cls.first_time_run[synapse]:
            # collect root expressions and initialize collector
            info_collector = ASTSynapseInformationCollector(synapse)

            # collect and process all basic mechanism information
            syn_info = defaultdict()
            syn_info = info_collector.collect_definitions(synapse, syn_info)
            syn_info = info_collector.extend_variables_with_initialisations(synapse, syn_info)
            syn_info = cls.ode_toolbox_processing(synapse, syn_info)

            # collect all spiking ports
            syn_info = info_collector.collect_ports(synapse, syn_info)

            # collect the onReceive function of pre- and post-spikes
            spiking_port_names, continuous_port_names = cls.get_port_names(syn_info)
            post_ports = FrontendConfiguration.get_codegen_opts()["neuron_synapse_pairs"][0]["post_ports"]
            pre_ports = list(set(spiking_port_names) - set(post_ports))
            syn_info = info_collector.collect_on_receive_blocks(synapse, syn_info, pre_ports, post_ports)

            # get corresponding delay variable
            syn_info["DelayVariable"] = FrontendConfiguration.get_codegen_opts()["delay_variable"][synapse.get_name().removesuffix("_nestml")]

            # collect the update block
            syn_info = info_collector.collect_update_block(synapse, syn_info)

            # collect dependencies (defined mechanism in neuron and no LHS appearance in synapse)
            syn_info = info_collector.collect_potential_dependencies(synapse, syn_info)

            syn_info = cls.collect_kernels(synapse, syn_info, neuron_synapse_pairs)

            syn_info = cls.convolution_ode_toolbox_processing(synapse, syn_info)

            cls.syn_info[synapse.get_name()] = syn_info
            cls.first_time_run[synapse.get_name()] = False

    @classmethod
    def print_element(cls, name, element, rec_step):
        message = ""
        for indent in range(rec_step):
            message += "----"
        message += name + ": "
        if isinstance(element, defaultdict):
            message += "\n"
            message += cls.print_dictionary(element, rec_step + 1)
        else:
            if hasattr(element, 'name'):
                message += element.name
            elif isinstance(element, str):
                message += element
            elif isinstance(element, dict):
                message += "\n"
                message += cls.print_dictionary(element, rec_step + 1)
            elif isinstance(element, list):
                for index in range(len(element)):
                    message += "\n"
                    message += cls.print_element(str(index), element[index], rec_step + 1)
            elif isinstance(element, ASTExpression) or isinstance(element, ASTSimpleExpression):
                message += cls._ode_toolbox_printer.print(element)

            message += "(" + type(element).__name__ + ")"
        return message

    @classmethod
    def print_dictionary(cls, dictionary, rec_step):
        """
        Print the mechanisms info dictionaries.
        """
        message = ""
        for name, element in dictionary.items():
            message += cls.print_element(name, element, rec_step)
            message += "\n"
        return message
