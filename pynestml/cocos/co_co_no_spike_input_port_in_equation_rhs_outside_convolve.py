# -*- coding: utf-8 -*-
#
# co_co_no_spike_input_port_in_equation_rhs_outside_convolve.py
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
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoNoSpikeInputPortInEquationRhsOutsideConvolve(CoCo):
    """
    This coco checks that no spiking input port appears on the right-hand side of equations, outside a convolve() call.

    For instance, provided:

    .. code:: nestml

       input:
           spikes_in_port <- spikes

    The following is allowed:

    .. code:: nestml

       equations:
           kernel K = delta(t)
           x' = convolve(K, spikes_in_port) / s

    But the following is not:

    .. code:: nestml

       equations:
           x' = spikes_in_port

    """

    @classmethod
    def check_co_co(cls, model):
        """
        Ensures the coco for the handed over model.
        :param model: a single model instance.
        """
        model.accept(NoSpikeInputPortInEquationRhsOutsideConvolveVisitor())


class NoSpikeInputPortInEquationRhsOutsideConvolveVisitor(ASTVisitor):
    def visit_variable(self, node: ASTVariable):
        model = ASTUtils.find_parent_node_by_type(node, ASTModel)
        assert model is not None
        inport = ASTUtils.get_input_port_by_name(model.get_input_blocks(), node.get_name())
        if inport and inport.is_spike():
            if ASTUtils.find_parent_node_by_type(node, ASTEquationsBlock):
                func_call = ASTUtils.find_parent_node_by_type(node, ASTFunctionCall)
                if func_call and func_call.callee_name == PredefinedFunctions.CONVOLVE:
                    # it appears inside a convolve() call -- everything is fine!
                    return

                # it's an input port inside the equations block, but not inside a convolve() call -- error
                code, message = Messages.get_spike_input_port_in_equation_rhs_outside_convolve()
                Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR, node=node)
                return
