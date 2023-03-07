from collections import defaultdict
import copy

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.ast_mechanism_information_collector import ASTMechanismInformationCollector

from pynestml.utils.ast_utils import ASTUtils
from pynestml.codegeneration.printers.nestml_printer import NESTMLPrinter

from pynestml.codegeneration.printers.constant_printer import ConstantPrinter
from pynestml.codegeneration.printers.ode_toolbox_expression_printer import ODEToolboxExpressionPrinter
from pynestml.codegeneration.printers.ode_toolbox_function_call_printer import ODEToolboxFunctionCallPrinter
from pynestml.codegeneration.printers.ode_toolbox_variable_printer import ODEToolboxVariablePrinter
from pynestml.codegeneration.printers.unitless_cpp_simple_expression_printer import UnitlessCppSimpleExpressionPrinter
from odetoolbox import analysis
import json

class MechanismProcessing(object):
    # used to keep track of whenever check_co_co was already called
    # see inside check_co_co
    first_time_run = defaultdict(lambda: True)
    # stores syns_info from the first call of check_co_co
    mechs_info = defaultdict()

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

    @classmethod
    def ode_toolbox_processing(cls, neuron, mechs_info):
        chan_info = cls.prepare_equations_for_ode_toolbox(neuron, mechs_info)
        chan_info = cls.collect_raw_odetoolbox_output(mechs_info)
        return chan_info

    @classmethod
    def collect_information_for_specific_mech_types(cls, neuron, mechs_info):
        """to be implemented for specific mechanisms (concentration, synapse, channel)"""
        return mechs_info

    @classmethod
    def get_mechs_info(cls, neuron: ASTNeuron, mechType: str):
        """
        returns previously generated mechs_info
        as a deep copy so it can't be changed externally
        via object references
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """

        return copy.deepcopy(cls.mechs_info[neuron][mechType])



    @classmethod
    def check_co_co(cls, neuron: ASTNeuron, mechType: str):
        """
        Checks if mechanism conditions apply for the handed over neuron.
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """

        # make sure we only run this a single time
        # subsequent calls will be after AST has been transformed
        # and there would be no kernels or inlines any more
        if cls.first_time_run[neuron]:
            #collect root expressions and initialize collector
            info_collector = ASTMechanismInformationCollector(neuron)
            mechs_info = info_collector.detect_mechs(mechType)

            #collect and process all basic mechanism information
            mechs_info = info_collector.collect_mechanism_related_definitions(mechs_info)
            mechs_info = info_collector.extend_variables_with_initialisations(mechs_info)
            mechs_info = cls.ode_toolbox_processing(neuron, mechs_info)

            #collect and process all mechanism type specific information
            mechs_info = cls.collect_information_for_specific_mech_types(neuron, mechs_info)

            cls.mechs_info[neuron] = mechs_info
            cls.first_time_run[neuron][mechType] = False