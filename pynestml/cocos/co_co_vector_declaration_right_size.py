# -*- coding: utf-8 -*-
#
# co_co_vector_declaration_right_size.py
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
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoVectorDeclarationRightSize(CoCo):
    """
    This CoCo checks if the size of the vector during vector declaration is greater than 0
    """

    @classmethod
    def check_co_co(cls, node: ASTNeuron):
        visitor = VectorDeclarationVisitor()
        node.accept(visitor)


class VectorDeclarationVisitor(ASTVisitor):
    """
    This visitor ensures that vectors are declared with size greater than 0
    """

    def visit_declaration(self, node: ASTDeclaration):

        variables = node.get_variables()
        for variable in variables:
            vector_parameter = variable.get_vector_parameter()
            if vector_parameter is not None:
                assert vector_parameter.is_variable() or vector_parameter.is_numeric_literal()

                vector_parameter_val = None

                if vector_parameter.is_numeric_literal():
                    assert isinstance(vector_parameter.type, IntegerTypeSymbol)
                    vector_parameter_val = int(vector_parameter.get_numeric_literal())

                if vector_parameter.is_variable():
                    symbol = vector_parameter.get_scope().resolve_to_symbol(vector_parameter.get_variable().get_complete_name(),
                                                                            SymbolKind.VARIABLE)

                    assert symbol is not None
                    assert isinstance(symbol.get_type_symbol(), IntegerTypeSymbol)

                    vector_parameter_val = int(str(symbol.get_declaring_expression()))

                if vector_parameter_val is not None and vector_parameter_val <= 0:
                    code, message = Messages.get_vector_parameter_wrong_size(vector_parameter.get_variable().get_complete_name(),
                                                                             str(vector_parameter_val))
                    Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                       code=code, message=message)
