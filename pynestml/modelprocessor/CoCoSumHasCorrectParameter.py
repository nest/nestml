#
# CoCoSumHasCorrectParameter.py
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
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class CoCoSumHasCorrectParameter(CoCo):
    """
    This coco ensures that cur_sum,cond_sum and convolve get only simple variable references as inputs.
    Not allowed:
     V mV = convolve(g_in+g_ex,Buffer)
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.neuronName = _neuron.get_name()
        visitor = SumIsCorrectVisitor()
        _neuron.accept(visitor)
        return


class SumIsCorrectVisitor(ASTVisitor):
    """
    This visitor ensures that sums/convolve are provided with a correct rhs.
    """

    def visit_function_call(self, node=None):
        """
        Checks the coco on the current function call.
        :param node: a single function call.
        :type node: ASTFunctionCall
        """
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
        from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
        assert (node is not None and isinstance(node, ASTFunctionCall)), \
            '(PyNestML.CoCo.SumHasCorrectParameter) No or wrong type of function call provided (%s)!' % type(
                node)
        fName = node.get_name()
        if fName == PredefinedFunctions.CURR_SUM or fName == PredefinedFunctions.COND_SUM or \
                        fName == PredefinedFunctions.CONVOLVE:
            for arg in node.get_args():
                if not isinstance(arg, ASTSimpleExpression) or not arg.is_variable():
                    code, message = Messages.getNotAVariable(str(arg))
                    Logger.logMessage(_code=code, _message=message,
                                      _errorPosition=arg.get_source_position(), _logLevel=LOGGING_LEVEL.ERROR)
        return
