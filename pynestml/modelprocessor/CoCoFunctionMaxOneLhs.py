#
# CoCoFunctionMaxOneLhs.py
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
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class CoCoFunctionMaxOneLhs(CoCo):
    """
    This coco ensures that whenever a function (aka alias) is declared, only one left-hand side is present.
    Allowed:
        function V_rest mV = V_m - 55mV
    Not allowed:
        function V_reset,V_rest mV = V_m - 55mV
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionsWithLhs) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(FunctionMaxOneLhs())
        return


class FunctionMaxOneLhs(ASTVisitor):
    """
    This visitor ensures that every function has exactly one lhs.
    """

    def visit_declaration(self, node=None):
        """
        Checks the coco.
        :param node: a single declaration.
        :type node: ASTDeclaration
        """
        if node.is_function() and len(node.get_variables()) > 1:
            code, message = Messages.getSeveralLhs(list((var.get_name() for var in node.get_variables())))
            Logger.logMessage(_errorPosition=node.get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR,
                              _code=code, _message=message)
        return
