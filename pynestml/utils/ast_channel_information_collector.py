# -*- coding: utf-8 -*-
#
# ast_channel_information_collector.py
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

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter

#--------------ode additional imports

from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter
from pynestml.codegeneration.printers.ode_toolbox_function_call_printer import ODEToolboxFunctionCallPrinter
from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter
from pynestml.codegeneration.printers.unitless_cpp_simple_expression_printer import UnitlessCppSimpleExpressionPrinter
from pynestml.utils.ast_utils import ASTUtils
from odetoolbox import analysis
import json


class ASTChannelInformationCollector(object):
    """
    This class is used to enforce constraint conditions on a compartmental model neuron

    While checking compartmental model constraints it also builds a nested
    data structure (chan_info) that can be used for code generation later

    Constraints:

    It ensures that all variables x as used in the inline expression named {channelType}
    (which has no kernels and is inside ASTEquationsBlock)
    have the following compartmental model functions defined

        x_inf_{channelType}(v_comp real) real
        tau_x_{channelType}(v_comp real) real


    Example:
        equations:
            inline Na real = m_Na_**3 * h_Na_**1
        end

        # triggers requirements for functions such as
        function h_inf_Na(v_comp real) real:
            return 1.0/(exp(0.16129032258064516*v_comp + 10.483870967741936) + 1.0)
        end

        function tau_h_Na(v_comp real) real:
            return 0.3115264797507788/((-0.0091000000000000004*v_comp - 0.68261830000000012)/(1.0 - 3277527.8765015295*exp(0.20000000000000001*v_comp)) + (0.024*v_comp + 1.200312)/(1.0 - 4.5282043263959816e-5*exp(-0.20000000000000001*v_comp)))
        end

    Moreover it checks
    -if all expected sates are defined,
    -that at least one gating variable exists (which is recognize when variable name ends with _{channel_name} )
    -that no gating variable repeats inside the inline expression that triggers cm mechanism
    Example:
        inline Na real = m_Na**3 * h_Na**1

    #causes the requirement for following entries in the state block

        gbar_Na
        e_Na
        m_Na
        h_Na

    Other allowed examples:
        # any variable that does not end with _Na is allowed
        inline Na real = m_Na**3 * h_Na**1 + x
        # gbar and e variables will not be counted as gating variables
        inline Na real = gbar_Na * m_Na**3 * h_Na**1 * (e_Na - v_comp) # gating variables detected: m and h

    Not allowed examples:
        inline Na real = p_Na **3 + p_Na **1  # same gating variable used twice
        inline Na real = x**2                 # no gating variables

    """

    padding_character = "_"
    inf_string = "inf"
    tau_sring = "tau"
    gbar_string = "gbar"
    equilibrium_string = "e"

    first_time_run = defaultdict(lambda: True)
    chan_info = defaultdict()

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

    def __init__(self, params):
        '''
        Constructor
        '''

    """
    detect_cm_inline_expressions

    analyzes any inline without kernels and returns

    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "gating_variables": [ASTVariable, ASTVariable, ASTVariable, ...], # potential gating variables

        },
        "K":
        {
            ...
        }
    }
    """

    @classmethod
    def detect_cm_inline_expressions(cls, neuron):
        if not FrontendConfiguration.target_is_compartmental():
            return defaultdict()

        # search for inline expressions inside equations block
        inline_expressions_inside_equations_block_collector_visitor = ASTInlineExpressionInsideEquationsCollectorVisitor()
        neuron.accept(
            inline_expressions_inside_equations_block_collector_visitor)
        inline_expressions_dict = inline_expressions_inside_equations_block_collector_visitor.inline_expressions_to_variables

        # filter for any inline that has no kernel
        relevant_inline_expressions_to_variables = defaultdict(lambda: list())
        for expression, variables in inline_expressions_dict.items():
            inline_expression_name = expression.variable_name
            if not inline_expressions_inside_equations_block_collector_visitor.is_synapse_inline(
                    inline_expression_name):
                relevant_inline_expressions_to_variables[expression] = variables

        # create info structure
        chan_info = defaultdict()
        for inline_expression, inner_variables in relevant_inline_expressions_to_variables.items():
            info = defaultdict()
            channel_name = cls.cm_expression_to_channel_name(inline_expression)
            info["ASTInlineExpression"] = inline_expression
            info["gating_variables"] = inner_variables
            chan_info[channel_name] = info

        return chan_info

    # extract channel name from inline expression name
    # i.e  Na_ -> channel name is Na
    @classmethod
    def cm_expression_to_channel_name(cls, expr):
        assert isinstance(expr, ASTInlineExpression)
        return expr.variable_name.strip(cls.padding_character)

    # extract pure variable name from inline expression variable name
    # i.e  p_Na -> pure variable name is p
    @classmethod
    def extract_pure_variable_name(cls, varname, ic_name):
        varname = varname.strip(cls.padding_character)
        assert varname.endswith(ic_name)
        return varname[:-len(ic_name)].strip(cls.padding_character)

    # generate gbar variable name from ion channel name
    # i.e  Na -> gbar_Na
    @classmethod
    def get_expected_gbar_name(cls, ion_channel_name):
        return cls.gbar_string + cls.padding_character + ion_channel_name

    # generate equilibrium variable name from ion channel name
    # i.e  Na -> e_Na
    @classmethod
    def get_expected_equilibrium_var_name(cls, ion_channel_name):
        return cls.equilibrium_string + cls.padding_character + ion_channel_name

    # generate tau function name from ion channel name
    # i.e  Na, p -> tau_p_Na
    @classmethod
    def get_expected_tau_result_var_name(
            cls, ion_channel_name, pure_variable_name):
        return cls.padding_character + \
            cls.get_expected_tau_function_name(ion_channel_name, pure_variable_name)

    # generate tau variable name (stores return value)
    # from ion channel name and pure variable name
    # i.e  Na, p -> _tau_p_Na
    @classmethod
    def get_expected_tau_function_name(
            cls, ion_channel_name, pure_variable_name):
        return cls.tau_sring + cls.padding_character + \
            pure_variable_name + cls.padding_character + ion_channel_name

    # generate inf function name from ion channel name and pure variable name
    # i.e  Na, p -> p_inf_Na
    @classmethod
    def get_expected_inf_result_var_name(
            cls, ion_channel_name, pure_variable_name):
        return cls.padding_character + \
            cls.get_expected_inf_function_name(ion_channel_name, pure_variable_name)

    # generate inf variable name (stores return value)
    # from ion channel name and pure variable name
    # i.e  Na, p -> _p_inf_Na
    @classmethod
    def get_expected_inf_function_name(
            cls, ion_channel_name, pure_variable_name):
        return pure_variable_name + cls.padding_character + \
            cls.inf_string + cls.padding_character + ion_channel_name

    # calculate function names that must be implemented
    # i.e
    # m_Na**3 * h_Na**1
    # expects
    # m_inf_Na(v_comp real) real
    # tau_m_Na(v_comp real) real
    """
    analyzes cm inlines for expected function names
    input:
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "gating_variables": [ASTVariable, ASTVariable, ASTVariable, ...]

        },
        "K":
        {
            ...
        }
    }

    output:
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "gating_variables":
            {
                "m":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": str,
                        "inf": str
                    }
                },
                "h":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": str,
                        "inf": str
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }

    """

    @classmethod
    def calc_expected_function_names_for_channels(cls, chan_info):
        variables_procesed = defaultdict()

        for ion_channel_name, channel_info in chan_info.items():
            cm_expression = channel_info["ASTInlineExpression"]
            variables = channel_info["gating_variables"]
            variable_names_seen = set()

            variables_info = defaultdict()
            channel_parameters_exclude = cls.get_expected_equilibrium_var_name(
                ion_channel_name), cls.get_expected_gbar_name(ion_channel_name)

            for variable_used in variables:
                variable_name = variable_used.name.strip(cls.padding_character)
                if not variable_name.endswith(ion_channel_name):
                    # not a gating variable
                    continue

                # exclude expected channel parameters
                if variable_name in channel_parameters_exclude:
                    continue

                # enforce unique variable names per channel, i.e n and m , not
                # n and n
                if variable_name in variable_names_seen:
                    code, message = Messages.get_cm_inline_expression_variable_used_mulitple_times(
                        cm_expression, variable_name, ion_channel_name)
                    Logger.log_message(
                        code=code,
                        message=message,
                        error_position=variable_used.get_source_position(),
                        log_level=LoggingLevel.ERROR,
                        node=variable_used)
                    continue
                else:
                    variable_names_seen.add(variable_name)

                pure_variable_name = cls.extract_pure_variable_name(
                    variable_name, ion_channel_name)
                expected_inf_function_name = cls.get_expected_inf_function_name(
                    ion_channel_name, pure_variable_name)
                expected_tau_function_name = cls.get_expected_tau_function_name(
                    ion_channel_name, pure_variable_name)

                variables_info[pure_variable_name] = defaultdict(
                    lambda: defaultdict())
                variables_info[pure_variable_name]["expected_functions"][cls.inf_string] = expected_inf_function_name
                variables_info[pure_variable_name]["expected_functions"][cls.tau_sring] = expected_tau_function_name
                variables_info[pure_variable_name]["ASTVariable"] = variable_used

            variables_procesed[ion_channel_name] = copy.copy(variables_info)

        for ion_channel_name, variables_info in variables_procesed.items():
            chan_info[ion_channel_name]["gating_variables"] = variables_info

        return chan_info

    """
    generate Errors on invalid variable names
    and add channel_parameters section to each channel

    input:
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "gating_variables":
            {
                "m":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                },
                "h":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }

    output:

    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "channel_parameters":
            {
                "gbar":{"expected_name": "gbar_Na"},
                "e":{"expected_name": "e_Na"}
            }
            "gating_variables":
            {
                "m":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                },
                "h":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }

    """
    @classmethod
    def add_channel_parameters_section_and_enforce_proper_variable_names(
            cls, node, chan_info):
        ret = copy.copy(chan_info)

        channel_parameters = defaultdict()
        for ion_channel_name, channel_info in chan_info.items():
            channel_parameters[ion_channel_name] = defaultdict()
            channel_parameters[ion_channel_name][cls.gbar_string] = defaultdict()
            channel_parameters[ion_channel_name][cls.gbar_string]["expected_name"] = cls.get_expected_gbar_name(ion_channel_name)
            channel_parameters[ion_channel_name][cls.equilibrium_string] = defaultdict()
            channel_parameters[ion_channel_name][cls.equilibrium_string]["expected_name"] = cls.get_expected_equilibrium_var_name(ion_channel_name)

            if len(channel_info["gating_variables"]) < 1:
                cm_inline_expr = channel_info["ASTInlineExpression"]
                code, message = Messages.get_no_gating_variables(
                    cm_inline_expr, ion_channel_name)
                Logger.log_message(
                    code=code,
                    message=message,
                    error_position=cm_inline_expr.get_source_position(),
                    log_level=LoggingLevel.ERROR,
                    node=cm_inline_expr)
                continue

        for ion_channel_name, channel_info in chan_info.items():
            ret[ion_channel_name]["channel_parameters"] = channel_parameters[ion_channel_name]

        return ret

    """
    checks if all expected functions exist and have the proper naming and signature
    also finds their corresponding ASTFunction objects

    input
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "gating_variables":
            {
                "m":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": str,
                        "inf": str
                    }
                },
                "h":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": str,
                        "inf": str
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }

    output
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "gating_variables":
            {
                "m":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                },
                "h":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }
    """
    @classmethod
    def check_and_find_functions(cls, neuron, chan_info):
        ret = copy.copy(chan_info)
        # get functions and collect their names
        declared_functions = neuron.get_functions()

        function_name_to_function = {}
        for declared_function in declared_functions:
            function_name_to_function[declared_function.name] = declared_function

        # check for missing functions
        for ion_channel_name, channel_info in chan_info.items():
            for pure_variable_name, variable_info in channel_info["gating_variables"].items(
            ):
                if "expected_functions" in variable_info.keys():
                    for function_type, expected_function_name in variable_info["expected_functions"].items(
                    ):
                        if expected_function_name not in function_name_to_function.keys():
                            code, message = Messages.get_expected_cm_function_missing(
                                ion_channel_name, variable_info["ASTVariable"].name, expected_function_name)
                            Logger.log_message(
                                code=code,
                                message=message,
                                error_position=neuron.get_source_position(),
                                log_level=LoggingLevel.ERROR,
                                node=neuron)
                        else:
                            ret[ion_channel_name]["gating_variables"][pure_variable_name]["expected_functions"][function_type] = defaultdict()
                            ret[ion_channel_name]["gating_variables"][pure_variable_name]["expected_functions"][
                                function_type]["ASTFunction"] = function_name_to_function[expected_function_name]
                            ret[ion_channel_name]["gating_variables"][pure_variable_name][
                                "expected_functions"][function_type]["function_name"] = expected_function_name

                            # function must have exactly one argument
                            astfun = ret[ion_channel_name]["gating_variables"][pure_variable_name][
                                "expected_functions"][function_type]["ASTFunction"]
                            if len(astfun.parameters) != 1:
                                code, message = Messages.get_expected_cm_function_wrong_args_count(
                                    ion_channel_name, variable_info["ASTVariable"].name, astfun)
                                Logger.log_message(
                                    code=code,
                                    message=message,
                                    error_position=astfun.get_source_position(),
                                    log_level=LoggingLevel.ERROR,
                                    node=astfun)

                            # function must return real
                            if not astfun.get_return_type().is_real:
                                code, message = Messages.get_expected_cm_function_bad_return_type(
                                    ion_channel_name, astfun)
                                Logger.log_message(
                                    code=code,
                                    message=message,
                                    error_position=astfun.get_source_position(),
                                    log_level=LoggingLevel.ERROR,
                                    node=astfun)

                            if function_type == "tau":
                                ret[ion_channel_name]["gating_variables"][pure_variable_name]["expected_functions"][function_type][
                                    "result_variable_name"] = cls.get_expected_tau_result_var_name(ion_channel_name, pure_variable_name)
                            elif function_type == "inf":
                                ret[ion_channel_name]["gating_variables"][pure_variable_name]["expected_functions"][function_type][
                                    "result_variable_name"] = cls.get_expected_inf_result_var_name(ion_channel_name, pure_variable_name)
                            else:
                                raise RuntimeError(
                                    'This should never happen! Unsupported function type ' + function_type + ' from variable ' + pure_variable_name)

        return ret


