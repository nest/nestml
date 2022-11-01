# -*- coding: utf-8 -*-
#
# nestml_variable_printer.py
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

from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.utils.ast_utils import ASTUtils


class NestMLVariablePrinter(VariablePrinter):
    r"""
    Print ``ASTVariable``s in NESTML syntax.
    """

    def print_variable(self, ast_variable: ASTVariable, prefix: str = '') -> str:
        """
        Returns the same string
        :param ast_variable: a single variable
        :return: the same string
        """
        return prefix + ast_variable.get_complete_name()
