# -*- coding: utf-8 -*-
#
# co_co_convolve_cond_correctly_built.py
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
from pynestml.cocos.co_co import CoCo
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoConvolveCondCorrectlyBuilt(CoCo):
    """
    This coco ensures that ``convolve`` is correctly called, i.e. that the first argument is the variable from the initial block and the second argument is an input buffer.

    Allowed:
        inline I_syn_exc pA = convolve(g_ex, spikesExc) * ( V_m - E_ex )

    Not allowed:
        inline I_syn_exc pA = convolve(g_ex, g_ex) * ( V_m - E_ex )
        inline I_syn_exc pA = convolve(spikesExc, g_ex) * ( V_m - E_ex )
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        node.accept(ConvolveCheckerVisitor())


class ConvolveCheckerVisitor(ASTVisitor):
    """
    Visits a function call and checks that if the function call is a convolve, the parameters are correct.
    """

    def visit_function_call(self, node):
        func_name = node.get_name()
        if func_name == 'convolve':
            symbol_var = node.get_scope().resolve_to_symbol(str(node.get_args()[0]),
                                                            SymbolKind.VARIABLE)
            symbol_buffer = node.get_scope().resolve_to_symbol(str(node.get_args()[1]),
                                                               SymbolKind.VARIABLE)
            if symbol_var is not None and not symbol_var.is_kernel() and not symbol_var.is_init_values():
                code, message = Messages.get_first_arg_not_kernel_or_equation(func_name)
                Logger.log_message(code=code, message=message,
                                   error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)
            if symbol_buffer is not None and not symbol_buffer.is_input_buffer_spike():
                code, message = Messages.get_second_arg_not_a_buffer(func_name)
                Logger.log_message(error_position=node.get_source_position(),
                                   code=code, message=message,
                                   log_level=LoggingLevel.ERROR)
            return
