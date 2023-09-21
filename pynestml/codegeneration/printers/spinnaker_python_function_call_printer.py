# -*- coding: utf-8 -*-
#
# spinnaker_python_function_call_printer.py
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

import re

from pynestml.codegeneration.printers.python_function_call_printer import PythonFunctionCallPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbol_table.scope import Scope
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable


class SpinnakerPythonFunctionCallPrinter(PythonFunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in Python syntax.
    """

    def _print_function_call_format_string(self, function_call: ASTFunctionCall) -> str:
        """
        Converts a single handed over function call to Python syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in Python syntax.
        """
        if function_call.get_name() == PredefinedFunctions.TIME_STEPS:
            return " SpynnakerDataView.get_simulation_time_step_per_ms() * {!s}"

        if function_call.get_name() == PredefinedFunctions.TIME_RESOLUTION:
            return "timestep"

        if function_call.get_name() == PredefinedFunctions.EMIT_SPIKE:
            return "send_spike(time, timer_count, neuron_index)"

        s = function_call.get_name()

        s += "("
        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            s += ", ".join(["{!s}" for _ in range(n_args)])

        s += ")"

        return s
