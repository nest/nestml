# -*- coding: utf-8 -*-
#
# co_co_integrate_odes_called_if_equations_defined.py
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
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.symbols.predefined_functions import PredefinedFunctions


class CoCoIntegrateOdesCalledIfEquationsDefined(CoCo):
    """
    This coco ensures that integrate_odes() is called if one or more dynamical equations are defined.
    """

    @classmethod
    def check_co_co(cls, node: ASTNeuron):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        """
        if isinstance(node, ASTSynapse):
            return
        equations_defined_visitor = EquationsDefinedVisitor()
        node.accept(equations_defined_visitor)
        integrate_odes_called_visitor = IntegrateOdesCalledVisitor()
        node.accept(integrate_odes_called_visitor)
        if equations_defined_visitor.equations_defined() and not integrate_odes_called_visitor.integrate_odes_called():
            code, message = Messages.get_equations_defined_but_integrate_odes_not_called()
            Logger.log_message(code=code, message=message,
                               error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)


class EquationsDefinedVisitor(ASTVisitor):
    """
    This visitor checks if equations are defined.
    """

    _equations_defined = False

    def visit_ode_equation(self, node):
        self._equations_defined = True

    def equations_defined(self) -> bool:
        return self._equations_defined


class IntegrateOdesCalledVisitor(ASTVisitor):
    """
    This visitor checks if integrate_odes() is called.
    """

    _integrate_odes_called = False

    def visit_function_call(self, node: ASTFunctionCall):
        if node.get_name() == PredefinedFunctions.INTEGRATE_ODES:
            self._integrate_odes_called = True

    def integrate_odes_called(self) -> bool:
        return self._integrate_odes_called
