from collections import defaultdict
import copy

from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages

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
    syns_info = defaultdict()

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
    def detectMechs(cls, neuron):

        # search for synapse_inline expressions inside equations block
        # but do not traverse yet because tests run this as well
        info_collector = ASTMechanismInformationCollector()

        mech_info = defaultdict()
        if not FrontendConfiguration.target_is_compartmental():
            return mech_info, info_collector

        # tests will arrive here if we actually have compartmental model
        neuron.accept(info_collector)

        mechanism_inlines = info_collector.get_mech_inline_expressions()
        for mechanism_inline in mechanism_inlines:
            mechanism_name = mechanism_inline.variable_name
            mech_info[mechanism_name] = defaultdict()
            mech_info[mechanism_name]["root_inline_expression"] = mechanism_inline

        mech_info = info_collector.collect_mechanism_related_definitions(neuron, mech_info)

        return syns_info, info_collector