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

from typing import Any, Mapping, Optional, Sequence, Union

import os

from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.codegeneration.printers.python_standalone_printer import PythonStandalonePrinter
from pynestml.codegeneration.printers.python_standalone_reference_converter import PythonStandaloneReferenceConverter
from pynestml.codegeneration.printers.python_types_printer import PythonTypesPrinter
from pynestml.codegeneration.printers.unitless_expression_printer import UnitlessExpressionPrinter


class PythonStandaloneCodeGenerator(CodeGenerator):

    codegen_int: Optional[NESTCodeGenerator] = None

    _default_options = {
        "neuron_synapse_pairs": [],
        "preserve_expressions": False,
        "simplify_expression": "sympy.logcombine(sympy.powsimp(sympy.expand(expr)))",
        "templates": {
            "path": "point_neuron",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.cpp.jinja2", "@NEURON_NAME@.h.jinja2"],
                "synapse": ["@SYNAPSE_NAME@.h.jinja2"]
            },
            "module_templates": ["setup"]
        }
    }


    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("python_standalone", options)

        self.codegen_int = NESTCodeGenerator(options)
        self.codegen_int._types_printer = PythonTypesPrinter()
        self.codegen_int._gsl_reference_converter = PythonStandaloneReferenceConverter()
        self.codegen_int._nest_reference_converter = PythonStandaloneReferenceConverter()
        self.codegen_int._expressions_printer = UnitlessExpressionPrinter(reference_converter=self.codegen_int._nest_reference_converter)

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
        self.codegen_int._options["templates"]["model_templates"]["neuron"] = ["@NEURON_NAME@.py.jinja2"]
        self.codegen_int._options["templates"]["model_templates"]["synapse"] = ["@SYNAPSE_NAME@.py.jinja2"]
        self.codegen_int._options["templates"]["module_templates"] = ["simulator.py.jinja2", "test_python_standalone_module.py.jinja2", "neuron.py.jinja2", "synapse.py.jinja2", "spike_generator.py.jinja2", "utils.py.jinja2", "vectorizable.py.jinja2"]
        self.codegen_int.setup_template_env()

    def generate_code(self, models: Sequence[Union[ASTNeuron, ASTSynapse]]) -> None:
        self.codegen_int.generate_code(models)

    def set_options(self, options: Mapping[str, Any]) -> Mapping[str, Any]:
        return self.codegen_int.set_options(options)

