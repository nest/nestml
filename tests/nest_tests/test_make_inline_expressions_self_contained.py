# -*- coding: utf-8 -*-
#
# test_make_inline_expressions_self_contained.py
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

import os

from pynestml.frontend.pynestml_frontend import generate_nest_target


class TestMakeInlineExpressionsSelfContained:
    r"""
    Test the transformer that makes inline expressions self contained.
    """

    def test_make_inline_expression_self_contained(self):
        r"""Generate the model code"""
        input_files = [os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "resources", "beta_function_with_inline_expression_neuron.nestml")))]
        generate_nest_target(input_path=input_files,
                             logging_level="DEBUG",
                             codegen_opts={"solver": "numeric"})
