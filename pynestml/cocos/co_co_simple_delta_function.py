# -*- coding: utf-8 -*-
#
# co_co_simple_delta_function.py
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
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_kernel import ASTKernel


class CoCoSimpleDeltaFunction(CoCo):
    """
    Check that predefined delta function is only used with single argument ``t``.
    """

    @classmethod
    def check_co_co(cls, node):
        """
        Checks if this coco applies for the handed over neuron.

        :param node: a single neuron instance.
        :type node: ASTNeuron
        """

        def check_simple_delta(_expr=None):
            if _expr.is_function_call() and _expr.get_function_call().get_name() == "delta":
                deltafunc = _expr.get_function_call()
                parent = node.get_parent(_expr)

                # check the argument
                if not (len(deltafunc.get_args()) == 1
                        and type(deltafunc.get_args()[0]) is ASTSimpleExpression
                        and deltafunc.get_args()[0].get_variable() is not None
                        and deltafunc.get_args()[0].get_variable().name == "t"):
                    code, message = Messages.delta_function_one_arg(deltafunc)
                    Logger.log_message(code=code, message=message,
                                       error_position=_expr.get_source_position(), log_level=LoggingLevel.ERROR)

                if type(parent) is not ASTKernel:
                    code, message = Messages.delta_function_cannot_be_mixed()
                    Logger.log_message(code=code, message=message,
                                       error_position=_expr.get_source_position(), log_level=LoggingLevel.ERROR)

        def func(x):
            return check_simple_delta(x) if isinstance(x, ASTSimpleExpression) else True

        node.accept(ASTHigherOrderVisitor(func))
