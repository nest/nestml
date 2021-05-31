# -*- coding: utf-8 -*-
#
# syns_processing.py
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

from collections import defaultdict
import copy

from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor
from build.lib.pynestml.meta_model.ast_kernel import ASTKernel


class SynsProcessing(object):
    padding_character = "_"
    #syns_expression_prefix = "I_SYN_"
    tau_sring = "tau"
    equilibrium_string = "e"
    
    # used to keep track of whenever check_co_co was already called
    # see inside check_co_co
    first_time_run = True
    # stores syns_info from the first call of check_co_co
    syns_info = defaultdict()
    
    def __init__(self, params):
        '''
        Constructor
        '''
    # @classmethod    
    # def extract_synapse_name(cls, name: str) -> str: 
    #     return name   
    #     #return name[len(cls.syns_expression_prefix):].strip(cls.padding_character)
    #

    """
    returns
    
    {
        "AMPA":
        {
            "inline_expression": ASTInlineExpression,
            "parameters_used": 
            {
                "e_AMPA": ASTDeclaration,
                "tau_syn_AMPA": ASTDeclaration
            }
            "kernels":
            {
                "g_ex": 
                {
                    "ASTKernel": ASTKernel,
                    "spike_source": str,
                }
            }
                
        },
        "GABA":
        {
            ...
        }
        ...
    }
    """
    @classmethod
    def detectSyns(cls, neuron):
        # search for synapse_inline expressions inside equations block
        info_collector = ASTSynapseInformationCollector()
        neuron.accept(info_collector)
        
        syns_info = defaultdict()
            
        synapse_inlines = info_collector.get_inline_expressions_with_kernels()
        for synapse_inline in synapse_inlines:

            synapse_name = synapse_inline.variable_name
            syns_info[synapse_name] = {
                "inline_expression": synapse_inline,
                "parameters_used": info_collector.get_synapse_specific_parameter_declarations(synapse_inline),
                "kernels":{}
                }
        
            kernel_arg_pairs = info_collector.get_extracted_kernel_args(synapse_inline)
            for kernel_var, spikes_var in kernel_arg_pairs:
                kernel_name = kernel_var.get_name()
                syns_info[synapse_name]["kernels"][kernel_name] = {
                    "ASTKernel": info_collector.get_kernel_by_name(kernel_name),
                    "spike_source": spikes_var.get_name()
                }
        
        return syns_info
        
        
        
        
        # inline_expressions_dict = inline_expressions_inside_equations_block_collector_visitor.inline_expressions_to_variables
        #
        # is_compartmental_model = cls.is_compartmental_model(neuron)
        #
        # # filter for cm_p_open_{channelType}
        # relevant_inline_expressions_to_variables = defaultdict(lambda:list())
        # for expression, variables in inline_expressions_dict.items():
        #     inline_expression_name = expression.variable_name
        #     if inline_expression_name.startswith(cls.inline_expression_prefix):
        #         relevant_inline_expressions_to_variables[expression] = variables
        #
        # #create info structure
        # cm_info = defaultdict()        
        # for inline_expression, inner_variables in relevant_inline_expressions_to_variables.items():
        #     info = defaultdict()
        #     channel_name = cls.cm_expression_to_channel_name(inline_expression)
        #     info["ASTInlineExpression"] = inline_expression
        #     info["inner_variables"] = inner_variables
        #     cm_info[channel_name] = info
        # neuron.is_compartmental_model = is_compartmental_model
        # return cm_info

    @classmethod
    def get_syns_info(cls, neuron: ASTNeuron):
        """
        Checks if this synapse conditions apply for the handed over neuron. 
        If yes, it checks the presence of expected kernels, inlines and declarations.
        In addition it organizes and builds a dictionary (syns_info) 
        which describes all the relevant data that was found
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """
                
        return cls.syns_info

    
    @classmethod
    def check_co_co(cls, neuron: ASTNeuron):
        """
        Checks if synapse conditions apply for the handed over neuron. 
        Models which do not have a state variable named as specified 
        in the value of cm_trigger_variable_name are not relevant
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """
        
        # make sure we only run this a single time
        # subsequent calls will be after AST has been transformed
        # and there would be no kernels or inlines any more
        if cls.first_time_run:
            cls.syns_info = cls.detectSyns(neuron)
            cls.first_time_run = False
        
        # # further computation not necessary if there were no cm neurons
        # if not cm_info: return True   
        #
        # cm_info = cls.calcExpectedFunctionNamesForChannels(cm_info)
        # cm_info = cls.checkAndFindFunctions(neuron, cm_info)
        # cm_info = cls.addChannelVariablesSectionAndEnforceProperVariableNames(neuron, cm_info)
        #
        # # now check for existence of expected state variables 
        # # and add their ASTVariable objects to cm_info
        # missing_states_visitor = StateMissingVisitor(cm_info)
        # neuron.accept(missing_states_visitor)
    
    
