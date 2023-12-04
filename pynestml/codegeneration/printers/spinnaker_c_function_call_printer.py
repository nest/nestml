# -*- coding: utf-8 -*-
#
# spinnaker_c_function_call_printer.py
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

from pynestml.codegeneration.printers.function_call_printer import FunctionCallPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils


class SpinnakerCFunctionCallPrinter(FunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in C Spinnaker API  syntax.
    """

    def print_function_call(self, node: ASTFunctionCall) -> str:
        r"""
        Converts a single handed over function call to C Spinnaker API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in C syntax.
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
            return 'neuron_recording_record_bit(SPIKE_RECORDING_BITFIELD, neuron_index);\n' \
                   'send_spike(timer_count, time, neuron_index)'

        if function_name == PredefinedFunctions.DELIVER_SPIKE:
            return "// Probably dont need to actively deliver spike"

        return super().print_function_call(node)

    def _print_function_call_format_string(self, function_call: ASTFunctionCall) -> str:
        r"""
        Converts a single handed over function call to C Spinnaker API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in C syntax.
        """
        function_name = function_call.get_name()

        if function_name == PredefinedFunctions.CLIP:
            # the arguments of this function must be swapped and are therefore [v_max, v_min, v]
            return 'MIN({2!s}, MAX({1!s}, {0!s}))'

        if function_name == PredefinedFunctions.MAX:
            return 'MAX({!s}, {!s})'

        if function_name == PredefinedFunctions.MIN:
            return 'MIN({!s}, {!s})'

        if function_name == PredefinedFunctions.EXP:
            return 'expk({!s})'

        if function_name == PredefinedFunctions.LN:
            return 'logk({!s})'

        if function_name == PredefinedFunctions.POW:
            return '(expk({1!s} * logk({0!s})))'

        if function_name == PredefinedFunctions.LOG10:
            return '(kdivk(logk({!s}), REAL_CONST(2.303)))'

        if function_name == PredefinedFunctions.COSH:
            return '(HALF * (expk({!s}) + expk(-{!s})))'

        if function_name == PredefinedFunctions.SINH:
            return '(HALF * (expk({!s}) - expk(-{!s})))'

        if function_name == PredefinedFunctions.TANH:
            return 'kdik((expk({!s}) - expk(-{!s})), (expk({!s}) + expk(-{!s})))'

        if function_name == PredefinedFunctions.ERF:
            raise Exception("Erf not defined for spinnaker")

        if function_name == PredefinedFunctions.ERFC:
            raise Exception("Erfc not defined for spinnaker")

        if function_name == PredefinedFunctions.EXPM1:
            raise Exception("Expm1 not defined for spinnaker")

        if function_name == PredefinedFunctions.PRINT:
            return 'printf("%s", {!s})'

        if function_name == PredefinedFunctions.PRINTLN:
            return 'printf("%s\n",{!s})'

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return function_name + '(' + ', '.join(['{!s}' for _ in range(n_args)]) + ')'

        return function_name + '()'
