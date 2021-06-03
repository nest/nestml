"""
for each inline expression inside the equations block,
collect all synapse relevant information

"""
from _collections import defaultdict
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTSynapseInformationCollector(ASTVisitor):

    kernel_name_to_kernel = defaultdict()
    inline_expression_to_kernel_args = defaultdict(lambda:set())
    parameter_name_to_declaration = defaultdict()
    state_name_to_declaration = defaultdict()
    inline_expression_to_variables = defaultdict(lambda:set())
    kernel_to_rhs_variables = defaultdict(lambda:set())
    input_port_name_to_input_port = defaultdict()
        
    def __init__(self):
        super(ASTSynapseInformationCollector, self).__init__()
        
        self.inside_parameter_block = False
        self.inside_state_block = False
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
        # self.current_variable = None
        
        self.current_synapse_name = None
        
    @classmethod    
    def get_kernel_by_name(cls, name: str):
        return cls.kernel_name_to_kernel[name]
    
    @classmethod 
    def get_inline_expressions_with_kernels (cls):
        return cls.inline_expression_to_kernel_args.keys()
    
    @classmethod 
    def get_synapse_specific_parameter_declarations (cls, synapse_inline: ASTInlineExpression) -> str:
        # find all variables used in the inline
        potential_parameters = cls.inline_expression_to_variables[synapse_inline]
        
        # find all kernels referenced by the inline 
        # and collect variables used by those kernels
        kernel_arg_pairs = ASTSynapseInformationCollector.get_extracted_kernel_args(synapse_inline)
        for kernel_var, spikes_var in kernel_arg_pairs:
            kernel = ASTSynapseInformationCollector.get_kernel_by_name(kernel_var.get_name())
            potential_parameters.update(cls.kernel_to_rhs_variables[kernel])
        
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
            if param_name in cls.parameter_name_to_declaration:
                dereferenced[param_name] = cls.parameter_name_to_declaration[param_name]
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
    def get_used_kernel_names (self, inline_expression: ASTInlineExpression):
        return [kernel_var.get_name() for kernel_var, _ in self.get_extracted_kernel_args(inline_expression)]
    
    @classmethod     
    def get_used_spike_names (self, inline_expression: ASTInlineExpression):
        return [spikes_var.get_name() for _, spikes_var in self.get_extracted_kernel_args(inline_expression)]
        
    def visit_kernel(self, node):
        self.current_kernel = node
        self.inside_kernel = True
        if self.inside_equations_block:
            kernel_name = node.get_variables()[0].get_name_of_lhs()
            ASTSynapseInformationCollector.kernel_name_to_kernel[kernel_name]=node
            
    def visit_function_call(self, node):
        if self.inside_equations_block and self.inside_inline_expression \
        and self.inside_simple_expression:
            if node.get_name() == "convolve":
                self.inside_kernel_call = True
                kernel, spikes = node.get_args()
                kernel_var = kernel.get_variables()[0]
                spikes_var = spikes.get_variables()[0]
                ASTSynapseInformationCollector.inline_expression_to_kernel_args[self.current_inline_expression].add((kernel_var, spikes_var))
        
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
            ASTSynapseInformationCollector.parameter_name_to_declaration[node.get_variables()[0].get_name()] = node
        elif self.inside_state_block:
            variable_name = node.get_variables()[0].get_name()
            ASTSynapseInformationCollector.state_name_to_declaration[variable_name] = node
    
    def endvisit_declaration(self, node):
        self.inside_declaration = False
        
    def visit_expression(self, node):
        self.inside_expression = True
    
    def endvisit_expression(self, node):
        self.inside_expression = False  
       
    # this method was copied over from ast_transformer
    # in order to avoid a circular dependency    
    @staticmethod    
    def construct_kernel_X_spike_buf_name(kernel_var_name: str, spike_input_port, order: int, diff_order_symbol="__d"):
        assert type(kernel_var_name) is str
        assert type(order) is int
        assert type(diff_order_symbol) is str
        return kernel_var_name.replace("$", "__DOLLAR") + "__X__" + str(spike_input_port) + diff_order_symbol * order