#----------------------- New collection functions for generalized ODE Descriptions

    """
        detect_cm_inline_expressions_ode

        analyzes any inline without kernels and returns

        {
            "Na":
            {
                "ASTInlineExpression": ASTInlineExpression,
                "ode_variables": [ASTVariable, ASTVariable, ASTVariable, ...], # potential ode variables

            },
            "K":
            {
                ...
            }
        }
        """

    @classmethod
    def detect_cm_inline_expressions_ode(cls, neuron):
        if not FrontendConfiguration.target_is_compartmental():
            return defaultdict()

        inline_expressions_inside_equations_block_collector_visitor = ASTInlineExpressionInsideEquationsCollectorVisitor()
        neuron.accept(
            inline_expressions_inside_equations_block_collector_visitor)
        inline_expressions_dict = inline_expressions_inside_equations_block_collector_visitor.inline_expressions_to_variables

        # filter for any inline that has no kernel
        relevant_inline_expressions_to_variables = defaultdict(lambda: list())
        for expression, variables in inline_expressions_dict.items():
            inline_expression_name = expression.variable_name
            if not inline_expressions_inside_equations_block_collector_visitor.is_synapse_inline(
                    inline_expression_name):
                relevant_inline_expressions_to_variables[expression] = variables

        # create info structure
        chan_info = defaultdict()
        for inline_expression, inner_variables in relevant_inline_expressions_to_variables.items():
            info = defaultdict()
            channel_name = cls.cm_expression_to_channel_name(inline_expression)
            info["RootInlineExpression"] = inline_expression
            #info["ode_variables"] = inner_variables
            chan_info[channel_name] = info

        return chan_info

    @classmethod
    def sort_for_actual_ode_vars_and_add_equations(cls, neuron, chan_info):
        #collect all ODEs
        ode_collector = ASTODEEquationCollectorVisitor()
        neuron.accept(ode_collector)
        odes = ode_collector.all_ode_equations

        for ion_channel_name, channel_info in chan_info.items():
            variables = channel_info["ode_variables"]
            chan_var_info = defaultdict()
            non_ode_vars = list()

            for variable_used in variables:
                variable_odes = list()

                for ode in odes:
                    if variable_used.get_name() == ode.get_lhs().get_name():
                        variable_odes.append(ode)

                if len(variable_odes) > 0:
                    info = defaultdict()
                    info["ASTVariable"] = variable_used
                    info["ASTOdeEquation"] = variable_odes[0]
                    chan_var_info[variable_used.get_name()] = info
                else:
                    non_ode_vars.append(variable_used)

            chan_info[ion_channel_name]["ode_variables"] = chan_var_info
            chan_info[ion_channel_name]["non_defined_variables"] = non_ode_vars
        return chan_info

    @classmethod
    def prepare_equations_for_ode_toolbox(cls, neuron, chan_info):
        for ion_channel_name, channel_info in chan_info.items():
            channel_odes = defaultdict()
            for ode in channel_info["ODEs"]:
                nestml_printer = NESTMLPrinter()
                ode_nestml_expression = nestml_printer.print_ode_equation(ode)
                channel_odes[ode.lhs.name] = defaultdict()
                channel_odes[ode.lhs.name]["ASTOdeEquation"] = ode
                channel_odes[ode.lhs.name]["ODENestmlExpression"] = ode_nestml_expression
            chan_info[ion_channel_name]["ODEs"] = channel_odes

        for ion_channel_name, channel_info in chan_info.items():
            for ode_variable_name, ode_info in channel_info["ODEs"].items():
                #Expression:
                odetoolbox_indict = {}
                odetoolbox_indict["dynamics"] = []
                lhs = ASTUtils.to_ode_toolbox_name(ode_info["ASTOdeEquation"].get_lhs().get_complete_name())
                rhs = cls._ode_toolbox_printer.print(ode_info["ASTOdeEquation"].get_rhs())
                entry = {"expression": lhs + " = " + rhs}

                #Initial values:
                entry["initial_values"] = {}
                symbol_order = ode_info["ASTOdeEquation"].get_lhs().get_differential_order()
                for order in range(symbol_order):
                    iv_symbol_name = ode_info["ASTOdeEquation"].get_lhs().get_name() + "'" * order
                    initial_value_expr = neuron.get_initial_value(iv_symbol_name)
                    entry["initial_values"][ASTUtils.to_ode_toolbox_name(iv_symbol_name)] = cls._ode_toolbox_printer.print(initial_value_expr)


                odetoolbox_indict["dynamics"].append(entry)
                chan_info[ion_channel_name]["ODEs"][ode_variable_name]["ode_toolbox_input"] = odetoolbox_indict

        return chan_info

    @classmethod
    def collect_raw_odetoolbox_output(cls, chan_info):
        for ion_channel_name, channel_info in chan_info.items():
            for ode_variable_name, ode_info in channel_info["ODEs"].items():
                solver_result = analysis(ode_info["ode_toolbox_input"], disable_stiffness_check=True)
                chan_info[ion_channel_name]["ODEs"][ode_variable_name]["ode_toolbox_output"] = solver_result

        return chan_info

    """
    @classmethod
    def collect_channel_functions(cls, neuron, chan_info):
        for ion_channel_name, channel_info in chan_info.items():
            functionCollector = ASTFunctionCollectorVisitor()
            neuron.accept(functionCollector)
            functions_in_inline = functionCollector.all_functions
            chan_functions = dict()

            for function in functions_in_inline:
                gsl_converter = ODEToolboxReferenceConverter()
                gsl_printer = UnitlessExpressionPrinter(gsl_converter)
                printed = gsl_printer.print_expression(function)
                chan_functions[printed] = function

            chan_info[ion_channel_name]["channel_functions"] = chan_functions

        return chan_info
    """

    @classmethod
    def extend_variable_list_name_based_restricted(cls, extended_list, appending_list, restrictor_list):
        for app_item in appending_list:
            appendable = True
            for rest_item in restrictor_list:
                if rest_item.name == app_item.name:
                    appendable = False
                    break
            if appendable:
                extended_list.append(app_item)

        return extended_list

    @classmethod
    def extend_function_call_list_name_based_restricted(cls, extended_list, appending_list, restrictor_list):
        for app_item in appending_list:
            appendable = True
            for rest_item in restrictor_list:
                if rest_item.callee_name == app_item.callee_name:
                    appendable = False
                    break
            if appendable:
                extended_list.append(app_item)

        return extended_list



    @classmethod
    def collect_channel_related_definitions(cls, neuron, chan_info):
        for ion_channel_name, channel_info in chan_info.items():
            variable_collector = ASTVariableCollectorVisitor()
            neuron.accept(variable_collector)
            global_states = variable_collector.all_states
            global_parameters = variable_collector.all_parameters

            function_collector = ASTFunctionCollectorVisitor()
            neuron.accept(function_collector)
            global_functions = function_collector.all_functions

            inline_collector = ASTInlineEquationCollectorVisitor()
            neuron.accept(inline_collector)
            global_inlines = inline_collector.all_inlines

            ode_collector = ASTODEEquationCollectorVisitor()
            neuron.accept(ode_collector)
            global_odes = ode_collector.all_ode_equations

            #print("states: "+str(len(global_states))+" param: "+str(len(global_parameters))+" funcs: "+str(len(global_functions))+" inlines: "+str(len(global_inlines))+" odes: "+str(len(global_odes)))

            channel_states = list()
            channel_parameters = list()
            channel_functions = list()
            channel_inlines = list()
            channel_odes = list()

            channel_inlines.append(chan_info[ion_channel_name]["RootInlineExpression"])

            search_variables = list()
            search_functions = list()

            found_variables = list()
            found_functions = list()

            local_variable_collector = ASTVariableCollectorVisitor()
            channel_inlines[0].accept(local_variable_collector)
            search_variables = local_variable_collector.all_variables

            local_function_call_collector = ASTFunctionCallCollectorVisitor()
            channel_inlines[0].accept(local_function_call_collector)
            search_functions = local_function_call_collector.all_function_calls

            while (len(search_functions) > 0 or len(search_variables) > 0):
                #print(str(len(search_functions))+", "+str(len(search_variables)))
                if(len(search_functions) > 0):
                    function_call = search_functions[0]
                    for function in global_functions:
                        if function.name == function_call.callee_name:
                            print("function found")
                            channel_functions.append(function)
                            found_functions.append(function_call)

                            local_variable_collector = ASTVariableCollectorVisitor()
                            function.accept(local_variable_collector)
                            #search_variables = search_variables + [item for item in list(dict.fromkeys(local_variable_collector.all_variables)) if item not in found_variables+search_variables]
                            search_variables = cls.extend_variable_list_name_based_restricted(search_variables, local_variable_collector.all_variables, search_variables+found_variables)

                            local_function_call_collector = ASTFunctionCallCollectorVisitor()
                            function.accept(local_function_call_collector)
                            #search_functions = search_functions + [item for item in list(dict.fromkeys(local_function_call_collector.all_function_calls)) if item not in found_functions+search_functions]
                            search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                              local_function_call_collector.all_function_calls,
                                                                                              search_functions + found_functions)
                            #IMPLEMENT CATCH NONDEFINED!!!
                    search_functions.remove(function_call)

                elif (len(search_variables) > 0):
                    variable = search_variables[0]
                    for inline in global_inlines:
                        if variable.name == inline.variable_name:
                            print("inline found")
                            channel_inlines.append(inline)

                            local_variable_collector = ASTVariableCollectorVisitor()
                            inline.accept(local_variable_collector)
                            search_variables = cls.extend_variable_list_name_based_restricted(search_variables, local_variable_collector.all_variables, search_variables+found_variables)

                            local_function_call_collector = ASTFunctionCallCollectorVisitor()
                            inline.accept(local_function_call_collector)
                            search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                                   local_function_call_collector.all_function_calls,
                                                                                                   search_functions + found_functions)

                    for ode in global_odes:
                        if variable.name == ode.lhs.name:
                            print("ode found")
                            channel_odes.append(ode)

                            local_variable_collector = ASTVariableCollectorVisitor()
                            ode.accept(local_variable_collector)
                            search_variables = cls.extend_variable_list_name_based_restricted(search_variables, local_variable_collector.all_variables, search_variables+found_variables)

                            local_function_call_collector = ASTFunctionCallCollectorVisitor()
                            ode.accept(local_function_call_collector)
                            search_functions = cls.extend_function_call_list_name_based_restricted(search_functions,
                                                                                                   local_function_call_collector.all_function_calls,
                                                                                                   search_functions + found_functions)

                    for state in global_states:
                        if variable.name == state.name:
                            print("state found")
                            channel_states.append(state)

                    for parameter in global_parameters:
                        if variable.name == parameter.name:
                            print("parameter found")
                            channel_parameters.append(parameter)

                    search_variables.remove(variable)
                    found_variables.append(variable)
                    # IMPLEMENT CATCH NONDEFINED!!!

            chan_info[ion_channel_name]["States"] = channel_states
            chan_info[ion_channel_name]["Parameters"] = channel_parameters
            chan_info[ion_channel_name]["Functions"] = channel_functions
            chan_info[ion_channel_name]["SecondaryInlineExpressions"] = channel_inlines
            chan_info[ion_channel_name]["ODEs"] = channel_odes

        return chan_info




    """
        analyzes cm inlines for expected odes
        input:
        {
            "Na":
            {
                "ASTInlineExpression": ASTInlineExpression,
                "ode_variables": [ASTVariable, ASTVariable, ASTVariable, ...]

            },
            "K":
            {
                ...
            }
        }

        output:
        {
            "Na":
            {
                "ASTInlineExpression": ASTInlineExpression,
                "ode_variables":
                {
                    "m":
                    {
                        "ASTVariable": ASTVariable
                        "describing_ode": ASTOdeEquation
                    },
                    "h":
                    {
                        "ASTVariable": ASTVariable
                        "describing_ode": ASTOdeEquation
                    },
                    ...
                },
            }
            "K":
            {
                ...
            }
        }

        """


