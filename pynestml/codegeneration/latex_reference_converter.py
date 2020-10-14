# -*- coding: utf-8 -*-
#
# latex_reference_converter.py
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

from pynestml.codegeneration.i_reference_converter import IReferenceConverter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.utils.ast_utils import ASTUtils
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.predefined_units import PredefinedUnits


class LatexReferenceConverter(IReferenceConverter):
    """
    ReferenceConverter for the LaTeX target.
    """

    def convert_unary_op(self, ast_unary_operator):
        """
        Convert unary operator.

        :param ast_unary_operator: a unary operator
        :type ast_unary_operator: ASTUnaryOperator
        :return: pretty-printed format string
        :rtype: str
        """
        return str(ast_unary_operator) + '%s'

    def convert_name_reference(self, ast_variable):
        """
        Convert name reference.

        :param ast_variable: a single variable
        :type ast_variable: ASTVariable
        :return: pretty-printed format string
        :rtype: str
        """
        var_name = ast_variable.get_name()
        var_complete_name = ast_variable.get_complete_name()
        if not ast_variable.get_scope().resolve_to_symbol(var_complete_name, SymbolKind.VARIABLE) \
                and PredefinedUnits.is_unit(var_complete_name):
            # convert a unit (e.g. ms, pA)
            # var_name = "\color{grey}\mathrm{" + var_name + "}\color{black}"	# readthedocs does not support \color!
            var_name = r"\mathrm{" + var_name + "}"
        # convert first underscore
        usc_idx = var_name.find("_")
        if usc_idx > 0:
            var_name = var_name[:usc_idx] + "_{" + var_name[usc_idx + 1:].replace("_", ",") + "}" + "'" * ast_variable.get_differential_order()
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
            before = var_name
            var_name = re.sub(r"(?<![a-zA-Z])(" + symbol_find + ")(?![a-zA-Z])",
                              symbol_replace, var_name)  # "whole word" match
            after = var_name
        return var_name

    def convert_function_call(self, function_call):
        """
        Convert function call.

        :param function_call: a function call
        :type function_call: ASTFunctionCall
        :return: pretty-printed format string
        :rtype: str
        """
        result = function_call.get_name()

        symbols = {
            "convolve": r"\\text{convolve}"
        }

        for symbol_find, symbol_replace in symbols.items():
            result = re.sub(r"(?<![a-zA-Z])(" + symbol_find + ")(?![a-zA-Z])",
                            symbol_replace, result)  # "whole word" match

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            result += '(' + ', '.join(['%s' for _ in range(n_args)]) + ')'
        else:
            result += '()'

        return result

    def convert_binary_op(self, ast_binary_operator, wide=False):
        """
        Convert binary operator.

        :param ast_binary_operator: a single binary operator
        :type ast_binary_operator: ASTBinaryOperator
        :return: pretty-printed format string
        :rtype: str
        """
        if ast_binary_operator.is_div_op:
            if wide:
                return r"\frac 1 { %(rhs)s } \left( { %(lhs)s } \right) "
            else:
                return r"\frac{ %(lhs)s } { %(rhs)s }"
        elif ast_binary_operator.is_times_op:
            return r'%(lhs)s \cdot %(rhs)s'
        elif ast_binary_operator.is_pow_op:
            return r'{ %(lhs)s }^{ %(rhs)s }'
        else:
            return r'%(lhs)s' + str(ast_binary_operator) + r'%(rhs)s'

    def convert_constant(self, constant_name):
        """
        Convert constant.

        :param constant_name: a constant name
        :type constant_name: str
        :return: pretty-printed format string
        :rtype: str
        """
        return constant_name

    def convert_ternary_operator(self):
        """
        Convert ternary operator.

        :return: pretty-printed format string
        :rtype: str
        """
        return '(' + '%s' + ')?(' + '%s' + '):(' + '%s' + ')'

    def convert_logical_operator(self, op):
        return str(op)

    def convert_arithmetic_operator(self, op):
        return str(op)

    def convert_encapsulated(self):
        return '(%s)'

    def convert_comparison_operator(self, op):
        return str(op)

    def convert_logical_not(self):
        return "\neg"

    def convert_bit_operator(self, op):
        return str(op)
