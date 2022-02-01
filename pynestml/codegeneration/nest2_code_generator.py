# -*- coding: utf-8 -*-
#
# nest2_code_generator.py
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

from typing import Any, Mapping, Optional

from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.codegeneration.nest2_gsl_reference_converter import NEST2GSLReferenceConverter
from pynestml.codegeneration.nest2_reference_converter import NEST2ReferenceConverter
from pynestml.codegeneration.unitless_expression_printer import UnitlessExpressionPrinter


class NEST2CodeGenerator(NESTCodeGenerator):
    r"""
    Code generator for a NEST Simulator (versions 2.x.x, in particular, 2.20.2 or higher) C++ extension module.
    """

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__(options)

        self._target = "NEST2"

        self.gsl_reference_converter = NEST2GSLReferenceConverter()
        self.gsl_printer = UnitlessExpressionPrinter(self.gsl_reference_converter)

        self.nest_reference_converter = NEST2ReferenceConverter()
        self.unitless_printer = UnitlessExpressionPrinter(self.nest_reference_converter)
