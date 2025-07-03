# -*- coding: utf-8 -*-
#
# nestml_function_call_printer.py
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

from pynestml.codegeneration.printers.function_call_printer import FunctionCallPrinter
from pynestml.meta_model.ast_function_call import ASTFunctionCall


class NESTMLFunctionCallPrinter(FunctionCallPrinter):
    r"""
    Printer for ASTFunctionCall in C++ syntax.
    """

    def print_function_call(self, node: ASTFunctionCall) -> str:
        ret = str(node.get_name()) + "("
        for i in range(0, len(node.get_args())):
            ret += self._expression_printer.print(node.get_args()[i])
            if i < len(node.get_args()) - 1:  # in the case that it is not the last arg, print also a comma
                ret += ", "

        ret += ")"

        return ret
