# -*- coding: utf-8 -*-
#
# nest_gpu_code_generator.py
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
import glob
import os
import shutil
from typing import Dict, Sequence, Optional, Mapping, Any

from pynestml.codegeneration.printers.cpp_function_call_printer import CppFunctionCallPrinter
from pynestml.codegeneration.printers.cpp_printer import CppPrinter

from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter

from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter

from pynestml.codegeneration.printers.cpp_variable_printer import CppVariablePrinter
from pynestml.codegeneration.printers.nest_gpu_function_call_printer import NESTGPUFunctionCallPrinter
from pynestml.codegeneration.printers.nest_gpu_numeric_function_call_printer import NESTGPUNumericFunctionPrinter
from pynestml.codegeneration.printers.nest_gpu_numeric_variable_printer import NESTGPUNumericVariablePrinter
from pynestml.codegeneration.printers.nest_gpu_variable_printer import NESTGPUVariablePrinter
from pynestml.codegeneration.printers.unitless_cpp_simple_expression_printer import UnitlessCppSimpleExpressionPrinter
from pynestml.meta_model.ast_neuron_or_synapse import ASTNeuronOrSynapse

from pynestml.utils.logger import LoggingLevel, Logger

from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.meta_model.ast_neuron import ASTNeuron


def replace_text_between_tags(filepath, replace_str, begin_tag="// <<BEGIN_NESTML_GENERATED>>",
                              end_tag="// <<END_NESTML_GENERATED>>", rfind=False):
    with open(filepath, "r") as f:
        file_str = f.read()

    # Find the start and end positions of the tags
    if rfind:
        start_pos = file_str.rfind(begin_tag) + len(begin_tag)
        end_pos = file_str.rfind(end_tag)
    else:
        start_pos = file_str.find(begin_tag) + len(begin_tag)
        end_pos = file_str.find(end_tag)

    # Concatenate the new string between the start and end tags and write it back to the file
    file_str = file_str[:start_pos] + replace_str + file_str[end_pos:]
    with open(filepath, "w") as f:
        f.write(file_str)
    f.close()


