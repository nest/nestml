# -*- coding: utf-8 -*-
#
# codegen_opts_detects_non_existing.py
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
import pytest

from pynestml.exceptions.code_generator_options_exception import CodeGeneratorOptionsException
from pynestml.frontend.pynestml_frontend import generate_nest_target


@pytest.mark.xfail(strict=True, raises=CodeGeneratorOptionsException)
def test_codegen_opts_detects_non_existing():
    generate_nest_target(input_path="models/neurons/iaf_psc_exp.nestml",
                         codegen_opts={"non_existing_options": "42"})
