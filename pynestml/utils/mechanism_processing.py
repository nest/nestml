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

from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.ast_mechanism_information_collector import ASTMechanismInformationCollector

from pynestml.utils.ast_utils import ASTUtils
from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter

from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter
from pynestml.codegeneration.printers.ode_toolbox_function_call_printer import ODEToolboxFunctionCallPrinter
from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter
from pynestml.codegeneration.printers.unitless_cpp_simple_expression_printer import UnitlessCppSimpleExpressionPrinter
from odetoolbox import analysis

from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression


class MechanismProcessing(object):
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
        simple_expression_printer=UnitlessCppSimpleExpressionPrinter(
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
    def get_mechs_info(cls, neuron: ASTNeuron):
        """
        returns previously generated mechs_info
        as a deep copy so it can't be changed externally
        via object references
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """

        return copy.deepcopy(cls.mechs_info[neuron][cls.mechType])

    @classmethod
    def check_co_co(cls, neuron: ASTNeuron):
        """
        Checks if mechanism conditions apply for the handed over neuron.
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """

        # make sure we only run this a single time
        # subsequent calls will be after AST has been transformed
        # and there would be no kernels or inlines any more
        if cls.first_time_run[neuron][cls.mechType]:
            # collect root expressions and initialize collector
            info_collector = ASTMechanismInformationCollector(neuron)
            mechs_info = info_collector.detect_mechs(cls.mechType)

            # collect and process all basic mechanism information
            mechs_info = info_collector.collect_mechanism_related_definitions(neuron, mechs_info)
            mechs_info = info_collector.extend_variables_with_initialisations(neuron, mechs_info)
            mechs_info = cls.ode_toolbox_processing(neuron, mechs_info)

            # collect and process all mechanism type specific information
            mechs_info = cls.collect_information_for_specific_mech_types(neuron, mechs_info)

            cls.mechs_info[neuron][cls.mechType] = mechs_info
            cls.first_time_run[neuron][cls.mechType] = False

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
