# -*- coding: utf-8 -*-
#
# ode_toolbox_utils.py
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

import sympy
from sympy.printing.str import StrPrinter


class ODEToolboxUtils:
    r"""
    A collection of helpful methods for interfacing with ODE-toolbox.
    """

    @classmethod
    def _rewrite_piecewise_into_ternary(cls, s: str) -> str:
        r"""Rewrite calls to ``Piecewise((expr_if_true, cond), (expr_if_false, True))`` in sympy syntax to ``cond ? expr_if_true : expr_if_false`` in NESTML syntax.
        """

        _sympy_globals_no_functions = {"Symbol": sympy.Symbol,
                                       "Integer": sympy.Integer,
                                       "Float": sympy.Float,
                                       "Function": sympy.Function}

        sympy_expr = sympy.parsing.sympy_parser.parse_expr(s, global_dict=_sympy_globals_no_functions)

        class MySympyPrinter(StrPrinter):
            """Resulting expressions will be parsed by NESTML parser. R
            """
            def _print_Function(self, expr):
                if expr.func.__name__ == "Piecewise":
                    assert len(expr.args) == 2, "Can only handle two-part piecewise conditional function"
                    cond = self.doprint(expr.args[0][1])
                    cond_always_true = expr.args[1][1]
                    assert cond_always_true == sympy.true
                    expr_if_true = self.doprint(expr.args[0][0])
                    expr_if_false = self.doprint(expr.args[1][0])
                    return "((" + cond + ") ? (" + expr_if_true + ") : (" + expr_if_false + "))"

                return super()._print_Function(expr)

        s_reformatted = MySympyPrinter().doprint(sympy_expr)

        return s_reformatted
