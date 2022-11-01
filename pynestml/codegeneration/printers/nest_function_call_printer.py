# -*- coding: utf-8 -*-
#
# cpp_simple_expression_printer.py
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

from typing import Optional, Tuple

import re

from pynestml.codegeneration.printers.cpp_function_call_printer import CppFunctionCallPrinter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbol_table.scope import Scope
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable


class NESTFunctionCallPrinter(CppFunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in C++ syntax.
    """

    def print(self, node: ASTNode, prefix: str = "") -> str:
        assert isinstance(node, ASTFunctionCall)
        return self.print_function_call(node, prefix=prefix)

    def print_function_call(self, function_call: ASTFunctionCall, prefix: str = '') -> str:
        """
        Converts a single handed over function call to C++ NEST API syntax.

        Parameters
        ----------
        function_call
            The function call node to convert.
        prefix
            Optional string that will be prefixed to the function call. For example, to refer to a function call in the class "node", use a prefix equal to "node." or "node->".

            Predefined functions will not be prefixed.

        Returns
        -------
        s
            The function call string in C++ syntax.
        """
        function_name = function_call.get_name()

        if function_name == PredefinedFunctions.TIME_RESOLUTION:
            # context dependent; we assume the template contains the necessary definitions
            return '__resolution'

        if function_name == PredefinedFunctions.TIME_STEPS:
            return 'nest::Time(nest::Time::ms((double) ({!s}))).get_steps()'

        if function_name == PredefinedFunctions.RANDOM_NORMAL:
            return '(({!s}) + ({!s}) * ' + prefix + 'normal_dev_( nest::get_vp_specific_rng( ' + prefix + 'get_thread() ) ))'

        if function_name == PredefinedFunctions.RANDOM_UNIFORM:
            return '(({!s}) + ({!s}) * nest::get_vp_specific_rng( ' + prefix + 'get_thread() )->drand())'

        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'

        if function_name == PredefinedFunctions.DELIVER_SPIKE:
            return '''
        set_delay( {1!s} );
        const long __delay_steps = nest::Time::delay_ms_to_steps( get_delay() );
        set_delay_steps(__delay_steps);
        e.set_receiver( *__target );
  e.set_weight( {0!s} );
  // use accessor functions (inherited from Connection< >) to obtain delay in steps and rport
  e.set_delay_steps( get_delay_steps() );
  e.set_rport( get_rport() );
e();
'''

        return super().print_function_call(function_call, prefix=prefix)
