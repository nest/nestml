# -*- coding: utf-8 -*-
#
# python_standalone_code_generator.py
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

from typing import Optional

import os

from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.codegeneration.printers.python_standalone_printer import PythonStandalonePrinter
from pynestml.codegeneration.printers.python_standalone_reference_converter import PythonStandaloneReferenceConverter
from pynestml.codegeneration.printers.python_types_printer import PythonTypesPrinter
from pynestml.codegeneration.printers.unitless_expression_printer import UnitlessExpressionPrinter


class PythonStandaloneCodeGenerator(CodeGenerator):

    codegen_int: Optional[NESTCodeGenerator] = None

    def __init__(self):
        self.codegen_int = NESTCodeGenerator()
        self.codegen_int._types_printer = PythonTypesPrinter()
        self.codegen_int._gsl_reference_converter = PythonStandaloneReferenceConverter()
        self.codegen_int._nest_reference_converter = PythonStandaloneReferenceConverter()
        self.codegen_int._expressions_printer = UnitlessExpressionPrinter(reference_converter=self.codegen_int._nest_reference_converter,
                                                                          types_printer=self.codegen_int._types_printer)

        self.codegen_int._gsl_printer = PythonStandalonePrinter(reference_converter=self.codegen_int._nest_reference_converter,
                                                                types_printer=self.codegen_int._types_printer,
                                                                expressions_printer=self.codegen_int._expressions_printer)

        self.codegen_int._unitless_nest_printer = PythonStandalonePrinter(reference_converter=self.codegen_int._nest_reference_converter,
                                                                          types_printer=self.codegen_int._types_printer,
                                                                          expressions_printer=self.codegen_int._expressions_printer)

        self.codegen_int._unitless_nest_gsl_printer = PythonStandalonePrinter(reference_converter=self.codegen_int._nest_reference_converter,
                                                                              types_printer=self.codegen_int._types_printer,
                                                                              expressions_printer=self.codegen_int._expressions_printer)

        self.codegen_int._options["templates"]["path"] = os.path.join(os.path.dirname(__file__), "resources_python_standalone")
        self.codegen_int._options["templates"]["model_templates"]["neuron"] = ["Neuron.py.jinja2"]
        self.codegen_int._options["templates"]["model_templates"]["synapse"] = ["Synapse.py.jinja2"]
        self.codegen_int._options["templates"]["module_templates"] = ["simulator.py.jinja2", "test_python_standalone_module.py.jinja2", "neuron.py.jinja2", "spike_generator.py.jinja2", "utils.py.jinja2"]
        self.codegen_int.setup_template_env()

    def generate_code(self, neurons, synapses):
        self.codegen_int.generate_code(neurons, synapses)
