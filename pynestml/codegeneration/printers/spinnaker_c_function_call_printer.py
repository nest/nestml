# -*- coding: utf-8 -*-
#
# spinnaker_cpp_function_call_printer.py
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

from typing import Tuple

from pynestml.codegeneration.printers.cpp_function_call_printer import CppFunctionCallPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils

class SpinnakerCFunctionCallPrinter(CppFunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in LaTeX syntax.
    """

    def print_function_call(self, node: ASTFunctionCall) -> str:
        r"""
        Converts a single handed over function call to C++ NEST API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in C++ syntax.
        """
        function_name = node.get_name()

        if function_name == PredefinedFunctions.TIME_RESOLUTION:
            # context dependent; we assume the template contains the necessary definitions
            return 'neuron->this_h'

        if function_name == PredefinedFunctions.TIME_STEPS:
            raise Exception("time_steps() function not yet implemented")

        if function_name == PredefinedFunctions.RANDOM_NORMAL:
            raise Exception("rng functions not yet implemented")

        if function_name == PredefinedFunctions.RANDOM_UNIFORM:
            raise Exception("rng functions not yet implemented")

        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'send_spike(timer_count, time, neuron_index)'

        if function_name == PredefinedFunctions.DELIVER_SPIKE:
            raise Exception("deliver_spike() function not yet implemented")

        return super().print_function_call(node)

    def _print_function_call_format_string(self, function_call: ASTFunctionCall) -> str:
        r"""
        Converts a single handed over function call to C++ NEST API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in C++ syntax.
        """
        function_name = function_call.get_name()

        if function_name == PredefinedFunctions.CLIP:
            # the arguments of this function must be swapped and are therefore [v_max, v_min, v]
            return 'min({2!s}, std::max({1!s}, {0!s}))'

        if function_name == PredefinedFunctions.MAX:
            return 'max({!s}, {!s})'

        if function_name == PredefinedFunctions.MIN:
            return 'min({!s}, {!s})'

        if function_name == PredefinedFunctions.EXP:
            return 'exp({!s})'

        if function_name == PredefinedFunctions.LN:
            return 'log({!s})'

        if function_name == PredefinedFunctions.LOG10:
            return 'log10({!s})'

        if function_name == PredefinedFunctions.COSH:
            return 'cosh({!s})'

        if function_name == PredefinedFunctions.SINH:
            return 'sinh({!s})'

        if function_name == PredefinedFunctions.TANH:
            return 'tanh({!s})'

        if function_name == PredefinedFunctions.ERF:
            return 'erf({!s})'

        if function_name == PredefinedFunctions.ERFC:
            return 'erfc({!s})'

        if function_name == PredefinedFunctions.EXPM1:
            return 'expm1({!s})'

        if function_name == PredefinedFunctions.PRINT:
            return 'printf({!s})'

        if function_name == PredefinedFunctions.PRINTLN:
            return 'printf({!s}+"\n")'

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return function_name + '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'

        return function_name + '()'
