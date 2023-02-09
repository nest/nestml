# -*- coding: utf-8 -*-
#
# spinnaker_function_call_printer.py
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


class SpinnakerCppFunctionCallPrinter(CppFunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in LaTeX syntax.
    """

    def _print_function_call(self, node: ASTFunctionCall) -> str:
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

        return super()._print_function_call(node)
