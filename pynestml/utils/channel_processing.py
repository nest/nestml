# -*- coding: utf-8 -*-
#
# channel_processing.py
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

import sympy
import re


class ChannelProcessing(MechanismProcessing):
    """Extends MechanismProcessing. Searches for Variables that if 0 lead to the root expression always beeing zero so
    that the computation can be skipped during the simulation"""

    mechType = "channel"

    def __init__(self, params):
        super(MechanismProcessing, self).__init__(params)

    @classmethod
    def collect_information_for_specific_mech_types(cls, neuron, mechs_info):
        mechs_info = cls.write_key_zero_parameters_for_root_inlines(mechs_info)

        return mechs_info

    @classmethod
    def check_if_key_zero_var_for_expression(cls, rhs_expression_str, var_str):
        """
        check if var being zero leads to the expression always being zero so that
        the computation may be skipped if this is determined to be the case during simulation.
        """
        if not re.search("1/.*", rhs_expression_str):
            sympy_expression = sympy.parsing.sympy_parser.parse_expr(rhs_expression_str, evaluate=False)
            if isinstance(sympy_expression, sympy.core.add.Add) \
                    and cls.check_if_key_zero_var_for_expression(str(sympy_expression.args[0]), var_str) \
                    and cls.check_if_key_zero_var_for_expression(str(sympy_expression.args[1]), var_str):
                return True

            if isinstance(sympy_expression, sympy.core.mul.Mul) \
                    and (cls.check_if_key_zero_var_for_expression(str(sympy_expression.args[0]), var_str)
                         or cls.check_if_key_zero_var_for_expression(str(sympy_expression.args[1]), var_str)):
                return True

            if rhs_expression_str == var_str:
                return True

            return False

        return False

    @classmethod
    def search_for_key_zero_parameters_for_expression(cls, rhs_expression_str, parameters):
        """
        Searching for parameters in the root-expression that if zero lead to the expression always being zero so that
        the computation may be skipped.
        """
        key_zero_parameters = list()
        for parameter_name, parameter_info in parameters.items():
            if cls.check_if_key_zero_var_for_expression(rhs_expression_str, parameter_name):
                key_zero_parameters.append(parameter_name)

        return key_zero_parameters

    @classmethod
    def write_key_zero_parameters_for_root_inlines(cls, chan_info):
        for channel_name, channel_info in chan_info.items():
            root_inline_rhs = cls._ode_toolbox_printer.print(channel_info["root_expression"].get_expression())
            chan_info[channel_name]["RootInlineKeyZeros"] = cls.search_for_key_zero_parameters_for_expression(
                root_inline_rhs, channel_info["Parameters"])

        return chan_info
