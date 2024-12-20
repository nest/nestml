# -*- coding: utf-8 -*-
#
# ast_variable_visitor.py
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

from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import MessageCode
from pynestml.utils.unit_type import UnitType
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTVariableVisitor(ASTVisitor):
    """
    This visitor visits a single variable and updates its type.
    """

    def visit_simple_expression(self, node: ASTSimpleExpression):
        """
        Visits a single variable as contained in a simple expression and derives its type.
        :param node: a single simple expression
        """
        assert isinstance(node, ASTSimpleExpression), \
            '(PyNestML.Visitor.VariableVisitor) No or wrong type of simple expression provided (%s)!' % type(node)
        assert (node.get_scope() is not None), \
            '(PyNestML.Visitor.VariableVisitor) No scope found, run symboltable creator!'

        scope = node.get_scope()
        var_name = node.get_variable().get_complete_name()
        var_resolve = node.get_variable().get_scope().resolve_to_symbol(var_name, SymbolKind.VARIABLE)

        # update the type of the variable according to its symbol type.
        if var_resolve is not None:
            inport = ASTUtils.get_input_port_by_name(ASTUtils.find_parent_node_by_type(node, ASTModel).get_input_blocks(), node.get_variable().get_name())
            if inport and inport.is_spike():
                # this variable represents a spiking input port
                if ASTUtils.find_parent_node_by_type(node, ASTEquationsBlock):
                    # it appears in an equations block; units are [units of attribute / s]
                    from astropy import units as u
                    if inport.get_parameters():
                        node.type = var_resolve.get_type_symbol() * UnitTypeSymbol(UnitType(name=str("1/s"), unit=1 / u.si.s))
                    else:
                        node.type = var_resolve.get_type_symbol()    # the type of the base port is [1/s]
                else:
                    # it appears in an equations block; units are [units of attribute]
                    node.type = var_resolve.get_type_symbol()
            else:
                # variable does not represent a spiking input port
                node.type = var_resolve.get_type_symbol()

            node.type.referenced_object = node
            return

        # check if var_name is actually a type literal (e.g. "mV")
        var_resolve = scope.resolve_to_symbol(var_name, SymbolKind.TYPE)
        if var_resolve is not None:
            node.type = var_resolve
            node.type.referenced_object = node
            return

        message = 'Variable ' + str(node) + ' could not be resolved!'
        Logger.log_message(code=MessageCode.SYMBOL_NOT_RESOLVED,
                           error_position=node.get_source_position(),
                           message=message, log_level=LoggingLevel.ERROR)
        node.type = ErrorTypeSymbol()

    def visit_expression(self, node):
        raise Exception("Deprecated method used!")