#----------------------- Test function for building a chan_info prototype
    @classmethod
    def create_chan_info_ode_prototype_hh(cls, chan_info):
        ret = copy.copy(chan_info)

    @classmethod
    def print_element(cls, name, element, rec_step):
        for indent in range(rec_step):
            print("----", end="")
        print(name + ": ", end="")
        if isinstance(element, defaultdict):
            print("\n")
            cls.print_dictionary(element, rec_step + 1)
        else:
            if hasattr(element, 'name'):
                print(element.name, end="")
            elif isinstance(element, str):
                print(element, end="")
            elif isinstance(element, dict):
                print(json.dumps(element, indent=4), end="")
            elif isinstance(element, list):
                for index in range(len(element)):
                    print("\n")
                    cls.print_element(str(index), element[index], rec_step+1)

            print("(" + type(element).__name__ + ")", end="")

    @classmethod
    def print_dictionary(cls, dictionary, rec_step):
        for name, element in dictionary.items():
            cls.print_element(name, element, rec_step)
            print("\n")




#----------------------- Collector root functions

    @classmethod
    def get_chan_info(cls, neuron: ASTNeuron):
        """
        returns previously generated chan_info
        as a deep copy so it can't be changed externally
        via object references
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """

        # trigger generation via check_co_co
        # if it has not been called before
        print("GET CHAN INFO")
        if cls.first_time_run[neuron]:
            cls.check_co_co(neuron)

        return copy.deepcopy(cls.chan_info[neuron])

    @classmethod
    def check_co_co(cls, neuron: ASTNeuron):
        """
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """
        # make sure we only run this a single time
        # subsequent calls will be after AST has been transformed
        # where kernels have been removed
        # and inlines therefore can't be recognized by kernel calls any more
        if cls.first_time_run[neuron]:
            #chan_info = cls.detect_cm_inline_expressions(neuron)
            chan_info = cls.detect_cm_inline_expressions_ode(neuron)


            cls.collect_channel_related_definitions(neuron, chan_info)

            # further computation not necessary if there were no cm neurons
            if not chan_info:
                cls.chan_info[neuron] = dict()
                # mark as done so we don't enter here again
                cls.first_time_run[neuron] = False
                return True

            cls.print_dictionary(chan_info, 0)
            chan_info = cls.prepare_equations_for_ode_toolbox(neuron, chan_info)
            cls.print_dictionary(chan_info, 0)
            chan_info = cls.collect_raw_odetoolbox_output(chan_info)
            cls.print_dictionary(chan_info, 0)



            #chan_info = cls.calc_expected_function_names_for_channels(chan_info)
            #chan_info = cls.check_and_find_functions(neuron, chan_info)
            #chan_info = cls.add_channel_parameters_section_and_enforce_proper_variable_names(neuron, chan_info)

            cls.print_dictionary(chan_info, 0)

            # now check for existence of expected state variables
            # and add their ASTVariable objects to chan_info
            #missing_states_visitor = VariableMissingVisitor(chan_info)
            #neuron.accept(missing_states_visitor)

            cls.chan_info[neuron] = chan_info
            cls.first_time_run[neuron] = False

        return True


