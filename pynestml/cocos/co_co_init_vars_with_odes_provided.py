# -*- coding: utf-8 -*-
#
# co_co_init_vars_with_odes_provided.py
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

from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.cocos.co_co import CoCo
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoInitVarsWithOdesProvided(CoCo):
    """
    This CoCo ensures that all variables which have been declared in the "initial_values" block are provided
    with a corresponding ode.
    Allowed:
        initial_values:
            V_m mV = E_L
        end
        ...
        equations:
            V_m' = ...
        end
    Not allowed:
        initial_values:
            V_m mV = E_L
        end
        ...
        equations:
            # no ode declaration given
        end
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Checks this coco on the handed over neuron.
        :param node: a single neuron instance.
        :type node: ASTNeuron
        """
        assert (node is not None and isinstance(node, ASTNeuron)), \
            '(PyNestML.CoCo.VariablesDefined) No or wrong type of neuron provided (%s)!' % type(node)
        node.accept(InitVarsVisitor())
        return


class InitVarsVisitor(ASTVisitor):
    """
    This visitor checks that all variables as provided in the init block have been provided with an ode.
    """

    def visit_declaration(self, node):
        """
        Checks the coco on the current node.
        :param node: a single declaration.
        :type node: ast_declaration
        """
        for var in node.get_variables():
            symbol = node.get_scope().resolve_to_symbol(var.get_complete_name(), SymbolKind.VARIABLE)
            # first check that all initial value variables have a lhs
            if symbol is not None and symbol.is_init_values() and not node.has_expression():
                code, message = Messages.get_no_rhs(symbol.get_symbol_name())
                Logger.log_message(error_position=var.get_source_position(), code=code,
                                   message=message, log_level=LoggingLevel.WARNING)
            # now check that they have been provided with an ODE
            if symbol is not None and symbol.is_init_values() \
                    and not (symbol.is_ode_defined() or symbol.is_kernel()) and not symbol.is_function:
                code, message = Messages.get_no_ode(symbol.get_symbol_name())
                Logger.log_message(error_position=var.get_source_position(), code=code,
                                   message=message, log_level=LoggingLevel.WARNING)
            if symbol is not None and symbol.is_init_values() and not symbol.has_initial_value():
                code, message = Messages.get_no_init_value(symbol.get_symbol_name())
                Logger.log_message(error_position=var.get_source_position(), code=code,
                                   message=message, log_level=LoggingLevel.WARNING)
        return
