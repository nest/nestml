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
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.ast_synapse_information_collector import ASTSynapseInformationCollector


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
    
    

        
        

                    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    