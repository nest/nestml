# -*- coding: utf-8 -*-
#
# co_co_on_receive_vectors_should_be_constant_size.py
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
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_model import ASTModel
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoOnReceiveVectorsShouldBeConstantSize(CoCo):
    r"""
    This CoCo is used to test the usage of onReceive blocks for vector ports of variable length.
    """

    @classmethod
    def check_co_co(cls, node: ASTModel):
        visitor = CoCoOnReceiveVectorsShouldBeConstantSizeVisitor()
        node.accept(visitor)


class CoCoOnReceiveVectorsShouldBeConstantSizeVisitor(ASTVisitor):
    def visit_input_port(self, node: ASTInputPort):
        if node.has_size_parameter():
            try:
                int(node.get_size_parameter())
            except ValueError:
                # exception converting size parameter to int; hence, not allowed
                code, message = Messages.get_vector_input_ports_should_be_of_constant_size()
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR, code=code, message=message)
