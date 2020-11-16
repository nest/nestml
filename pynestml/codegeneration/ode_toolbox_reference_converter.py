# -*- coding: utf-8 -*-
#
# ode_toolbox_reference_converter.py
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
from pynestml.codegeneration.nestml_reference_converter import NestMLReferenceConverter
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.utils.ast_utils import ASTUtils


class ODEToolboxReferenceConverter(NestMLReferenceConverter):
    """
    Convert into a format accepted by ODE-toolbox as input.
    """

    def convert_name_reference(self, ast_variable, prefix=''):
        """
        Returns the same string
        :param ast_variable: a single variable
        :type ast_variable: ASTVariable
        :return: the same string
        :rtype: str
        """
        return prefix + ast_variable.get_complete_name().replace("$", "__DOLLAR")

    def convert_ternary_operator(self):
        """
        ODE-toolbox does not support ternary operator! Ignore condition, and hard-wire to first parameter.
        :return: a string representation
        :rtype: str
        """
        s = '0 * (' + '%s' + ') + (' + '%s' + ') + 0 * (' + '%s' + ')'
        return '(' + s + ')'
