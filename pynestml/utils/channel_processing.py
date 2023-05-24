from pynestml.utils.mechanism_processing import MechanismProcessing
from collections import defaultdict
import sympy

from pynestml.meta_model.ast_neuron import ASTNeuron

class ChannelProcessing(MechanismProcessing):
    """Extends MechanismProcessing. Searches for Variables that if 0 lead to the root expression always beeing zero so
    that the computation can be skipped during the simulation"""

    mechType = "channel"

    def __init__(self, params):
        super(MechanismProcessing, self).__init__(params)

    @classmethod
    def collect_information_for_specific_mech_types(cls, neuron, mechs_info):
        """
        Searching for parameters in the root-expression that if zero lead to the expression always being zero so that
        the computation may be skipped.
        """
        mechs_info = cls.write_key_zero_parameters_for_root_inlines(mechs_info)

        return mechs_info

    @classmethod
    def check_if_key_zero_var_for_expression(cls, rhs_expression_str, var_str):
        sympy_expression = sympy.parsing.sympy_parser.parse_expr(rhs_expression_str, evaluate=False)
        if isinstance(sympy_expression, sympy.core.add.Add) and \
                cls.check_if_key_zero_var_for_expression(str(sympy_expression.args[0]), var_str) and \
                cls.check_if_key_zero_var_for_expression(str(sympy_expression.args[1]), var_str):
            return True
        elif isinstance(sympy_expression, sympy.core.mul.Mul) and \
                (cls.check_if_key_zero_var_for_expression(str(sympy_expression.args[0]), var_str) or \
                cls.check_if_key_zero_var_for_expression(str(sympy_expression.args[1]), var_str)):
            return True
        elif rhs_expression_str == var_str:
            return True
        else:
            return False

    @classmethod
    def search_for_key_zero_parameters_for_expression(cls, rhs_expression_str, parameters):
        key_zero_parameters = list()
        for parameter_name, parameter_info in parameters.items():
            if cls.check_if_key_zero_var_for_expression(rhs_expression_str, parameter_name):
                key_zero_parameters.append(parameter_name)

        return key_zero_parameters

    @classmethod
    def write_key_zero_parameters_for_root_inlines(cls, chan_info):
        for channel_name, channel_info in chan_info.items():
            root_inline_rhs = cls._ode_toolbox_printer.print(channel_info["root_expression"].get_expression())
            chan_info[channel_name]["RootInlineKeyZeros"] = cls.search_for_key_zero_parameters_for_expression(root_inline_rhs, channel_info["Parameters"])

        return chan_info