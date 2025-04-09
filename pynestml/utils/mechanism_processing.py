# -*- coding: utf-8 -*-
#
# mechanism_processing.py
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

from pynestml.utils.logger import Logger, LoggingLevel

from pynestml.utils.messages import Messages

from pynestml.frontend.frontend_configuration import FrontendConfiguration

from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables

from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.codegeneration.printers.sympy_simple_expression_printer import SympySimpleExpressionPrinter

from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter
from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter
from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter
from pynestml.codegeneration.printers.ode_toolbox_function_call_printer import ODEToolboxFunctionCallPrinter
from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.utils.ast_mechanism_information_collector import ASTMechanismInformationCollector
from pynestml.utils.ast_utils import ASTUtils

from odetoolbox import analysis


class MechanismProcessing:
    """Manages the collection of basic information necesary for all types of mechanisms and uses the
    collect_information_for_specific_mech_types interface that needs to be implemented by the specific mechanism type
    processing classes"""

    # used to keep track of whenever check_co_co was already called
    # see inside check_co_co
    first_time_run = defaultdict(lambda: defaultdict(lambda: True))
    # stores syns_info from the first call of check_co_co
    mechs_info = defaultdict(lambda: defaultdict())

    mechType = str()

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
    def prepare_equations_for_ode_toolbox(cls, neuron, mechs_info):
        """Transforms the collected ode equations to the required input format of ode-toolbox and adds it to the
        mechs_info dictionary"""
        for mechanism_name, mechanism_info in mechs_info.items():
            mechanism_odes = defaultdict()
            for ode in mechanism_info["ODEs"]:
                nestml_printer = NESTMLPrinter()
                ode_nestml_expression = nestml_printer.print_ode_equation(ode)
                mechanism_odes[ode.lhs.name] = defaultdict()
                mechanism_odes[ode.lhs.name]["ASTOdeEquation"] = ode
                mechanism_odes[ode.lhs.name]["ODENestmlExpression"] = ode_nestml_expression
            mechs_info[mechanism_name]["ODEs"] = mechanism_odes

        for mechanism_name, mechanism_info in mechs_info.items():
            for ode_variable_name, ode_info in mechanism_info["ODEs"].items():
                # Expression:
                odetoolbox_indict = {"dynamics": []}
                lhs = ASTUtils.to_ode_toolbox_name(ode_info["ASTOdeEquation"].get_lhs().get_complete_name())
                rhs = cls._ode_toolbox_printer.print(ode_info["ASTOdeEquation"].get_rhs())
                entry = {"expression": lhs + " = " + rhs, "initial_values": {}}

                # Initial values:
                symbol_order = ode_info["ASTOdeEquation"].get_lhs().get_differential_order()
                for order in range(symbol_order):
                    iv_symbol_name = ode_info["ASTOdeEquation"].get_lhs().get_name() + "'" * order
                    initial_value_expr = neuron.get_initial_value(iv_symbol_name)
                    entry["initial_values"][
                        ASTUtils.to_ode_toolbox_name(iv_symbol_name)] = cls._ode_toolbox_printer.print(
                        initial_value_expr)

                odetoolbox_indict["dynamics"].append(entry)
                mechs_info[mechanism_name]["ODEs"][ode_variable_name]["ode_toolbox_input"] = odetoolbox_indict

        return mechs_info

    @classmethod
    def collect_raw_odetoolbox_output(cls, mechs_info):
        """calls ode-toolbox for each ode individually and collects the raw output"""
        for mechanism_name, mechanism_info in mechs_info.items():
            for ode_variable_name, ode_info in mechanism_info["ODEs"].items():
                solver_result = analysis(ode_info["ode_toolbox_input"], disable_stiffness_check=True)
                mechs_info[mechanism_name]["ODEs"][ode_variable_name]["ode_toolbox_output"] = solver_result

        return mechs_info

    @classmethod
    def ode_toolbox_processing(cls, neuron, mechs_info):
        mechs_info = cls.prepare_equations_for_ode_toolbox(neuron, mechs_info)
        mechs_info = cls.collect_raw_odetoolbox_output(mechs_info)
        return mechs_info

    @classmethod
    def collect_information_for_specific_mech_types(cls, neuron, mechs_info):
        # to be implemented for specific mechanisms by child class (concentration, synapse, channel)
        pass

    @classmethod
    def determine_dependencies(cls, mechs_info):
        for mechanism_name, mechanism_info in mechs_info.items():
            dependencies = list()
            for inline in mechanism_info["SecondaryInlineExpressions"]:
                if isinstance(inline.get_decorators(), list):
                    if "mechanism" in [e.namespace for e in inline.get_decorators()]:
                        dependencies.append(inline)
            for ode in mechanism_info["ODEs"]:
                if isinstance(ode.get_decorators(), list):
                    if "mechanism" in [e.namespace for e in ode.get_decorators()]:
                        dependencies.append(ode)
            mechs_info[mechanism_name]["dependencies"] = dependencies
        return mechs_info

    @classmethod
    def convolution_ode_toolbox_processing(cls, neuron, mechs_info):
        for mechanism_name, mechanism_info in mechs_info.items():
            parameters_block = None
            if neuron.get_parameters_blocks():
                parameters_block = neuron.get_parameters_blocks()[0]
            for convolution_name, convolution_info in mechanism_info["convolutions"].items():
                kernel_buffer = (convolution_info["kernel"]["ASTKernel"], convolution_info["spikes"]["ASTInputPort"])
                convolution_solution = cls.ode_solve_convolution(neuron, parameters_block, kernel_buffer)
                mechanism_info["convolutions"][convolution_name]["analytic_solution"] = convolution_solution
        return mechs_info

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

    #@classmethod
    #def compute_update_block_variations(cls, info_collector, mechs_info, global_info):
    #    if global_info["UpdateBlock"] is not None:
    #        info_collector.collect_update_block_dependencies_and_owned(mechs_info, global_info)
    #        global_info["UpdateBlock"] = info_collector.recursive_update_block_reduction(mechs_info, [],
    #                                                                                     global_info["UpdateBlock"])

    @classmethod
    def extract_mech_blocks(cls, info_collector, mechs_info, global_info):
        block_list = list()
        if "UpdateBlock" in global_info and global_info["UpdateBlock"] is not None:
            block_list.append(global_info["UpdateBlock"].get_stmts_body())
        if "SelfSpikesFunction" in global_info and global_info["SelfSpikesFunction"] is not None:
            block_list.append(global_info["SelfSpikesFunction"].get_stmts_body())
        if len(block_list) > 0:
            info_collector.collect_block_dependencies_and_owned(mechs_info, block_list, "UpdateBlock")
            if "UpdateBlock" in global_info  and global_info["UpdateBlock"] is not None:
                info_collector.block_reduction(mechs_info, global_info["UpdateBlock"], "UpdateBlock")
            if "SelfSpikesFunction" in global_info and global_info["SelfSpikesFunction"] is not None:
                info_collector.block_reduction(mechs_info, global_info["SelfSpikesFunction"], "SelfSpikesFunction")


    @classmethod
    def get_mechs_info(cls, neuron: ASTModel):
        """
        returns previously generated mechs_info
        as a deep copy so it can't be changed externally
        via object references
        :param neuron: a single neuron instance.
        """

        return copy.deepcopy(cls.mechs_info[neuron][cls.mechType])

    @classmethod
    def check_co_co(cls, neuron: ASTModel, global_info):
        """
        Checks if mechanism conditions apply for the handed over neuron.
        :param neuron: a single neuron instance.
        """

        # make sure we only run this a single time
        # subsequent calls will be after AST has been transformed
        # and there would be no kernels or inlines any more
        if cls.first_time_run[neuron][cls.mechType]:
            # collect root expressions and initialize collector
            info_collector = ASTMechanismInformationCollector(neuron)
            mechs_info = info_collector.detect_mechs(cls.mechType)

            # collect and process all basic mechanism information
            mechs_info = info_collector.collect_mechanism_related_definitions(neuron, mechs_info, global_info, cls.mechType)
            cls.extract_mech_blocks(info_collector, mechs_info, global_info)
            mechs_info = info_collector.extend_variables_with_initialisations(neuron, mechs_info)

            mechs_info = info_collector.collect_kernels(neuron, mechs_info)
            mechs_info = cls.convolution_ode_toolbox_processing(neuron, mechs_info)

            # collect and process all mechanism type specific information
            mechs_info = cls.collect_information_for_specific_mech_types(neuron, mechs_info)

            cls.mechs_info[neuron][cls.mechType] = mechs_info
            cls.first_time_run[neuron][cls.mechType] = False

    @classmethod
    def get_transformed_ode_equations(cls, mechs_info: dict):
        from pynestml.utils.mechs_info_enricher import SynsInfoEnricherVisitor
        enriched_mechs_info = copy.copy(mechs_info)
        for mechanism_name, mechanism_info in mechs_info.items():
            transformed_odes = list()
            for ode in mechs_info[mechanism_name]["ODEs"]:
                ode_name = ode.lhs.name
                transformed_odes.append(
                    SynsInfoEnricherVisitor.ode_name_to_transformed_ode[ode_name])
            enriched_mechs_info[mechanism_name]["ODEs"] = transformed_odes

        return enriched_mechs_info

    @classmethod
    def check_all_convolutions_with_self_spikes(cls, mechs_info):
        for mechanism_name, mechanism_info in mechs_info.items():
            for convolution_name, convolution in mechanism_info["convolutions"].items():
                if convolution["spikes"]["name"] != "self_spikes":
                    code, message = Messages.cm_non_self_spike_convolution_in_mech(mechanism_name, cls.mechType)
                    Logger.log_message(error_position=None,
                                       code=code, message=message,
                                       log_level=LoggingLevel.ERROR)

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
            elif isinstance(element, bool):
                message += str(element)
            elif isinstance(element, dict):
                message += "\n"
                message += cls.print_dictionary(element, rec_step + 1)
            elif isinstance(element, list):
                for index in range(len(element)):
                    message += "\n"
                    message += cls.print_element(str(index), element[index], rec_step + 1)
            elif isinstance(element, ASTExpression) or isinstance(element, ASTSimpleExpression):
                message += cls._ode_toolbox_printer.print(element)
            elif isinstance(element, ASTInlineExpression):
                message += cls._ode_toolbox_printer.print(element.get_expression())

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