# ------------------- Helper classes
"""
    Finds the actual ASTVariables in state block
    For each expected variable extract their right hand side expression
    which contains the desired state value


    chan_info input
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "channel_parameters":
            {
                "gbar":{"expected_name": "gbar_Na"},
                "e":{"expected_name": "e_Na"}
            }
            "gating_variables":
            {
                "m":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                },
                "h":
                {
                    "ASTVariable": ASTVariable,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }

    chan_info output
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "channel_parameters":
            {
                "gbar": {
                            "expected_name": "gbar_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        },
                "e":  {
                            "expected_name": "e_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        }
            }
            "gating_variables":
            {
                "m":
                {
                    "ASTVariable": ASTVariable,
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                },
                "h":
                {
                    "ASTVariable": ASTVariable,
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction,
                                    "function_name": str,
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }

"""


class VariableMissingVisitor(ASTVisitor):

    def __init__(self, chan_info):
        super(VariableMissingVisitor, self).__init__()
        self.chan_info = chan_info

        # store ASTElement that causes the expecation of existence of state value
        # needed to generate sufficiently informative error message
        self.expected_to_object = defaultdict()

        self.values_expected_from_channel = set()
        for ion_channel_name, channel_info in self.chan_info.items():
            for channel_variable_type, channel_variable_info in channel_info["channel_parameters"].items(
            ):
                self.values_expected_from_channel.add(
                    channel_variable_info["expected_name"])
                self.expected_to_object[channel_variable_info["expected_name"]
                                        ] = channel_info["ASTInlineExpression"]

        self.values_expected_from_variables = set()
        for ion_channel_name, channel_info in self.chan_info.items():
            for pure_variable_type, variable_info in channel_info["gating_variables"].items(
            ):
                self.values_expected_from_variables.add(
                    variable_info["ASTVariable"].name)
                self.expected_to_object[variable_info["ASTVariable"]
                                        .name] = variable_info["ASTVariable"]

        self.not_yet_found_variables = set(
            self.values_expected_from_channel).union(
            self.values_expected_from_variables)

        self.inside_state_block = False
        self.inside_parameter_block = False
        self.inside_declaration = False
        self.current_block_with_variables = None
        self.current_declaration = None

    def visit_declaration(self, node):
        self.inside_declaration = True
        self.current_declaration = node

    def endvisit_declaration(self, node):
        self.inside_declaration = False
        self.current_declaration = None

    def visit_variable(self, node):
        if self.inside_state_block and self.inside_declaration:
            varname = node.name
            if varname in self.not_yet_found_variables:
                Logger.log_message(message="Expected state variable '" + varname + "' found inside state block", log_level=LoggingLevel.INFO)
                self.not_yet_found_variables.difference_update({varname})

                # make a copy because we can't write into the structure directly
                # while iterating over it
                chan_info_updated = copy.copy(self.chan_info)

                # now that we found the satate defintion, extract information
                # into chan_info

                # state variables
                if varname in self.values_expected_from_variables:
                    for ion_channel_name, channel_info in self.chan_info.items():
                        for pure_variable_name, variable_info in channel_info["gating_variables"].items(
                        ):
                            if variable_info["ASTVariable"].name == varname:
                                chan_info_updated[ion_channel_name]["gating_variables"][pure_variable_name]["state_variable"] = node
                                rhs_expression = self.current_declaration.get_expression()
                                if rhs_expression is None:
                                    code, message = Messages.get_cm_variable_value_missing(
                                        varname)
                                    Logger.log_message(
                                        code=code,
                                        message=message,
                                        error_position=node.get_source_position(),
                                        log_level=LoggingLevel.ERROR,
                                        node=node)

                                chan_info_updated[ion_channel_name]["gating_variables"][
                                    pure_variable_name]["rhs_expression"] = rhs_expression
                self.chan_info = chan_info_updated

        if self.inside_parameter_block and self.inside_declaration:
            varname = node.name
            if varname in self.not_yet_found_variables:
                Logger.log_message(message="Expected variable '" + varname + "' found inside parameter block", log_level=LoggingLevel.INFO)
                self.not_yet_found_variables.difference_update({varname})

                # make a copy because we can't write into the structure directly
                # while iterating over it
                chan_info_updated = copy.copy(self.chan_info)
                # now that we found the defintion, extract information into
                # chan_info

                # channel parameters
                if varname in self.values_expected_from_channel:
                    for ion_channel_name, channel_info in self.chan_info.items():
                        for variable_type, variable_info in channel_info["channel_parameters"].items(
                        ):
                            if variable_info["expected_name"] == varname:
                                chan_info_updated[ion_channel_name]["channel_parameters"][
                                    variable_type]["parameter_block_variable"] = node
                                rhs_expression = self.current_declaration.get_expression()
                                if rhs_expression is None:
                                    code, message = Messages.get_cm_variable_value_missing(
                                        varname)
                                    Logger.log_message(
                                        code=code,
                                        message=message,
                                        error_position=node.get_source_position(),
                                        log_level=LoggingLevel.ERROR,
                                        node=node)

                                chan_info_updated[ion_channel_name]["channel_parameters"][
                                    variable_type]["rhs_expression"] = rhs_expression
                self.chan_info = chan_info_updated

    def endvisit_neuron(self, node):
        missing_variable_to_proper_block = {}
        for variable in self.not_yet_found_variables:
            if variable in self.values_expected_from_channel:
                missing_variable_to_proper_block[variable] = "parameters block"
            elif variable in self.values_expected_from_variables:
                missing_variable_to_proper_block[variable] = "state block"

        if self.not_yet_found_variables:
            code, message = Messages.get_expected_cm_variables_missing_in_blocks(
                missing_variable_to_proper_block, self.expected_to_object)
            Logger.log_message(
                code=code,
                message=message,
                error_position=node.get_source_position(),
                log_level=LoggingLevel.ERROR,
                node=node)

    def visit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = True
        if node.is_parameters:
            self.inside_parameter_block = True
        self.current_block_with_variables = node

    def endvisit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = False
        if node.is_parameters:
            self.inside_parameter_block = False
        self.current_block_with_variables = None


