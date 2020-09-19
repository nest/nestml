# -*- coding: utf-8 -*-
#
# co_co_sum_has_correct_parameter.py
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
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.cocos.co_co import CoCo
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoSumHasCorrectParameter(CoCo):
    """
    This coco ensures that convolve gets only simple variable references as inputs.

    Not allowed:

    .. code-block::

        V mV = convolve(g_in + g_ex, spikes_in)

    """

    @classmethod
    def check_co_co(cls, neuron):
        """
        Ensures the coco for the handed over neuron.
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """
        cls.neuronName = neuron.get_name()
        visitor = ConvolveParametersCorrectVisitor()
        neuron.accept(visitor)


class ConvolveParametersCorrectVisitor(ASTVisitor):
    def visit_function_call(self, node):
        """
        Checks the coco on the current function call.
        :param node: a single function call.
        :type node: ASTFunctionCall
        """
        f_name = node.get_name()
        if f_name == PredefinedFunctions.CONVOLVE:
            for arg in node.get_args():
                if not isinstance(arg, ASTSimpleExpression) or not arg.is_variable():
                    code, message = Messages.get_not_a_variable(str(arg))
                    Logger.log_message(code=code, message=message,
                                       error_position=arg.get_source_position(), log_level=LoggingLevel.ERROR)
