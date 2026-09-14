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
from typing import Dict, Sequence, Optional, Mapping, Any, List, override, Iterable

import glob
import os
import shutil

from pynestml.codegeneration.code_generator_utils import CodeGeneratorUtils
from pynestml.codegeneration.nest_gpu_code_generator_utils import NESTGPUCodeGeneratorUtils
from pynestml.codegeneration.printers.c_simple_expression_printer import CSimpleExpressionPrinter
from pynestml.codegeneration.printers.cpp_printer import CppPrinter
from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.codegeneration.printers.nest_gpu_function_call_printer import NESTGPUFunctionCallPrinter
from pynestml.codegeneration.printers.nest_gpu_numeric_function_call_printer import NESTGPUNumericFunctionPrinter
from pynestml.codegeneration.printers.nest_gpu_numeric_variable_printer import NESTGPUNumericVariablePrinter
from pynestml.codegeneration.printers.nest_gpu_variable_printer import NESTGPUVariablePrinter
from pynestml.codegeneration.printers.unitless_c_simple_expression_printer import UnitlessCSimpleExpressionPrinter
from pynestml.meta_model.ast_model import ASTModel
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.frontend.frontend_configuration import FrontendConfiguration


class NESTGPUCodeGenerator(NESTCodeGenerator):
    """
    A code generator for NEST GPU target
    """

    _default_options = {
        "preserve_expressions": False,
        "simplify_expression": "sympy.logcombine(sympy.powsimp(sympy.expand(expr)))",
        "neuron_models": [],
        "neuron_synapse_pairs": [],
        "synapse_models": [],
        "templates": {
            "path": "resources_nest_gpu/point_neuron",
            "model_templates": {
                "neuron": ["@NEURON_NAME@.cu.jinja2", "@NEURON_NAME@.h.jinja2"],
                "synapse": ["@SYNAPSE_NAME@.cu.jinja2", "@SYNAPSE_NAME@.h.jinja2"]
            },
            "module_templates": []
        },
        "weight_variable": {},
        "solver": "analytic",
        "numeric_solver": "rk45",
        "nest_gpu_path": None
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(NESTCodeGenerator, self).__init__(
            NESTGPUCodeGenerator._default_options.update(options if options else {}))
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

    def setup_printers(self):
        super().setup_printers()

        # Printer with origin
        self._nest_variable_printer = NESTGPUVariablePrinter(expression_printer=None, with_origin=True,
                                                             is_synapse=False)
        self._nest_function_call_printer = NESTGPUFunctionCallPrinter(None)
        self._printer = CppExpressionPrinter(simple_expression_printer=CSimpleExpressionPrinter(
            variable_printer=self._nest_variable_printer,
            constant_printer=self._constant_printer,
            function_call_printer=self._nest_function_call_printer))
        self._nest_variable_printer._expression_printer = self._printer
        self._nest_function_call_printer._expression_printer = self._printer
        self._nest_printer = CppPrinter(expression_printer=self._printer)

        # Printer without origin
        self._nest_variable_printer_no_origin = NESTGPUVariablePrinter(None, with_origin=False,
                                                                       is_synapse=False)
        self._nest_function_call_printer_no_origin = NESTGPUFunctionCallPrinter(None)
        self._printer_no_origin = CppExpressionPrinter(simple_expression_printer=CSimpleExpressionPrinter(
            variable_printer=self._nest_variable_printer_no_origin,
            constant_printer=self._constant_printer,
            function_call_printer=self._nest_function_call_printer_no_origin))
        self._nest_variable_printer_no_origin._expression_printer = self._printer_no_origin
        self._nest_function_call_printer_no_origin._expression_printer = self._printer_no_origin

        # Printer for numeric solver
        self._gsl_variable_printer = NESTGPUNumericVariablePrinter(None)
        self._gsl_function_call_printer = NESTGPUNumericFunctionPrinter(None)
        self._gsl_printer = CppExpressionPrinter(simple_expression_printer=UnitlessCSimpleExpressionPrinter(
            variable_printer=self._gsl_variable_printer,
            constant_printer=self._constant_printer,
            function_call_printer=self._gsl_function_call_printer))
        self._gsl_function_call_printer._expression_printer = self._gsl_printer

    @override
    def generate_code(self,
                      models: Iterable[ASTModel],
                      metadata: Dict[str, Dict[str, Any]]) -> None:
        models = list(models)
        # remove the co-generated neuron model from the list of neurons
        for neuron_synapse_pair in self.get_option("neuron_synapse_pairs"):
            neuron_name = neuron_synapse_pair["neuron"]

            for synapse_name in neuron_synapse_pair["synapses"].keys():
                cogen_neuron_name = neuron_name + FrontendConfiguration.suffix + "__with_" + synapse_name + FrontendConfiguration.suffix
                cogen_neuron = ASTUtils.find_model_by_name(cogen_neuron_name, models)
                if cogen_neuron:
                    model_index = models.index(cogen_neuron)
                    models.pop(model_index)

        # neurons, synapses = CodeGeneratorUtils.get_model_types_from_names(models, synapse_models=self.get_option("synapse_models"))
        # for synapse in synapses:
        #     synapse_name_stripped = synapse.get_name().split("__with_")[0]
        #     synapse.set_name(synapse_name_stripped)

        super().generate_code(models, metadata)

    @override
    def generate_neuron_code(self, neuron: ASTModel,
                             metadata: Dict[str, Dict[str, Any]]) -> None:
        self._nest_variable_printer.is_synapse = False
        self._nest_variable_printer_no_origin.is_synapse = False

        super().generate_neuron_code(neuron, metadata)

    @override
    def generate_synapse_code(self, synapse: ASTModel,
                              metadata: Dict[str, Dict[str, Any]]) -> None:
        self._nest_variable_printer.is_synapse = True
        self._nest_variable_printer_no_origin.is_synapse = True

        # synapse_name_stripped = synapse.get_name().split("__with_")[0]
        # synapse.set_name(synapse_name_stripped)

        super().generate_synapse_code(synapse, metadata)

    @override
    def generate_module_code(self, neurons: Sequence[ASTModel], synapses: Sequence[ASTModel],
                             metadata: Dict[str, Dict[str, Any]]):
        """
        Modify header and CUDA files for the new models to be recognized
        """
        self.copy_models_from_target_path()
        self.add_model_name_to_neuron_header(neurons)
        self.add_model_to_neuron_class(neurons)
        self.add_files_to_cmakelists(neurons, synapses)
        if synapses:
            self.add_model_to_synapse_header(synapses)
            self.add_model_to_synapse_class(synapses)

    def copy_models_from_target_path(self):
        """Copies all the files related to the neuron model to the NEST GPU src directory"""
        types = ["*.h", "*.cu"]
        dst_path = os.path.join(self.nest_gpu_path, "src")
        for _type in types:
            for file in glob.glob(os.path.join(FrontendConfiguration.get_target_path(), _type)):
                shutil.copy(file, dst_path)

    def add_model_name_to_neuron_header(self, neurons: Sequence[ASTModel]):
        """
        Modifies the ``neuron_models.h`` file to add the newly generated model's header files
        """
        neuron_models_h_path = str(os.path.join(self.nest_gpu_path, "src", "neuron_models.h"))
        shutil.copy(neuron_models_h_path, neuron_models_h_path + ".bak")

        neuron_indexes = []
        neuron_names = []
        for neuron in neurons:
            neuron_indexes.append("\ni_" + neuron.get_name() + "_model,")
            neuron_names.append("\n, \"" + neuron.get_name() + "\"")

        neuron_indexes = "".join(neuron_indexes) + "\n"
        neuron_names = "".join(neuron_names) + "\n"
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(neuron_models_h_path, neuron_indexes)
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(neuron_models_h_path, neuron_names, n=2)

    def add_model_to_neuron_class(self, neurons: Sequence[ASTModel]):
        """
        Modifies the ``neuron_models.cu`` file to add the newly generated model's .cu file
        """
        neuron_models_cu_path = str(os.path.join(self.nest_gpu_path, "src", "neuron_models.cu"))
        shutil.copy(neuron_models_cu_path, neuron_models_cu_path + ".bak")

        include_files = []
        code_blocks = []
        for neuron in neurons:
            include_files.append("\n#include \"" + neuron.get_name() + ".h\"")
            model_name_index = "i_" + neuron.get_name() + "_model"
            model_name = neuron.get_name()
            n_ports = len(neuron.get_spike_input_ports())
            code_blocks.append("\n"
                               f"else if (model_name == neuron_model_name[{model_name_index}]) {{\n"
                               f"    n_ports = {n_ports};\n"
                               f"    {model_name} *{model_name}_group = new {model_name};\n"
                               f"    node_vect_.push_back({model_name}_group);\n"
                               " }")
        include_files = "".join(include_files) + "\n"
        code_blocks = "".join(code_blocks) + "\n"
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(neuron_models_cu_path, include_files)
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(neuron_models_cu_path, code_blocks, n=2)

    def add_model_to_synapse_header(self, synapses: Sequence[ASTModel]):
        """
        Modifies ``syn_model.h`` file to add the newly generated synapse
        """
        syn_model_h_path = str(os.path.join(self.nest_gpu_path, "src", "syn_model.h"))
        shutil.copy(syn_model_h_path, syn_model_h_path + ".bak")

        synapse_indexes = []
        synapse_names = []
        for synapse in synapses:
            synapse_indexes.append("\ni_" + synapse.get_name() + "_model,")
            synapse_names.append("\n, \"" + synapse.get_name() + "\"")

        synapse_indexes = "".join(synapse_indexes) + "\n"
        synapse_names = "".join(synapse_names) + "\n"
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(syn_model_h_path, synapse_indexes)
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(syn_model_h_path, synapse_names, n=2)

    def add_model_to_synapse_class(self, synapses: Sequence[ASTModel]):
        """
        Modifies the ``syn_model.cu`` file to add the code corresponding to the newly generated synapse
        """
        syn_model_cu_path = str(os.path.join(self.nest_gpu_path, "src", "syn_model.cu"))
        shutil.copy(syn_model_cu_path, syn_model_cu_path + ".bak")

        include_files = []
        synapse_create_block = []
        synapse_update_block = []
        pre_trace_update_block = []
        post_trace_update_block = []

        for synapse in synapses:
            synapse_name = synapse.get_name()
            synapse_index = "i_" + synapse.get_name() + "_model"
            include_files.append("\n#include \"" + synapse_name + ".h\"")
            synapse_create_block.append("\n"
                                        f" else if ( model_name == syn_model_name[ {synapse_index} ] )\n"
                                        f" {{\n"
                                        f" {synapse_name}* {synapse_name}_group = new {synapse_name};\n"
                                        f" syn_group_vect_.push_back( {synapse_name}_group );\n"
                                        f" }}")
            pre_trace_update_block.append("\n"
                                          f"case {synapse_index}:\n"
                                          f"  {synapse_name}_ns::{synapse_name}_PreTraceUpdate(i_conn);\n"
                                          f"  break;\n")
            post_trace_update_block.append("\n"
                                           f"case {synapse_index}:\n"
                                           f"  {synapse_name}_ns::{synapse_name}_PostTraceUpdate(i_conn);\n"
                                           f"  break;\n")
            synapse_update_block.append("\n"
                                        f"case {synapse_index}:\n"
                                        f"  {synapse_name}_ns::{synapse_name}_Update( w, Dt, param, i_conn );\n"
                                        f"  break;")
        include_files = "".join(include_files) + "\n"
        synapse_create_block = "".join(synapse_create_block) + "\n"
        pre_trace_update_block = "".join(pre_trace_update_block) + "\n"
        post_trace_update_block = "".join(post_trace_update_block) + "\n"
        synapse_update_block = "".join(synapse_update_block) + "\n"

        NESTGPUCodeGeneratorUtils.replace_text_between_tags(syn_model_cu_path, include_files)
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(syn_model_cu_path, synapse_update_block, n=2)
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(syn_model_cu_path, pre_trace_update_block, n=3)
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(syn_model_cu_path, post_trace_update_block, n=4)
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(syn_model_cu_path, synapse_create_block, n=5)

    def add_files_to_cmakelists(self, neurons: Sequence[ASTModel], synapses: Sequence[ASTModel]):
        """
        Modifies the CMakeLists file in NEST GPU repository to compile the newly generated models.
        """
        cmakelists_path = str(os.path.join(self.nest_gpu_path, "src", "CMakeLists.txt"))
        shutil.copy(cmakelists_path, cmakelists_path + ".bak")

        gen_files = []
        for neuron in neurons:
            gen_files.append("\n"
                             f"    {neuron.get_name()}.h\n"
                             f"    {neuron.get_name()}.cu\n")
        for synapse in synapses:
            gen_files.append("\n"
                             f"    {synapse.get_name()}.h\n"
                             f"    {synapse.get_name()}.cu\n")
        gen_files = "".join(gen_files) + "\n"
        NESTGPUCodeGeneratorUtils.replace_text_between_tags(cmakelists_path, gen_files,
                                                            begin_tag="# <<BEGIN_NESTML_GENERATED>>",
                                                            end_tag="# <<END_NESTML_GENERATED>>")

    def _get_neuron_model_namespace(self, neuron: ASTModel, metadata: Dict[str, Dict[str, Any]]) -> Dict:
        namespace = super()._get_neuron_model_namespace(neuron, metadata)
        # neuron_name_stripped = neuron.get_name().split("__with_")[0]
        # namespace["neuronName"] = neuron_name_stripped
        if namespace["uses_numeric_solver"]:
            namespace["printer"] = self._gsl_printer
            namespace["uses_analytic_solver"] = False

        return namespace

    def _get_synapse_model_namespace(self,
                                     synapse: ASTModel,
                                     metadata: Dict[str, Dict[str, Any]]) -> Dict:
        namespace = super()._get_synapse_model_namespace(synapse, metadata)
        # synapse_name_stripped = synapse.get_name().split("__with_")[0]
        # namespace["synapseName"] = synapse_name_stripped
        #
        # synapse.set_name(synapse_name_stripped)

        # Get pre- and post- onReceive block statements
        pre_spike_weight_stmts, pre_spike_block_stmts = ASTUtils.separate_stmts_with_weight_var_from_on_receive_block(
            synapse, namespace["pre_ports"], namespace["synapse_weight_variable"])
        post_spike_weight_stmts, post_spike_block_stmts = ASTUtils.separate_stmts_with_weight_var_from_on_receive_block(
            synapse, namespace["post_ports"], namespace["synapse_weight_variable"])

        namespace["pre_spike_weight_stmts"] = pre_spike_weight_stmts
        namespace["pre_spike_block_stmts"] = pre_spike_block_stmts

        namespace["post_spike_weight_stmts"] = post_spike_weight_stmts
        namespace["post_spike_block_stmts"] = post_spike_block_stmts

        return namespace
