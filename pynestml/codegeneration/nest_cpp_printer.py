# -*- coding: utf-8 -*-
#
# nest_cpp_printer.py
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



from typing import Any, List, Mapping, Optional, Sequence
import pynestml
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_node import ASTNode
from pynestml.codegeneration.nest_codegenerator import NESTCodeGenerator
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from jinja2 import Environment, Template, FileSystemLoader
import os
import copy
import textwrap


class NestCppPrinter:
    def __init__(self, node: ASTNode):
        if node.get_scope() is None:
            from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
            visitor = ASTSymbolTableVisitor()
            visitor.handle(node)

        code_generator = NESTCodeGenerator()
        if isinstance(node, ASTNeuron):
            code_generator.analyse_transform_neurons([node])
            self.namespace = code_generator._get_neuron_model_namespace(node)
        elif isinstance(node, ASTSynapse):
            code_generator.analyse_transform_synapses([node])
            self.namespace = code_generator._NESTCodeGenerator_get_synapse_model_namespace(node)
        else:
            raise TypeError(
                "The parameter node must be an instance of one the following sub-classes: [ASTNeuron, ASTSynapse]")
        self.node = node

    def print_function(self, func : ASTFunction, func_namespace=""):
        output = self.namespace["printer"].print_function_definition(func, func_namespace)
        output += "{"

        templates_root = os.path.join(pynestml.__path__[0], "codegeneration", "resources_nest", "point_neuron")
        block_template = os.path.join(templates_root, "directives")
        loader = FileSystemLoader(block_template)
        env = Environment(loader=loader)
        block_template = env.get_template("Block.jinja2")

        namespace_copy = copy.deepcopy(self.namespace)
        namespace_copy["ast"] = func.get_block()

        env.loader.searchpath.append(templates_root)
        function_body = block_template.render(namespace_copy)
        padding = 2 * ' '
        padded_function_body = textwrap.indent(function_body, padding)

        output += padded_function_body
        output += "\n}"

        return output

    def print_functions(self, namespace=""):
        functions = self.node.get_functions()
        outputs = {}
        for func in functions:
            name = func.get_name()
            output = self.print_function(func, namespace)
            outputs[name] = output
        return outputs