"""
for each inline expression inside the equations block,
collect all ASTVariables that are present inside
"""


class ASTInlineExpressionInsideEquationsCollectorVisitor(ASTVisitor):

    def __init__(self):
        super(ASTInlineExpressionInsideEquationsCollectorVisitor, self).__init__()
        self.inline_expressions_to_variables = defaultdict(lambda: list())
        self.inline_expressions_with_kernels = set()
        self.inside_equations_block = False
        self.inside_inline_expression = False
        self.inside_kernel_call = False
        self.inside_simple_expression = False
        self.current_inline_expression = None

    def is_synapse_inline(self, inline_name):
        return inline_name in self.inline_expressions_with_kernels

    def visit_variable(self, node):
        if self.inside_equations_block and self.inside_inline_expression and self.current_inline_expression is not None:
            self.inline_expressions_to_variables[self.current_inline_expression].append(
                node)

    def visit_inline_expression(self, node):
        self.inside_inline_expression = True
        self.current_inline_expression = node

    def endvisit_inline_expression(self, node):
        self.inside_inline_expression = False
        self.current_inline_expression = None

    def visit_equations_block(self, node):
        self.inside_equations_block = True

    def endvisit_equations_block(self, node):
        self.inside_equations_block = False

    def visit_function_call(self, node):
        if self.inside_equations_block:
            if self.inside_inline_expression and self.inside_simple_expression:
                if node.get_name() == "convolve":
                    inline_name = self.current_inline_expression.variable_name
                    self.inline_expressions_with_kernels.add(inline_name)

    def visit_simple_expression(self, node):
        self.inside_simple_expression = True

    def endvisit_simple_expression(self, node):
        self.inside_simple_expression = False

