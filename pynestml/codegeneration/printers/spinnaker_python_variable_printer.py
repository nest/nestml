# -*- coding: utf-8 -*-
#
# python_variable_printer.py
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

from __future__ import annotations

try:
    # Available in the standard library starting with Python 3.12
    from typing import override
except ImportError:
    # Fallback for Python 3.8 - 3.11
    from typing_extensions import override

from pynestml.codegeneration.printers.python_variable_printer import PythonVariablePrinter
from pynestml.codegeneration.python_code_generator_utils import PythonCodeGeneratorUtils


class SpiNNakerPythonVariablePrinter(PythonVariablePrinter):
    r"""
    Variable printer for Python syntax.
    """

    @override
    def _print(self, variable, symbol, with_origin: bool = True) -> str:
        variable_name = SpiNNakerPythonVariablePrinter._print_python_name(variable.get_complete_name())

        if symbol.is_local():
            return variable_name

        if variable.is_delay_variable():
            return self._print_delay_variable(variable)

        if with_origin:
            return PythonCodeGeneratorUtils.print_symbol_origin(symbol, variable) % variable_name

        return "self._nestml_model_variables[\"" + variable_name + "\"]"
