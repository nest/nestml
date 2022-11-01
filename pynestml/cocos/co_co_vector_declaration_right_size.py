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
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.integer_type_symbol import IntegerTypeSymbol
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoVectorDeclarationRightSize(CoCo):
    r"""
    This CoCo checks if the size of the vector during vector declaration is an integer and greater than 0, and that the index into a vector is of type integer and non-negative.
    """

    @classmethod
    def check_co_co(cls, node: ASTNeuron):
        visitor = VectorDeclarationVisitor()
        visitor._neuron = node
        node.accept(visitor)


class VectorDeclarationVisitor(ASTVisitor):
    r"""
    This visitor checks if the size of the vector during vector declaration is an integer and greater than 0, and that the index into a vector is of type integer and non-negative.
    """

    def visit_variable(self, node: ASTVariable):
        vector_parameter = node.get_vector_parameter()
        if vector_parameter is not None:
            if isinstance(self._neuron.get_parent(node), ASTDeclaration):
                # node is being declared: size should be >= 1
                min_index = 1
            else:
                # node is being indexed; index should be >= 0
                min_index = 0

            # account for negative numbers as an index, which is an expression (e.g. "-42")
            if isinstance(vector_parameter, ASTExpression) and vector_parameter.is_unary_operator() and vector_parameter.get_unary_operator().is_unary_minus and vector_parameter.get_expression().is_numeric_literal():
                code, message = Messages.get_vector_parameter_wrong_size(node.get_complete_name() + "[" + str(vector_parameter) + "]", str(vector_parameter))
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)
                return

            # otherwise, ``vector_parameter`` is a SimpleExpression
            assert vector_parameter.is_variable() or vector_parameter.is_numeric_literal()

            vector_parameter_val = None

            if vector_parameter.is_numeric_literal():
                if not isinstance(vector_parameter.type, IntegerTypeSymbol):
                    code, message = Messages.get_vector_parameter_wrong_type(node.get_complete_name() + "[" + str(vector_parameter) + "]")
                    Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                       code=code, message=message)
                    return

                vector_parameter_val = int(vector_parameter.get_numeric_literal())

            if vector_parameter.is_variable():
                symbol = vector_parameter.get_scope().resolve_to_symbol(vector_parameter.get_variable().get_complete_name(),
                                                                        SymbolKind.VARIABLE)

                if symbol is None or not isinstance(symbol.get_type_symbol(), IntegerTypeSymbol):
                    code, message = Messages.get_vector_parameter_wrong_type(node.get_complete_name() + "[" + str(vector_parameter) + "]")
                    Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                       code=code, message=message)
                    return

                vector_parameter_val = int(str(symbol.get_declaring_expression()))

            if vector_parameter_val is not None and vector_parameter_val < min_index:
                code, message = Messages.get_vector_parameter_wrong_size(node.get_complete_name(),
                                                                         str(vector_parameter_val))
                Logger.log_message(error_position=node.get_source_position(), log_level=LoggingLevel.ERROR,
                                   code=code, message=message)