class NESTGPUCodeGenerator(NESTCodeGenerator):
    """
    A code generator for NEST GPU target
    """

    _default_options = {
        "neuron_parent_class": "BaseNeuron",
        "neuron_parent_class_include": "archiving_node.h",
        "preserve_expressions": False,
        "simplify_expression": "sympy.logcombine(sympy.powsimp(sympy.expand(expr)))",
        "templates": {
            "path": "resources_nest_gpu/point_neuron",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.cu.jinja2", "@NEURON_NAME@.h.jinja2"]
                #"@NEURON_NAME@_kernel.h.jinja2", "@NEURON_NAME@_rk5.h.jinja2"],
            },
            "module_templates": []
        },
        "solver": "analytic",
        "numeric_solver": "rk45",
        "nest_gpu_path": None
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(NESTCodeGenerator, self).__init__("nest_gpu",
                                                NESTGPUCodeGenerator._default_options.update(
                                                    options if options else {}))
        self._target = "NEST_GPU"
        if not self.option_exists("nest_gpu_path") or not self.get_option("nest_gpu_path"):
            if "NEST_GPU" in os.environ:
                self.nest_gpu_path = os.environ["NEST_GPU"]
            else:
                self.nest_gpu_path = os.getcwd()
            self.set_options({"nest_gpu_path": self.nest_gpu_path})
            Logger.log_message(None, -1, "The NEST-GPU path was automatically detected as: " + self.nest_gpu_path, None,
                               LoggingLevel.INFO)
        
        # make sure NEST GPU code generator contains all options that are present in the NEST code generator, like gap junctions flags needed by the template
        for k, v in NESTCodeGenerator._default_options.items():
            if not k in self._options.keys():
                self.add_options({k: v})

        self.analytic_solver = {}
        self.numeric_solver = {}
        self.non_equations_state_variables = {}

        self.setup_template_env()
        self.setup_printers()
        # TODO: setup the printers and reference converters

    def setup_printers(self):
        super().setup_printers()

        # Printer with origin
        self._nest_variable_printer = NESTGPUVariablePrinter(expression_printer=None, with_origin=True,
                                                             with_vector_parameter=False)
        self._nest_function_call_printer = NESTGPUFunctionCallPrinter(None)
        self._printer = CppExpressionPrinter(simple_expression_printer=CppSimpleExpressionPrinter(
            variable_printer=self._nest_variable_printer,
            constant_printer=self._constant_printer,
            function_call_printer=self._nest_function_call_printer))
        self._nest_variable_printer._expression_printer = self._printer
        self._nest_function_call_printer._expression_printer = self._printer
        self._nest_printer = CppPrinter(expression_printer=self._printer)

        # Printer without origin
        self._nest_variable_printer_no_origin = NESTGPUVariablePrinter(None, with_origin=False,
                                                                       with_vector_parameter=False)
        self._nest_function_call_printer_no_origin = NESTGPUFunctionCallPrinter(None)
        self._printer_no_origin = CppExpressionPrinter(simple_expression_printer=CppSimpleExpressionPrinter(
            variable_printer=self._nest_variable_printer_no_origin,
            constant_printer=self._constant_printer,
            function_call_printer=self._nest_function_call_printer_no_origin))
        self._nest_variable_printer_no_origin._expression_printer = self._printer_no_origin
        self._nest_function_call_printer_no_origin._expression_printer = self._printer_no_origin

        # Printer for numeric solver
        self._gsl_variable_printer = NESTGPUNumericVariablePrinter(None)
        self._gsl_function_call_printer = NESTGPUNumericFunctionPrinter(None)
        self._gsl_printer = CppExpressionPrinter(simple_expression_printer=UnitlessCppSimpleExpressionPrinter(
            variable_printer=self._gsl_variable_printer,
            constant_printer=self._constant_printer,
            function_call_printer=self._gsl_function_call_printer))
        self._gsl_function_call_printer._expression_printer = self._gsl_printer

    def generate_module_code(self, neurons: Sequence[ASTNeuron], synapses: Sequence[ASTSynapse]):
        """
        Modify some header and CUDA files for the new models to be recognized
        """
        for neuron in neurons:
            self.copy_models_from_target_path(neuron)
            self.add_model_name_to_neuron_header(neuron)
            self.add_model_to_neuron_class(neuron)
            self.add_files_to_makefile(neuron)

    def copy_models_from_target_path(self, neuron: ASTNeuron):
        """Copies all the files related to the neuron model to the NEST GPU src directory"""
        file_match_str = f"*{neuron.get_name()}*"
        dst_path = os.path.join(self.nest_gpu_path, "src")
        for file in glob.glob(os.path.join(FrontendConfiguration.get_target_path(), file_match_str)):
            shutil.copy(file, dst_path)

    def add_model_name_to_neuron_header(self, neuron: ASTNeuron):
        """
        Modifies the ``neuron_models.h`` file to add the newly generated model's header files
        """
        neuron_models_h_path = str(os.path.join(self.nest_gpu_path, "src", "neuron_models.h"))
        shutil.copy(neuron_models_h_path, neuron_models_h_path + ".bak")

        replace_str = "\ni_" + neuron.get_name() + "_model,\n"
        replace_text_between_tags(neuron_models_h_path, replace_str)

        replace_str = "\n, \"" + neuron.get_name() + "\"\n"
        replace_text_between_tags(neuron_models_h_path, replace_str, rfind=True)

    def add_model_to_neuron_class(self, neuron: ASTNeuron):
        """
        Modifies the ``neuron_models.cu`` file to add the newly generated model's .cu file
        """
        neuron_models_cu_path = str(os.path.join(self.nest_gpu_path, "src", "neuron_models.cu"))
        shutil.copy(neuron_models_cu_path, neuron_models_cu_path + ".bak")

        replace_str = "\n#include \"" + neuron.get_name() + ".h\"\n"
        replace_text_between_tags(neuron_models_cu_path, replace_str)

        model_name_index = "i_" + neuron.get_name() + "_model"
        model_name = neuron.get_name()
        n_ports = len(neuron.get_spike_input_ports())
        code_block = "\n" \
                     f"else if (model_name == neuron_model_name[{model_name_index}]) {{\n" \
                     f"    n_port = {n_ports};\n" \
                     f"    {model_name} *{model_name}_group = new {model_name};\n" \
                     f"    node_vect_.push_back({model_name}_group);\n" \
                     " }\n"
        replace_text_between_tags(neuron_models_cu_path, code_block, rfind=True)

    def add_files_to_makefile(self, neuron: ASTNeuron):
        """
        Modifies the Makefile in NEST GPU repository to compile the newly generated models.
        """
        cmakelists_path = str(os.path.join(self.nest_gpu_path, "src", "CMakeLists.txt"))
        shutil.copy(cmakelists_path, cmakelists_path + ".bak")

        code_block = "\n" \
                     f"    {neuron.get_name()}.h\n" \
                     f"    {neuron.get_name()}.cu\n"
                    #  f"    {neuron.get_name()}_kernel.h\n" \
                    #  f"    {neuron.get_name()}_rk5.h\n" \
        replace_text_between_tags(cmakelists_path, code_block,
                                  begin_tag="# <<BEGIN_NESTML_GENERATED>>",
                                  end_tag="# <<END_NESTML_GENERATED>>")

    def add_model_header_to_rk5_interface(self, neuron: ASTNeuron):
        """
        Modifies the rk5_interface.h header file to add the model rk5 header file. This is only for 
        neuron models with a numeric solver.
        """
        rk5_interface_path = str(os.path.join(self.nest_gpu_path, "src", "rk5_interface.h"))
        shutil.copy(rk5_interface_path, rk5_interface_path + ".bak")

        code_block = f"#include \"{neuron.get_name()}_rk5.h\""

        replace_text_between_tags(rk5_interface_path, code_block)

    def _get_neuron_model_namespace(self, astnode: ASTNeuronOrSynapse) -> Dict:
        namespace = super()._get_neuron_model_namespace(astnode)
        if namespace["uses_numeric_solver"]:
            namespace["printer"] = self._gsl_printer
        
        return namespace
