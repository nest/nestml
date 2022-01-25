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
from pynestml.codegeneration.ast_transformers import ASTTransformers
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_node import ASTNode
from pynestml.codegeneration.nest_codegenerator import NESTCodeGenerator
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_synapse import ASTSynapse
from jinja2 import Environment, FileSystemLoader
import os
import copy
import textwrap


class NestCppPrinter:
    def __init__(self, node: ASTNode):
        if node.get_scope() is None:
            from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
            visitor = ASTSymbolTableVisitor()
            visitor.handle(node)
        if FrontendConfiguration.logging_level is None:
            FrontendConfiguration.logging_level = 'ERROR'
        code_generator = NESTCodeGenerator()
        if isinstance(node, ASTNeuron):
            code_generator.analyse_transform_neurons([node])
            self.namespace = code_generator._get_neuron_model_namespace(node)
        elif isinstance(node, ASTSynapse):
            code_generator.analyse_transform_synapses([node])
            self.namespace = code_generator._get_synapse_model_namespace(node)
        else:
            raise TypeError(
                "The parameter node must be an instance of one the following sub-classes: [ASTNeuron, ASTSynapse]")
        self.node = node

        templates_root = os.path.join(pynestml.__path__[0], "codegeneration", "resources_nest", "point_neuron")
        directives = os.path.join(templates_root, "directives")

        loader = FileSystemLoader(templates_root)
        self.env = Environment(loader=loader)
        self.env.loader.searchpath.append(directives)

        self.env.globals["is_delta_kernel"] = ASTTransformers.is_delta_kernel

    def get_template(self, template_name):
        template = self.env.get_template(f"{template_name}.jinja2")
        return template

    def print_function(self, func: ASTFunction, func_namespace=None):
        if func_namespace is None:
            func_namespace = "toRemove"
            output = self.namespace["printer"].print_function_definition(func, func_namespace)
            output = output.replace("toRemove::", "")
        else:
            output = self.namespace["printer"].print_function_definition(func, func_namespace)
        output += "{"

        ast = copy.deepcopy(self.namespace.get("ast", None))
        self.namespace["ast"] = func.get_block()

        block_template = self.get_template("Block")
        function_body = block_template.render(self.namespace)
        # reset to original value
        self.namespace["ast"] = ast
        padding = 2 * ' '
        padded_function_body = textwrap.indent(function_body, padding)

        output += padded_function_body
        output += "\n}"

        return output

    def print_declaration(self, declaration: ASTDeclaration):
        declaration_template = self.get_template("Declaration")
        ast = copy.deepcopy(self.namespace.get("ast", None))
        self.namespace["ast"] = declaration
        cpp_declaration = declaration_template.render(self.namespace)
        # reset to original value
        self.namespace["ast"] = ast
        return cpp_declaration

    def print_functions(self, namespace=None):
        functions = self.node.get_functions()
        outputs = {}
        for func in functions:
            name = func.get_name()
            output = self.print_function(func, namespace)
            outputs[name] = output
        return outputs

    def print_declarations(self, ast_block):
        declarations = ast_block.get_declarations()
        outputs = {}
        for declaration in declarations:
            variables = declaration.get_variables()
            names = tuple([v.name for v in variables])
            printed_declaration = self.print_declaration(declaration)
            outputs[names] = printed_declaration
        return outputs

    def print_struct(self, struct_template_name, include_instance=True):
        struct_template = self.get_template(struct_template_name)
        cpp_struct = struct_template.render(self.namespace)
        return cpp_struct

    def print_struct_instance(self, struct_type):
        accepted_structs = ["State", "Parameters", "Variables"]
        if struct_type in accepted_structs:
            type_name = f"{struct_type}_"
            instance_name = f"{type_name[0]}_"
            instance_declaration = f"{type_name} {instance_name};"
            return instance_declaration
        else:
            raise TypeError(f"struct_type must be in {accepted_structs}")

    def print_state_struct(self, include_instance=True):
        return self.print_struct("StateStruct", include_instance)

    def print_parameters_struct(self, include_instance=True):
        return self.print_struct("ParametersStruct", include_instance)

    def print_internal_struct(self, include_instance=True):
        return self.print_struct("VariablesStruct", include_instance)

    def print_block_getter_setter(self, block_template_name):
        block_template = self.get_template(block_template_name)
        cpp_getter_setter_block = block_template.render(self.namespace)
        return cpp_getter_setter_block

    def print_state_getter_setter(self):
        return self.print_block_getter_setter("StateGetterAndSetter")

    def print_parameters_getter_setter(self):
        return self.print_block_getter_setter("ParametersGetterAndSetter")

    def print_internals_getter_setter(self):
        return self.print_block_getter_setter("InternalsGetterAndSetter")

    def print_getter_setter(self, blocks_name=None):
        accepted_blocks_name = ["State", "Parameters", "Internals"]
        output = ""
        if blocks_name is None:
            for block_name in accepted_blocks_name:
                template_name = f"{block_name}GetterAndSetter"
                output += self.print_block_getter_setter(template_name)
                output += "\n"
            return output
        else:
            if all(x in accepted_blocks_name for x in blocks_name):
                for block_name in blocks_name:
                    template_name = f"{block_name}GetterAndSetter"
                    output += self.print_block_getter_setter(template_name)
                    output += "\n"
                return output
            else:
                raise ValueError(f"blocks_name must be either None or in {accepted_blocks_name}")

    def print_default_constructorBody(self):
        default_constructor_template = self.get_template("DefaultConstructorBody")
        return default_constructor_template.render(self.namespace)
