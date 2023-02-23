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
import os
import re
import shutil
from typing import Sequence, Optional, Mapping, Any
from pynestml.codegeneration.nest_code_generator import NESTCodeGenerator
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.meta_model.ast_neuron import ASTNeuron


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
            "path": os.path.join(os.path.dirname(__file__), "resources_nest_gpu"),
            "model_templates": {
                "neuron": ["@NEURON_NAME@.cu.jinja2", "@NEURON_NAME@.h.jinja2",
                           "@NEURON_NAME@_kernel.h.jinja2", "@NEURON_NAME@_rk5.h.jinja2"],
            },
            "module_templates": [""]
        }
    }

    def __init__(self, options: Optional[Mapping[str, Any]] = None):
        super(NESTCodeGenerator, self).__init__("nest_gpu",
                                                NESTGPUCodeGenerator._default_options.update(options if options else {}))
        self._target = "NEST_GPU"
        self.setup_template_env()
        # TODO: setup the printers and reference converters

    def generate_neuron_code(self, neuron: ASTNeuron) -> None:
        """
        Overrides the function to generate model files for GPU target
        :param neuron:
        :return:
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())

        for _model_templ in self._model_templates["neuron"]:
            file_extension = _model_templ.filename.split(".")[-2]
            _file = _model_templ.render(self._get_neuron_model_namespace(neuron))
            suffix = ""
            if "kernel" in _model_templ.filename:
                suffix = "_kernel"
            elif "rk5" in _model_templ.filename:
                suffix = "_rk5"
            filename = str(os.path.join(FrontendConfiguration.get_target_path(),
                                        neuron.get_name())) + suffix + "." + file_extension
            with open(filename, "w+") as f:
                f.write(str(_file))

    def generate_module_code(self, neurons: Sequence[ASTNeuron], synapses: Sequence[ASTSynapse]):
        """
        Modify some header and CUDA files for the new models to be recognized
        """
        for neuron in neurons:
            self.add_model_name_to_neuron_header(neuron)
            self.add_model_to_neuron_class(neuron)
            self.add_files_to_makefile(neuron)

    def add_model_name_to_neuron_header(self, neuron: ASTNeuron):
        """
        Modifies the ``neuron_models.h`` file to add the newly generated model's header files
        """
        neuron_models_h_path = str(os.path.join(FrontendConfiguration.get_target_path(), "neuron_models.h"))
        shutil.copy(neuron_models_h_path, neuron_models_h_path + ".bak")
        with open(neuron_models_h_path, "r") as f:
            file_str = f.read()

        pos = file_str.find("N_NEURON_MODELS")
        file_str = file_str[:pos] + "i_" + neuron.get_name() + "_model," + file_str[pos:]

        pos = file_str.rfind("};")
        file_str = file_str[:pos] + ", \"" + neuron.get_name() + "\"" + file_str[pos:]

        with open(neuron_models_h_path, "w") as f:
            f.write(file_str)

    def add_model_to_neuron_class(self, neuron: ASTNeuron):
        """
        Modifies the ``neuron_models.cu`` file to add the newly generated model's .cu file
        """
        neuron_models_cu_path = str(os.path.join(FrontendConfiguration.get_target_path(), "neuron_models.cu"))
        shutil.copy(neuron_models_cu_path, neuron_models_cu_path + ".bak")

        with open(neuron_models_cu_path, "r") as f:
            file_str = f.read()

        itr = re.finditer(r"#include \"[[a-zA-Z_][a-zA-Z0-9_]*.h\"", file_str)
        start_pos, end_pos = [(m.start(0), m.end(0)) for m in itr][-1]
        file_str = file_str[:end_pos + 1] + "#include \"" + neuron.get_name() + ".h\"" + file_str[end_pos:]

        model_name_index = "i_" + neuron.get_name() + "_model"
        model_name = neuron.get_name()
        code_block = f"else if (model_name == neuron_model_name[{model_name_index}]) {{\n" \
                     f"    {model_name} *{model_name}_group = new {model_name};\n" \
                     f"    node_vect_.push_back({model_name}_group);\n" \
                     " }\n"
        itr = re.finditer(r"else {\n\s+throw ngpu_exception", file_str)
        pos = [m.start(0) for m in itr][-1]
        file_str = file_str[:pos] + code_block + file_str[pos:]

        with open(neuron_models_cu_path, "w") as f:
            f.write(file_str)

    def add_files_to_makefile(self, neuron: ASTNeuron):
        """
        Modifies the Makefile in NEST GPU repository to compile the newly generated models.
        """
        makefile_path = str(os.path.join(os.path.dirname(FrontendConfiguration.get_target_path()), "Makefile.am"))
        shutil.copy(makefile_path, makefile_path + ".bak")

        with open(makefile_path, "r") as f:
            file_str = f.read()

        pos = file_str.find("ngpu_src_files")
        code_block = " \\\n" \
                     f"$(top_srcdir)/src/{neuron.get_name()}.h \\\n" \
                     f"$(top_srcdir)/src/{neuron.get_name()}_kernel.h \\\n" \
                     f"$(top_srcdir)/src/{neuron.get_name()}_rk5.h\n\n"
        file_str = file_str[:pos - 2] + code_block + file_str[pos:]

        pos = file_str.find("COMPILER_FLAGS")
        code_block = " \\\n" \
                     f"$(top_srcdir)/src/{neuron.get_name()}.cu\n\n"
        file_str = file_str[:pos - 2] + code_block + file_str[pos:]

        with open(makefile_path, "w") as f:
            f.write(file_str)
