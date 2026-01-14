# -*- coding: utf-8 -*-
#
# co_co_parameters_defined_before_internals_defined_before_state.py
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
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoParametersDefinedBeforeInternalsDefinedBeforeState:
    r"""
    Variables in the state block are only allowed to refer back to internals and parameters, internals are only allowed to refer back to parameters, and parameters can refer back to neither but need to be defined in a self-contained manner.

    Allowed:

    .. ::

          parameters:
              bar real = 123

          state:
              foo real = bar

    Not allowed:

    .. ::

          parameters:
              bar real = foo

          state:
              foo real = 123

    Not allowed:

    .. ::

          state:
              foo real = 123

          parameters:
              bar real = foo

    """

    @classmethod
    def check_co_co(cls, node: ASTModel):
        """
        Ensures the coco for the handed over neuron.
        :param node: a single neuron instance.
        """
        node.accept(CoCoParametersDefinedBeforeInternalsDefinedBeforeStateVisitor())


class CoCoParametersDefinedBeforeInternalsDefinedBeforeStateVisitor(ASTVisitor):

    def visit_variable(self, node: ASTVariable):
        """
        Ensures the coco.
        :param node: a single equation object.
        """
        # ensure node is declared (in scope)?

        # if node is in state block:
        #   check that node is declared earlier up in state block, OR that node is declared internals, OR that node is declared in parameters

        # elif node is in internals block:
        #   check that node is declared earlier up in internals block, OR that node is declared in parameters

        # elif node is in parameters block:
        #   check that node is declared earlier up in parameters block
