"""
for each inline expression inside the equations block,
collect all synapse relevant information

"""
from _collections import defaultdict
import copy

from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTSynapseInformationCollector(ASTVisitor):

    kernel_name_to_kernel = defaultdict()
    inline_expression_to_kernel_args = defaultdict(lambda:set())
    inline_expression_to_function_calls = defaultdict(lambda:set())
    kernel_to_function_calls = defaultdict(lambda:set())
    parameter_name_to_declaration = defaultdict(lambda:None)
    state_name_to_declaration = defaultdict(lambda:None)
    variable_name_to_declaration = defaultdict(lambda:None)
    internal_var_name_to_declaration = defaultdict(lambda:None)
    inline_expression_to_variables = defaultdict(lambda:set())
    kernel_to_rhs_variables = defaultdict(lambda:set())
    declaration_to_rhs_variables = defaultdict(lambda:set())
    
    input_port_name_to_input_port = defaultdict()
        
    def __init__(self):
        super(ASTSynapseInformationCollector, self).__init__()
        
        self.inside_parameter_block = False
        self.inside_state_block = False 
        self.inside_internals_block = False
        self.inside_equations_block = False
        self.inside_input_block = False
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
        self.current_expression = None
        self.current_simple_expression = None
        self.current_declaration = None
        # self.current_variable = None
        
        self.current_synapse_name = None
        
        
    @classmethod
    def get_state_declaration(cls, variable_name):
        return ASTSynapseInformationCollector.state_name_to_declaration[variable_name]
    
    @classmethod
    def get_variable_declaration(cls, variable_name):
        return ASTSynapseInformationCollector.variable_name_to_declaration[variable_name]
        
    @classmethod    
    def get_kernel_by_name(cls, name: str):
        return cls.kernel_name_to_kernel[name]
    
    @classmethod 
    def get_inline_expressions_with_kernels (cls):
        return cls.inline_expression_to_kernel_args.keys()
    
    @classmethod
    def get_kernel_function_calls(cls, kernel: ASTKernel):
        return ASTSynapseInformationCollector.kernel_to_function_calls[kernel]
    
    @classmethod
    def get_inline_function_calls(cls, inline: ASTInlineExpression):
        return ASTSynapseInformationCollector.inline_expression_to_function_calls[inline]
    
    # extracts all variables specific to a single synapse
    # (which is defined by the inline expression containing kernels)
    # independently from what block they are declared in
    # it also cascades over all right hand side variables until all 
    # variables are included
    @classmethod
    def get_variable_names_of_synapse(cls, synapse_inline: ASTInlineExpression, exclude_names: set = set(), exclude_ignorable = True) -> set:
        if exclude_ignorable:
            exclude_names.update(cls.get_variable_names_to_ignore())
        
        # find all variables used in the inline
        potential_variables = cls.inline_expression_to_variables[synapse_inline]
        
        # find all kernels referenced by the inline 
        # and collect variables used by those kernels
        kernel_arg_pairs = ASTSynapseInformationCollector.get_extracted_kernel_args(synapse_inline)
        for kernel_var, spikes_var in kernel_arg_pairs:
            kernel = ASTSynapseInformationCollector.get_kernel_by_name(kernel_var.get_name())
            potential_variables.update(cls.kernel_to_rhs_variables[kernel])
             
        # find declarations for all variables and check
        # what variables their rhs expressions use
        # for example if we have 
        # a = b * c
        # then check if b and c are already in potential_variables
        # if not, add those as well
        potential_variables_copy = copy.copy(potential_variables) 
        
        potential_variables_prev_count = len(potential_variables)
        while True:  
            for potential_variable in potential_variables_copy:
                var_name = potential_variable.get_name() 
                if var_name in exclude_names: continue 
                declaration = cls.get_variable_declaration(var_name)
                if declaration is None: 
                    continue
                variables_referenced = ASTSynapseInformationCollector.declaration_to_rhs_variables[var_name]
                potential_variables.update(variables_referenced)
            if potential_variables_prev_count == len(potential_variables): break
            potential_variables_prev_count = len(potential_variables)    

        # transform variables into their names and filter 
        # out anything form exclude_names
        result = set()    
        for potential_variable in potential_variables:
            var_name = potential_variable.get_name() 
            if var_name not in exclude_names:
                result.add(var_name)  
                
                
        return result
    
    @classmethod
    def get_variable_names_to_ignore(cls):
        return set(PredefinedVariables.get_variables().keys()).union({"v_comp"})
    
    @classmethod 
    def get_synapse_specific_internal_declarations (cls, synapse_inline: ASTInlineExpression) -> defaultdict:
        synapse_variable_names = cls.get_variable_names_of_synapse(synapse_inline)
                
        # now match those variable names with 
        # variable declarations from the internals block
        dereferenced = defaultdict()
        for potential_internals_name in synapse_variable_names:
            if potential_internals_name in cls.internal_var_name_to_declaration:
                dereferenced[potential_internals_name] = cls.internal_var_name_to_declaration[potential_internals_name]
        return dereferenced
    
    @classmethod 
    def get_synapse_specific_state_declarations (cls, synapse_inline: ASTInlineExpression) -> defaultdict:
        synapse_variable_names = cls.get_variable_names_of_synapse(synapse_inline)
                
        # now match those variable names with 
        # variable declarations from the state block
        dereferenced = defaultdict()
        for potential_state_name in synapse_variable_names:
            if potential_state_name in cls.state_name_to_declaration:
                dereferenced[potential_state_name] = cls.state_name_to_declaration[potential_state_name]
        return dereferenced
                
    
    @classmethod 
    def get_synapse_specific_parameter_declarations (cls, synapse_inline: ASTInlineExpression) -> defaultdict:
        synapse_variable_names = cls.get_variable_names_of_synapse(synapse_inline)
                
        # now match those variable names with 
        # variable declarations from the parameter block
        dereferenced = defaultdict()
        for potential_param_name in synapse_variable_names:
            if potential_param_name in cls.parameter_name_to_declaration:
                dereferenced[potential_param_name] = cls.parameter_name_to_declaration[potential_param_name]
        return dereferenced

      
    @classmethod 
    def get_extracted_kernel_args (cls, inline_expression: ASTInlineExpression) -> set:
        return cls.inline_expression_to_kernel_args[inline_expression]
    
    
    """
    for every occurence of convolve(port, spikes) generate "port__X__spikes" variable
    gather those variables for this synapse inline and return their list
    
    note that those variables will occur as substring in other kernel variables
    i.e  "port__X__spikes__d" or "__P__port__X__spikes__port__X__spikes"
    
    so we can use the result to identify all the other kernel variables related to the
    specific synapse inline declaration
    """
    @classmethod
    def get_basic_kernel_variable_names(cls, synapse_inline):
        order = 0
        results = []
        for syn_inline, args in ASTSynapseInformationCollector.inline_expression_to_kernel_args.items():
            if synapse_inline.variable_name == syn_inline.variable_name:
                for kernel_var, spike_var in args:
                    kernel_name = kernel_var.get_name()
                    spike_input_port = ASTSynapseInformationCollector.input_port_name_to_input_port[spike_var.get_name()]
                    kernel_variable_name = ASTSynapseInformationCollector.construct_kernel_X_spike_buf_name(kernel_name, spike_input_port, order)
                    results.append(kernel_variable_name)
            
        return results    

    @classmethod 
    def get_used_kernel_names (cls, inline_expression: ASTInlineExpression):
        return [kernel_var.get_name() for kernel_var, _ in cls.get_extracted_kernel_args(inline_expression)]
    
    @classmethod
    def get_input_port_by_name(cls, name):
        return cls.input_port_name_to_input_port[name]
    
    @classmethod     
    def get_used_spike_names (cls, inline_expression: ASTInlineExpression):
        return [spikes_var.get_name() for _, spikes_var in cls.get_extracted_kernel_args(inline_expression)]
        
    def visit_kernel(self, node):
        self.current_kernel = node
        self.inside_kernel = True
        if self.inside_equations_block:
            kernel_name = node.get_variables()[0].get_name_of_lhs()
            ASTSynapseInformationCollector.kernel_name_to_kernel[kernel_name]=node
            
    def visit_function_call(self, node):
        if self.inside_equations_block:
            if self.inside_inline_expression and self.inside_simple_expression:
                if node.get_name() == "convolve":
                    self.inside_kernel_call = True
                    kernel, spikes = node.get_args()
                    kernel_var = kernel.get_variables()[0]
                    spikes_var = spikes.get_variables()[0]
                    ASTSynapseInformationCollector.inline_expression_to_kernel_args[self.current_inline_expression].add((kernel_var, spikes_var))
                else:
                    ASTSynapseInformationCollector.inline_expression_to_function_calls[self.current_inline_expression].add(node)
            if self.inside_kernel and self.inside_simple_expression:
                ASTSynapseInformationCollector.kernel_to_function_calls[self.current_kernel].add(node)
                
        
    def endvisit_function_call(self, node):
        self.inside_kernel_call = False   
        
    def endvisit_kernel(self, node):
        self.current_kernel = None
        self.inside_kernel = False

    def visit_variable(self, node):
        if self.inside_inline_expression and not self.inside_kernel_call:
            ASTSynapseInformationCollector.inline_expression_to_variables[self.current_inline_expression].add(node)
        elif self.inside_kernel and (self.inside_expression or self.inside_simple_expression):
            ASTSynapseInformationCollector.kernel_to_rhs_variables[self.current_kernel].add(node)    
        elif self.inside_declaration and self.inside_expression:
            declared_variable = self.current_declaration.get_variables()[0].get_name()
            ASTSynapseInformationCollector.declaration_to_rhs_variables[declared_variable].add(node)
            
                
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
        
    def visit_input_block(self, node):
        self.inside_input_block = True
        
    def visit_input_port(self, node):
        ASTSynapseInformationCollector.input_port_name_to_input_port[node.get_name()] = node
        
    def endvisit_input_block(self, node):
        self.inside_input_block = False
    
    def visit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = True
        if node.is_parameters: 
            self.inside_parameter_block = True
        if node.is_internals: 
            self.inside_internals_block = True

    def endvisit_block_with_variables(self, node):
        if node.is_state:
            self.inside_state_block = False
        if node.is_parameters: 
            self.inside_parameter_block = False
        if node.is_internals: 
            self.inside_internals_block = False
                
    def visit_simple_expression(self, node):
        self.inside_simple_expression = True
        self.current_simple_expression = node
    
    def endvisit_simple_expression(self, node):
        self.inside_simple_expression = False
        self.current_simple_expression = None
      
    def visit_declaration(self, node):
        self.inside_declaration = True
        self.current_declaration = node
        
        # collect decalarations generally
        variable_name = node.get_variables()[0].get_name()
        ASTSynapseInformationCollector.variable_name_to_declaration[variable_name] = node
        
        # collect declarations per block
        if self.inside_parameter_block:
            ASTSynapseInformationCollector.parameter_name_to_declaration[variable_name] = node
        elif self.inside_state_block:
            ASTSynapseInformationCollector.state_name_to_declaration[variable_name] = node
        elif self.inside_internals_block:
            ASTSynapseInformationCollector.internal_var_name_to_declaration[variable_name] = node
    
    def endvisit_declaration(self, node):
        self.inside_declaration = False
        self.current_declaration = None
        
    def visit_expression(self, node):
        self.inside_expression = True
        self.current_expression = node
    
    def endvisit_expression(self, node):
        self.inside_expression = False  
        self.current_expression = None
       
    # this method was copied over from ast_transformer
    # in order to avoid a circular dependency    
    @staticmethod    
    def construct_kernel_X_spike_buf_name(kernel_var_name: str, spike_input_port, order: int, diff_order_symbol="__d"):
        assert type(kernel_var_name) is str
        assert type(order) is int
        assert type(diff_order_symbol) is str
        return kernel_var_name.replace("$", "__DOLLAR") + "__X__" + str(spike_input_port) + diff_order_symbol * order





