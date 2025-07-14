# -*- coding: utf-8 -*-
#
# co_co_integrate_odes_params_correct.py
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

from typing import Union

from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_model import ASTModel
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoIntegrateODEsParamsCorrect(CoCo):
    r"""
    This coco ensures that ``integrate_odes()`` contains either no parameters or only state variable names as parameters.
    """

    @classmethod
    def check_co_co(cls, model: ASTModel):
        """
        Ensures the coco for the handed over model.
        :param node: a single model instance.
        """
        model.accept(IntegrateODEsCheckerVisitor())


class IntegrateODEsCheckerVisitor(ASTVisitor):
    def visit_function_call(self, node):
        func_name = node.get_name()
        if func_name == 'integrate_odes':
            for arg in node.get_args():
                symbol_var = node.get_scope().resolve_to_symbol(str(arg), SymbolKind.VARIABLE)
                if symbol_var is None or not symbol_var.is_state():
                    code, message = Messages.get_integrate_odes_wrong_arg(str(arg))
                    Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)
                elif symbol_var.is_state() and arg.get_variable().get_differential_order() > 0:
                    code, message = Messages.get_integrate_odes_arg_higher_order(str(arg))
                    Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR)
