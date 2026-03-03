# -*- coding: utf-8 -*-
#
# spinnaker_gsl_function_call_printer.py
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

from pynestml.codegeneration.printers.spinnaker_c_function_call_printer import SpinnakerCFunctionCallPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbols.predefined_functions import PredefinedFunctions


class SpinnakerGSLFunctionCallPrinter(SpinnakerCFunctionCallPrinter):
    r"""
    This class is used to convert function calls to the GSL (GNU Scientific Library) syntax.
    """

    def _print_function_call_format_string(self, function_call: ASTFunctionCall) -> str:
        r"""Convert a single function call to C GSL API syntax.

        Parameters
        ----------
        function_call : ASTFunctionCall
            The function call node to convert.

        Returns
        -------
        s : str
            The function call string in C syntax.
        """

        function_name = function_call.get_name()

        function_is_predefined = bool(PredefinedFunctions.get_function(function_name))
        if function_is_predefined:
            return super()._print_function_call_format_string(function_call)

        return "node." + super()._print_function_call_format_string(function_call)