"""
for each inline expression inside the equations block,
collect all ASTVariables that are present inside
"""
class ASTSynapseInformationCollector(ASTVisitor):

    def __init__(self):
        super(ASTSynapseInformationCollector, self).__init__()
        self.kernel_name_to_kernel = defaultdict()
        self.inline_expression_to_kernel_args = defaultdict(lambda:set())
        self.parameter_name_to_declaration = defaultdict()
        self.state_name_to_declaration = defaultdict()
        self.inline_expression_to_variables = defaultdict(lambda:set())
        self.kernel_to_rhs_variables = defaultdict(lambda:set())
        
        self.inside_parameter_block = False
        self.inside_state_block = False
        self.inside_equations_block = False
        self.inside_inline_expression = False
        self.inside_kernel = False
        self.inside_kernel_call = False
        self.inside_declaration = False
        # self.inside_variable = False
        self.inside_simple_expression = False
        self.inside_expression = False
        # self.inside_function_call = False
        
        self.current_inline_expression = None
        self.current_kernel = None
        # self.current_variable = None
        
        self.current_synapse_name = None
        
    def get_kernel_by_name(self, name: str):
        return self.kernel_name_to_kernel[name]
    
    def get_inline_expressions_with_kernels (self):
        return self.inline_expression_to_kernel_args.keys()
    
    def get_synapse_specific_parameter_declarations (self, synapse_inline: ASTInlineExpression) -> str:
        # find all variables used in the inline
        potential_parameters = self.inline_expression_to_variables[synapse_inline]
        
        # find all kernels referenced by the inline 
        # and collect variables used by those kernels
        kernel_arg_pairs = self.get_extracted_kernel_args(synapse_inline)
        for kernel_var, spikes_var in kernel_arg_pairs:
            kernel = self.get_kernel_by_name(kernel_var.get_name())
            potential_parameters.update(self.kernel_to_rhs_variables[kernel])
        
        # transform variables into their names and filter 
        # out ones that are available to every synapse
        param_names = set()    
        for potential_parameter in potential_parameters:
            param_name = potential_parameter.get_name() 
            if param_name not in ("t", "v_comp"):
                param_names.add(param_name)
                
        # now match those parameter names with 
        # variable declarations form the parameter block
        dereferenced = defaultdict()
        for param_name in param_names:
            if param_name in self.parameter_name_to_declaration:
                dereferenced[param_name] = self.parameter_name_to_declaration[param_name]
        return dereferenced    

    def get_extracted_kernel_args (self, inline_expression: ASTInlineExpression) -> set:
        return self.inline_expression_to_kernel_args[inline_expression]
    
    def get_used_kernel_names (self, inline_expression: ASTInlineExpression):
        return [kernel_var.get_name() for kernel_var, _ in self.get_extracted_kernel_args(inline_expression)]
        
    def get_used_spike_names (self, inline_expression: ASTInlineExpression):
        return [spikes_var.get_name() for _, spikes_var in self.get_extracted_kernel_args(inline_expression)]
        
    def visit_kernel(self, node):
        self.current_kernel = node
        self.inside_kernel = True
        if self.inside_equations_block:
            kernel_name = node.get_variables()[0].get_name_of_lhs()
            self.kernel_name_to_kernel[kernel_name]=node
            
    def visit_function_call(self, node):
        if self.inside_equations_block and self.inside_inline_expression \
        and self.inside_simple_expression:
            if node.get_name() == "convolve":
                self.inside_kernel_call = True
                kernel, spikes = node.get_args()
                kernel_var = kernel.get_variables()[0]
                spikes_var = spikes.get_variables()[0]
                self.inline_expression_to_kernel_args[self.current_inline_expression].add((kernel_var, spikes_var))
        
    def endvisit_function_call(self, node):
        self.inside_kernel_call = False   
        
    def endvisit_kernel(self, node):
        self.current_kernel = None
        self.inside_kernel = False

    def visit_variable(self, node):
        if self.inside_inline_expression and not self.inside_kernel_call:
            self.inline_expression_to_variables[self.current_inline_expression].add(node)
        elif self.inside_kernel and (self.inside_expression or self.inside_simple_expression):
            self.kernel_to_rhs_variables[self.current_kernel].add(node)    
                
    def visit_inline_expression(self, node):
        self.inside_inline_expression = True
        self.current_inline_expression = node
        
    def endvisit_inline_expression(self, node):
        self.inside_inline_expression = False
        self.current_inline_expression = None
        
    def visit_equations_block(self, node):
        self.inside_equations_block = True
    
    def endvisit_equations_block(self, node):
        self.inside_equations_block = False
    
    def visit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = True
        if node.is_parameters: 
            self.inside_parameter_block = True

    def endvisit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = False
        if node.is_parameters: 
            self.inside_parameter_block = False
                
    def visit_simple_expression(self, node):
        self.inside_simple_expression = True
    
    def endvisit_simple_expression(self, node):
        self.inside_simple_expression = False
        
    def visit_declaration(self, node):
        self.inside_declaration = True
        
        if self.inside_parameter_block:
            self.parameter_name_to_declaration[node.get_variables()[0].get_name()] = node
        elif self.inside_state_block:
            variable_name = node.get_variables()[0].get_name()
            self.state_name_to_declaration[variable_name] = node
    
    def endvisit_declaration(self, node):
        self.inside_declaration = False
        
    def visit_expression(self, node):
        self.inside_expression = True
    
    def endvisit_expression(self, node):
        self.inside_expression = False    
        
                    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    