# -*- coding: utf-8 -*-
#
# spinnaker_code_generator.py
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

from typing import Sequence, Union, Optional, Mapping, Any, Dict

import os

from pynestml.utils.logger import Logger
from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.codegeneration.printers.spinnaker_reference_converter import SpinnakerReferenceConverter
from pynestml.codegeneration.printers.spinnaker_types_printer import SpinnakerTypesPrinter
from pynestml.codegeneration.printers.unitless_expression_printer import UnitlessExpressionPrinter
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.codegeneration.printers.nest_printer import NestPrinter


class SpiNNakerCodeGenerator(CodeGenerator):
    """
    Code generator for SpiNNaker
    """

    codegen_int: Optional[NESTCodeGenerator] = None

    _default_options = {
        "templates": {
            "path": os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.join(
                os.pardir, "codegeneration", "resources_spinnaker")))),
            "model_templates": {
                "neuron": ["@NEURON_NAME@_impl.h.jinja2",
                           "@NEURON_NAME@.py.jinja2",
                           "@NEURON_NAME@_impl.py.jinja2",
                           "extra.mk.jinja2",
                           "extra_neuron.mk.jinja2",
                           "Makefile_@NEURON_NAME@_impl.jinja2"],
            },
            "module_templates": ["Makefile.jinja2", "extra_neuron.mk.jinja2"]
        }
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super().__init__("SpiNNaker", options)

        self._reference_converter = SpinnakerReferenceConverter()
        self._expression_printer = CppExpressionPrinter(self._reference_converter)

        self.codegen_int = NESTCodeGenerator(options)
        self.codegen_int._types_printer = SpinnakerTypesPrinter()
        self.codegen_int._gsl_reference_converter = self._reference_converter
        self.codegen_int._nest_reference_converter = self._reference_converter
        self.codegen_int._gsl_printer = UnitlessExpressionPrinter(reference_converter=self.codegen_int._nest_reference_converter)
        self.codegen_int._unitless_nest_printer = NestPrinter(reference_converter=self.codegen_int._nest_reference_converter,
                                                              types_printer=self.codegen_int._types_printer,
                                                              expression_printer=self._expression_printer)
        self.codegen_int._unitless_nest_gsl_printer = NestPrinter(reference_converter=self.codegen_int._nest_reference_converter,
                                                                  types_printer=self.codegen_int._types_printer,
                                                                  expression_printer=self._expression_printer)
        self.codegen_int._default_options["templates"] = SpiNNakerCodeGenerator._default_options["templates"]
        self.codegen_int.set_options({"templates": self.codegen_int._default_options["templates"]})
        self.codegen_int.setup_template_env()

    def generate_code(self, models: Sequence[Union[ASTNeuron, ASTSynapse]]) -> None:
        neurons = [model for model in models if isinstance(model, ASTNeuron)]
        self.codegen_int.analyse_transform_neurons(neurons)
        self.codegen_int.generate_neurons(neurons)
        self.codegen_int.generate_module_code(neurons, [])

        for astnode in neurons:
            if Logger.has_errors(astnode):
                raise Exception("Error(s) occurred during code generation")

    def _get_neuron_model_namespace(self, neuron: ASTNeuron) -> Dict:
        return self.codegen_int._get_neuron_model_namespace(neuron)
