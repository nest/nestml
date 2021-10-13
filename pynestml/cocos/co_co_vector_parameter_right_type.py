# -*- coding: utf-8 -*-
#
# co_co_vector_parameter_right_type.py
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
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoVectorParameterRightType(CoCo):
    """
    This CoCo ensures that the vector parameter is of the integer type
    """
    @classmethod
    def check_co_co(cls, node: ASTNeuron):
        visitor = VectorVariablesVisitor()
        node.accept(visitor)


class VectorVariablesVisitor(ASTVisitor):
    """
    A visitor to check if all the variables with a vector parameter has the parameter of type integer
    """
    def visit_variable(self, node: ASTVariable):
        vector_parameter = node.get_vector_parameter()
        if vector_parameter is not None:
            vector_parameter_var = ASTVariable(vector_parameter, scope=node.get_scope())
            symbol = vector_parameter_var.get_scope().resolve_to_symbol(vector_parameter_var.get_complete_name(),
                                                                        SymbolKind.VARIABLE)

            # vector parameter is a variable
            if symbol is not None:
                if not isinstance(symbol.get_type_symbol(), IntegerTypeSymbol):
                    code, message = Messages.get_vector_parameter_wrong_type(vector_parameter_var.get_complete_name())
                    Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,

                                       code=code, message=message)
