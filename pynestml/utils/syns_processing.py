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

from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.utils.ast_synapse_information_collector import ASTSynapseInformationCollector
from pynestml.utils.messages import Messages
from pynestml.utils.logger import Logger, LoggingLevel


class SynsProcessing(object):
    padding_character = "_"
    #syns_expression_prefix = "I_SYN_"
    tau_sring = "tau"
    equilibrium_string = "e"
    
    # used to keep track of whenever check_co_co was already called
    # see inside check_co_co
    first_time_run = defaultdict(lambda: True)
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
            },
            "states_used": 
            {
                "v_comp": ASTDeclaration,
            },
            "internals_used_declared":
            {
                "td": ASTDeclaration,
                "g_norm_exc": ASTDeclaration,
            },
            "total_used_declared": {"e_AMPA", ..., "v_comp", ..., "td", ...}
            ,
            "convolutions":
            {
                "g_ex_AMPA__X__b_spikes": 
                {
                    "kernel": 
                    {
                        "name": "g_ex_AMPA",
                        "ASTKernel": ASTKernel
                    },
                    "spikes": 
                    {
                        "name": "b_spikes",
                        "ASTInputPort": ASTInputPort
                    },
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
                "states_used": info_collector.get_synapse_specific_state_declarations(synapse_inline),
                "internals_used_declared": info_collector.get_synapse_specific_internal_declarations(synapse_inline), 
                "total_used_declared": info_collector.get_variable_names_of_synapse(synapse_inline),
                "convolutions":{}
                }
        
            kernel_arg_pairs = info_collector.get_extracted_kernel_args(synapse_inline)
            for kernel_var, spikes_var in kernel_arg_pairs:
                kernel_name = kernel_var.get_name()
                spikes_name = spikes_var.get_name()
                convolution_name = info_collector.construct_kernel_X_spike_buf_name(kernel_name, spikes_name, 0)
                syns_info[synapse_name]["convolutions"][convolution_name] = {
                    "kernel": {
                        "name": kernel_name,
                        "ASTKernel": info_collector.get_kernel_by_name(kernel_name),
                    },
                    "spikes": {
                        "name": spikes_name,
                        "ASTInputPort": info_collector.get_input_port_by_name(spikes_name),
                    },
                }
        
        return syns_info, info_collector

    """
    input:
    {
        "AMPA":
        {
            "inline_expression": ASTInlineExpression,
            "parameters_used": 
            {
                "e_AMPA": ASTDeclaration,
                "tau_syn_AMPA": ASTDeclaration
            },
            "states_used": 
            {
                "v_comp": ASTDeclaration,
            },            
            "internals_used_declared":
            {
                "td": ASTDeclaration,
                "g_norm_exc": ASTDeclaration,
            },
            "total_used_declared": {"e_AMPA", ..., "v_comp", ..., "td", ...}
            ,
            "convolutions":
            {
                "g_ex_AMPA__X__b_spikes": 
                {
                    "kernel": 
                    {
                        "name": "g_ex_AMPA",
                        "ASTKernel": ASTKernel
                    },
                    "spikes": 
                    {
                        "name": "b_spikes",
                        "ASTInputPort": ASTInputPort
                    },
                }
            }
                
        },
        "GABA":
        {
            ...
        }
        ...
    }
    
    output:    
    {
        "AMPA":
        {
            "inline_expression": ASTInlineExpression,
            "buffers_used": {"b_spikes"},
            "parameters_used": 
            {
                "e_AMPA": ASTDeclaration,
                "tau_syn_AMPA": ASTDeclaration
            },
            "states_used": 
            {
                "v_comp": ASTDeclaration,
            },            
            "internals_used_declared":
            {
                "td": ASTDeclaration,
                "g_norm_exc": ASTDeclaration,
            },
            "total_used_declared": {"e_AMPA", ..., "v_comp", ..., "td", ...}
            ,
            "convolutions":
            {
                "g_ex_AMPA__X__b_spikes": 
                {
                    "kernel": 
                    {
                        "name": "g_ex_AMPA",
                        "ASTKernel": ASTKernel
                    },
                    "spikes": 
                    {
                        "name": "b_spikes",
                        "ASTInputPort": ASTInputPort
                    },
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
    def collect_and_check_inputs_per_synapse(cls, neuron: ASTNeuron, info_collector: ASTSynapseInformationCollector, syns_info: dict):
        new_syns_info = copy.copy(syns_info)
        
        # collect all buffers used
        for synapse_name, synapse_info in syns_info.items():
            new_syns_info[synapse_name]["buffers_used"] = set()
            for convolution_name, convolution_info in synapse_info["convolutions"].items():
                input_name = convolution_info["spikes"]["name"]
                new_syns_info[synapse_name]["buffers_used"].add(input_name)

        # now make sure each synapse is using exactly one buffer
        for synapse_name, synapse_info in syns_info.items():
            buffers = new_syns_info[synapse_name]["buffers_used"]
            if len(buffers) != 1:
                code, message = Messages.get_syns_bad_buffer_count(buffers, synapse_name)
                causing_object = synapse_info["inline_expression"]
                Logger.log_message(code=code, message=message, error_position=causing_object.get_source_position(), log_level=LoggingLevel.ERROR, node=causing_object)
        
        return new_syns_info        


    @classmethod
    def get_syns_info(cls, neuron: ASTNeuron):
        """
        returns previously generated syns_info
        :param neuron: a single neuron instance.
        :type neuron: ASTNeuron
        """
  
        return copy.copy(cls.syns_info[neuron])

    
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
        if cls.first_time_run[neuron]:
            syns_info, info_collector = cls.detectSyns(neuron)
            syns_info = cls.collect_and_check_inputs_per_synapse(neuron, info_collector, syns_info)
            cls.syns_info[neuron] = syns_info
            cls.first_time_run[neuron] = False
        

    
    

        
        

                    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    