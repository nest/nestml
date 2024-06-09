# -*- coding: utf-8 -*-
#
# nest_gpu_function_call_printer.py
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

from pynestml.codegeneration.printers.cuda_function_call_printer import CUDAFunctionCallPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.symbols.predefined_functions import PredefinedFunctions


class NESTGPUFunctionCallPrinter(CUDAFunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall for NEST-GPU target
    """

    def _print_function_call_format_string(self, function_call: ASTFunctionCall) -> str:
        """
        Converts a single handed over function call to CUDA NEST-GPU API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.

        Returns
        -------
        s
            The function call string in NEST-GPU target syntax.
        """
        function_name = function_call.get_name()

        if function_name == PredefinedFunctions.TIME_RESOLUTION:
            # context dependent; we assume the template contains the necessary definitions
            return 'NESTGPUTimeResolution'

        if function_name == PredefinedFunctions.TIME_STEPS:
            return '(int)round({!s}/NESTGPUTimeResolution)'

        # TODO:
        # if function_name == PredefinedFunctions.RANDOM_NORMAL:
        #     return '(({!s}) + ({!s}) * ' + 'normal_dev_( nest::get_vp_specific_rng( ' + 'get_thread() ) ))'
        #
        # if function_name == PredefinedFunctions.RANDOM_UNIFORM:
        #     return '(({!s}) + ({!s}) * nest::get_vp_specific_rng( ' + 'get_thread() )->drand())'

        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'PushSpike(i_node_0 + i_neuron, 1.0);'

        return super()._print_function_call_format_string(function_call)
