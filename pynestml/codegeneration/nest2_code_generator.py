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
from pynestml.codegeneration.printers.nest2_gsl_reference_converter import NEST2GSLReferenceConverter
from pynestml.codegeneration.printers.nest2_reference_converter import NEST2ReferenceConverter
from pynestml.codegeneration.printers.nest_printer import NestPrinter
from pynestml.codegeneration.printers.unitless_expression_printer import UnitlessExpressionPrinter


class NEST2CodeGenerator(NESTCodeGenerator):
    r"""
    Code generator for a NEST Simulator (versions 2.x.x, in particular, 2.20.2 or higher) C++ extension module.
    """

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__(options)

        self._target = "NEST2"

        self._gsl_reference_converter = NEST2GSLReferenceConverter()
        self._gsl_printer = UnitlessExpressionPrinter(reference_converter=self._gsl_reference_converter)

        self._nest_reference_converter = NEST2ReferenceConverter()
        self._expression_printer = UnitlessExpressionPrinter(reference_converter=self._nest_reference_converter)

        self._unitless_nest_printer = NestPrinter(reference_converter=self._nest_reference_converter,
                                                  types_printer=self._types_printer,
                                                  expression_printer=self._expression_printer)

        self._unitless_nest_gsl_printer = NestPrinter(reference_converter=self._nest_reference_converter,
                                                      types_printer=self._types_printer,
                                                      expression_printer=self._expression_printer)
