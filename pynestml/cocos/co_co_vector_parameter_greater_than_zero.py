# -*- coding: utf-8 -*-
#
# co_co_vector_parameter_greater_than_zero.py
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
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoVectorParameterGreaterThanZero(CoCo):
    """
    This CoCo checks if the size of the vector (vector parameter) in a vector declaration is greater than 0
    """

    @classmethod
    def check_co_co(cls, node: ASTNeuron):
        visitor = VectorDeclarationVisitor()
        node.accept(visitor)


class VectorDeclarationVisitor(ASTVisitor):

    def visit_declaration(self, node: ASTDeclaration):
        variables = node.get_variables()

        for variable in variables:
            vector_parameter = variable.get_vector_parameter()
            if vector_parameter is not None:
                vector_parameter_var = ASTVariable(vector_parameter, scope=node.get_scope())
                symbol = vector_parameter_var.get_scope().resolve_to_symbol(vector_parameter_var.get_complete_name(),
                                                                            SymbolKind.VARIABLE)
                if symbol is not None:
                    value = int(str(symbol.get_declaring_expression()))
                else:
                    value = int(vector_parameter)

                if value <= 0:
                    code, message = Messages.get_vector_parameter_wrong_size(vector_parameter_var.get_complete_name(),
                                                                             str(value))
                    Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                       code=code, message=message)
