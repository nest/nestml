# -*- coding: utf-8 -*-
#
# cpp_expression_printer.py
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

from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils


class GSLSimpleExpressionPrinter(CppSimpleExpressionPrinter):
    r"""
    Printer for ``ASTExpression`` nodes in C++ syntax in the GSL stepping function.
    """

    def print(self, node: ASTNode, prefix: str = "") -> str:
        if isinstance(node, ASTExpression):
            return self._print(node, prefix)

        if isinstance(node, ASTSimpleExpression):
            return self.cpp_simple_expression_printer.print(node, prefix)

        raise RuntimeError("Tried to print unknown expression: \"%s\"" % str(node))


    def print_function_call(self, function_call: ASTFunctionCall, prefix: str = '') -> str:
        """Convert a single function call to C++ GSL API syntax.

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
            return "__resolution"

        if function_name == PredefinedFunctions.TIME_STEPS:
            return "nest::Time(nest::Time::ms((double) {!s})).get_steps()"

        if function_name == PredefinedFunctions.RANDOM_NORMAL:
            return "(({!s}) + ({!s}) * " + prefix + "normal_dev_( nest::get_vp_specific_rng( " + prefix + "get_thread() ) ))"

        if function_name == PredefinedFunctions.RANDOM_UNIFORM:
            return "(({!s}) + ({!s}) * nest::get_vp_specific_rng( " + prefix + "get_thread() )->drand())"

        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return "set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n" \
                   "nest::SpikeEvent se;\n" \
                   "nest::kernel().event_delivery_manager.send(*this, se, lag)"

        if function_name == PredefinedFunctions.DELIVER_SPIKE:
            return '''set_delay( {1!s} );
const long __delay_steps = nest::Time::delay_ms_to_steps( get_delay() );
set_delay_steps(__delay_steps);
e.set_receiver( *__target );
e.set_weight( {0!s} );
// use accessor functions (inherited from Connection< >) to obtain delay in steps and rport
e.set_delay_steps( get_delay_steps() );
e.set_rport( get_rport() );
e();'''

        # suppress prefix for misc. predefined functions
        # check if function is "predefined" purely based on the name, as we don't have access to the function symbol here
        function_is_predefined = PredefinedFunctions.get_function(function_name)
        if function_is_predefined:
            prefix = ''

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            return prefix + function_name + "(" + ", ".join(["{!s}" for _ in range(n_args)]) + ")"

        return prefix + function_name + "()"
