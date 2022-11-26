# -*- coding: utf-8 -*-
#
# latex_variable_printer.py
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

from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.symbol import SymbolKind


class LatexVariablePrinter(VariablePrinter):
    def print_variable(self, node: ASTVariable) -> str:
        """
        Convert name reference.

        :param ast_variable: a single variable
        :return: the corresponding string representation
        """
        var_name = node.get_name()
        var_complete_name = node.get_complete_name()
        if not node.get_scope().resolve_to_symbol(var_complete_name, SymbolKind.VARIABLE) \
                and PredefinedUnits.is_unit(var_complete_name):
            # convert a unit (e.g. ms, pA)
            # var_name = "\color{grey}\mathrm{" + var_name + "}\color{black}"	# readthedocs does not support \color!
            var_name = r"\mathrm{" + var_name + "}"
        # convert first underscore
        usc_idx = var_name.find("_")
        if usc_idx > 0:
            var_name = var_name[:usc_idx] + "_{" + var_name[usc_idx + 1:].replace("_", ",") + "}" + "'" * node.get_differential_order()
        symbols = {
            "inf": r"\\infty",
            "alpha": r"\\alpha",
            "beta": r"\\beta",
            "gamma": r"\\gamma",
            "delta": r"\\delta",
            "epsilon": r"\\epsilon",
            "zeta": r"\\zeta",
            "eta": r"\\eta",
            "theta": r"\\theta",
            "iota": r"\\iota",
            "kappa": r"\\kappa",
            "lambda": r"\\lambda",
            "labda": r"\\lambda",
            "mu": r"\\mu",
            "nu": r"\\nu",
            "xi": r"\\xi",
            "omnikron": "o",
            "pi": r"\\pi",
            "rho": r"\\rho",
            "sigma": r"\\sigma",
            "tau": r"\\tau",
            "upsilon": r"\\upsilon",
            "phi": r"\\phi",
            "chi": r"\\chi",
            "psi": r"\\psi",
            "omega": r"\\omega",
            "Alpha": r"\\Alpha",
            "Beta": r"\\Beta",
            "Gamma": r"\\Gamma",
            "Delta": r"\\Delta",
            "Epsilon": r"\\Epsilon",
            "Zeta": r"\\zeta",
            "Eta": r"\\Eta",
            "Theta": r"\\Theta",
            "Iota": r"\\Iota",
            "Kappa": r"\\Kappa",
            "Lambda": r"\\Lambda",
            "Labda": r"\\Lambda",
            "Mu": r"\\Mu",
            "Nu": r"\\Nu",
            "Xi": r"\\Xi",
            "Omnikron": "O",
            "Pi": r"\\Pi",
            "Rho": r"\\Rho",
            "Sigma": r"\\Sigma",
            "Tau": r"\\Tau",
            "Upsilon": r"\\Upsilon",
            "Phi": r"\\Phi",
            "Chi": r"\\Chi",
            "Psi": r"\\Psi",
            "Omega": r"\\Omega"
        }
        for symbol_find, symbol_replace in symbols.items():
            var_name = re.sub(r"(?<![a-zA-Z])(" + symbol_find + ")(?![a-zA-Z])",
                              symbol_replace, var_name)  # "whole word" match

        return var_name