#----------------- New ode helpers
class ASTODEEquationCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTODEEquationCollectorVisitor, self).__init__()
        self.inside_ode_expression = False
        self.all_ode_equations = list()

    def visit_ode_equation(self, node):
        self.inside_ode_expression = True
        self.all_ode_equations.append(node.clone())

    def endvisit_ode_equation(self, node):
        self.inside_ode_expression = False

class ASTVariableCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTVariableCollectorVisitor, self).__init__()
        self.inside_variable = False
        self.inside_block_with_variables = False
        self.all_states = list()
        self.all_parameters = list()
        self.inside_states_block = False
        self.inside_parameters_block = False
        self.all_variables = list()

    def visit_block_with_variables(self, node):
        self.inside_block_with_variables = True
        if node.is_state:
            self.inside_states_block = True
        if node.is_parameters:
            self.inside_parameters_block = True

    def endvisit_block_with_variables(self, node):
        self.inside_states_block = False
        self.inside_parameters_block = False
        self.inside_block_with_variables = False

    def visit_variable(self, node):
        self.inside_variable = True
        self.all_variables.append(node.clone())
        if self.inside_states_block:
            self.all_states.append(node.clone())
        if self.inside_parameters_block:
            self.all_parameters.append(node.clone())

    def endvisit_variable(self, node):
        self.inside_variable = False

class ASTFunctionCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTFunctionCollectorVisitor, self).__init__()
        self.inside_function = False
        self.all_functions = list()

    def visit_function(self, node):
        self.inside_function = True
        self.all_functions.append(node.clone())

    def endvisit_function(self, node):
        self.inside_function = False

class ASTInlineEquationCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTInlineEquationCollectorVisitor, self).__init__()
        self.inside_inline_expression = False
        self.all_inlines = list()

    def visit_inline_expression(self, node):
        self.inside_inline_expression = True
        self.all_inlines.append(node.clone())

    def endvisit_inline_expression(self, node):
        self.inside_inline_expression = False

class ASTFunctionCallCollectorVisitor(ASTVisitor):
    def __init__(self):
        super(ASTFunctionCallCollectorVisitor, self).__init__()
        self.inside_function_call = False
        self.all_function_calls = list()

    def visit_function_call(self, node):
        self.inside_function_call = True
        self.all_function_calls.append(node.clone())

    def endvisit_function_call(self, node):
        self.inside_function_call = False