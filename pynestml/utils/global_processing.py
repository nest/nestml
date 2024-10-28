# -*- coding: utf-8 -*-
#
# global_processing.py
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
from pynestml.codegeneration.printers.unitless_cpp_simple_expression_printer import UnitlessCppSimpleExpressionPrinter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.utils.ast_global_information_collector import ASTGlobalInformationCollector
from pynestml.utils.ast_utils import ASTUtils

from odetoolbox import analysis

class GlobalProcessing:
    """Manages the collection of basic information necesary for all types of mechanisms and uses the
    collect_information_for_specific_mech_types interface that needs to be implemented by the specific mechanism type
    processing classes"""

    # used to keep track of whenever check_co_co was already called
    # see inside check_co_co
    first_time_run = defaultdict(lambda: True)
    # stores neuron from the first call of check_co_co
    global_info = defaultdict()

    # ODE-toolbox printers
    _constant_printer = ConstantPrinter()
    _ode_toolbox_variable_printer = ODEToolboxVariablePrinter(None)
    _ode_toolbox_function_call_printer = ODEToolboxFunctionCallPrinter(None)
    _ode_toolbox_printer = ODEToolboxExpressionPrinter(
        simple_expression_printer=UnitlessCppSimpleExpressionPrinter(
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
    def ode_toolbox_processing(cls, neuron, global_info):
        global_info = cls.prepare_equations_for_ode_toolbox(neuron, global_info)
        global_info = cls.collect_raw_odetoolbox_output(global_info)
        return global_info

    @classmethod
    def get_global_info(cls, neuron):
        """
        returns previously generated global_info
        as a deep copy so it can't be changed externally
        via object references
        :param neuron: a single neuron instance.
        """
        # breakpoint()
        return copy.deepcopy(cls.global_info[neuron.get_name()])

    @classmethod
    def check_co_co(cls, neuron: ASTModel):
        """
        Checks if mechanism conditions apply for the handed over neuron.
        :param neuron: a single neuron instance.
        """

        # make sure we only run this a single time
        # subsequent calls will be after AST has been transformed
        # and there would be no kernels or inlines anymore
        if cls.first_time_run[neuron]:
            # collect root expressions and initialize collector
            info_collector = ASTGlobalInformationCollector(neuron)

            # collect and process all basic mechanism information
            global_info = defaultdict()

            global_info = info_collector.collect_update_block(neuron, global_info)
            global_info = info_collector.collect_self_spike_function(neuron, global_info)

            global_info = info_collector.collect_related_definitions(neuron, global_info)
            global_info = info_collector.extend_variables_with_initialisations(neuron, global_info)
            global_info = cls.ode_toolbox_processing(neuron, global_info)

            cls.global_info[neuron.get_name()] = global_info
            cls.first_time_run[neuron.get_name()] = False

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