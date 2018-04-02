#
# CoCoShapeVarInCorrectExpression.py
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
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class CoCoConvolveCondCorrectlyBuilt(CoCo):
    """
    This coco ensures that convolve and cond/curr sum are correctly build, i.e.,
    that the first argument is the variable from the initial block and the second argument an input buffer.
    Allowed:
        function I_syn_exc pA =   convolve(g_ex, spikesExc) * ( V_bounded - E_ex )
    Not allowed:
        function I_syn_exc pA =   convolve(g_ex, g_ex) * ( V_bounded - E_ex )

    """

    @classmethod
    def check_co_co(cls, node):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.CorrectNumerator) No or wrong type of neuron provided (%s)!' % type(node)
        node.accept(ConvolveCheckerVisitor())
        return


class ConvolveCheckerVisitor(ASTVisitor):
    """
    Visits a function call and checks that if the function call is a cond_sum,cur_sum or convolve, the parameters
    are correct.
    """

    def visit_function_call(self, node):
        func_name = node.get_name()
        if func_name == 'convolve' or func_name == 'cond_sum' or func_name == 'curr_sum':
            symbol_var = node.get_scope().resolveToSymbol(str(node.get_args()[0]),
                                                          SymbolKind.VARIABLE)
            symbol_buffer = node.get_scope().resolveToSymbol(str(node.get_args()[1]),
                                                             SymbolKind.VARIABLE)
            if symbol_var is not None and not symbol_var.is_shape() and not symbol_var.is_init_values():
                code, message = Messages.getFirstArgNotShapeOrEquation(func_name)
                Logger.logMessage(_code=code, _message=message,
                                  _errorPosition=node.get_source_position(), _logLevel=LOGGING_LEVEL.ERROR)
            if symbol_buffer is not None and not symbol_buffer.is_input_buffer_spike():
                code, message = Messages.getSecondArgNotABuffer(func_name)
                Logger.logMessage(_errorPosition=node.get_source_position(),
                                  _code=code, _message=message,
                                  _logLevel=LOGGING_LEVEL.ERROR)
            return
