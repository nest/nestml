# -*- coding: utf-8 -*-
#
# concentration_processing.py
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
from collections import defaultdict

import sympy
import re


class ConcentrationProcessing(MechanismProcessing):
    """The default Processing ignores the root expression when solving the odes which in case of the concentration
    mechanism is a ode that needs to be solved. This is added here."""
    mechType = "concentration"

    def __init__(self, params):
        super(MechanismProcessing, self).__init__(params)

    @classmethod
    def collect_information_for_specific_mech_types(cls, neuron, mechs_info):
        mechs_info = cls.ode_toolbox_processing_for_root_expression(neuron, mechs_info)
        mechs_info = cls.write_key_zero_parameters_for_root_odes(mechs_info)

        return mechs_info

    @classmethod
    def ode_toolbox_processing_for_root_expression(cls, neuron, conc_info):
        """applies the ode_toolbox_processing to the root_expression since that was never appended to the list of ODEs
        in the base processing and thereby also never went through the ode_toolbox processing"""
        for concentration_name, concentration_info in conc_info.items():
            # Create fake mechs_info such that it can be processed by the existing ode_toolbox_processing function.
            fake_conc_info = defaultdict()
            fake_concentration_info = defaultdict()
            fake_concentration_info["ODEs"] = list()
            fake_concentration_info["ODEs"].append(concentration_info["root_expression"])
            fake_conc_info["fake"] = fake_concentration_info

            fake_conc_info = cls.ode_toolbox_processing(neuron, fake_conc_info)

            conc_info[concentration_name]["ODEs"] = {**conc_info[concentration_name]["ODEs"], **fake_conc_info["fake"][
                "ODEs"]}

        return conc_info

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
        key_zero_parameters = list()
        for parameter_name, parameter_info in parameters.items():
            if cls.check_if_key_zero_var_for_expression(rhs_expression_str, parameter_name):
                key_zero_parameters.append(parameter_name)

        return key_zero_parameters

    @classmethod
    def write_key_zero_parameters_for_root_odes(cls, conc_info):
        for concentration_name, concentration_info in conc_info.items():
            root_inline_rhs = cls._ode_toolbox_printer.print(concentration_info["root_expression"].get_rhs())
            conc_info[concentration_name]["RootOdeKeyZeros"] = cls.search_for_key_zero_parameters_for_expression(
                root_inline_rhs, concentration_info["Parameters"])

        return conc_info
