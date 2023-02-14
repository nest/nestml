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

import re


class ODEToolboxUtils:
    r"""
    A collection of helpful methods for interfacing with ODE-toolbox.
    """

    @classmethod
    def _rewrite_piecewise_into_ternary(cls, s: str) -> str:
        r"""Rewrite calls to ``Piecewise((expr_if_true, cond), (expr_if_false, True))`` in sympy syntax to ``cond ? expr_if_true : expr_if_false`` in NESTML syntax.
        """
        for match in re.findall(r"Piecewise\(.*\)", s):
            match = match[len("Piecewise("):]
            match = match[:-1]
            args = re.findall(r"\(.*?\,.*?\)", match)
            assert len(args) == 2, "Can only handle two-part piecewise conditional function"
            expr_if_true = re.search(r"\(.*?\,", args[0])[0][1:-1]
            expr_if_false = re.search(r"\(.*?\,", args[1])[0][1:-1]
            cond = re.search(r"\,.*?\)", args[0])[0][2:-1]
            s = s.replace("Piecewise(" + match + ")", "((" + cond + ") ? (" + expr_if_true + ") : (" + str(expr_if_false) + "))")

        return s
