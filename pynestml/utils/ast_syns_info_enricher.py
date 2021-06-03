"""
input: a neuron after ODE-toolbox transformations

the kernel analysis solves all kernels at the same time
this splits the variables on per kernel basis

"""        
from _collections import defaultdict
import copy

from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_visitor import ASTVisitor





class ASTSynsInfoEnricher(ASTVisitor):
    #
    # cm_syns_info = {}
    # kernel_name_to_analytic_solver = {}
    #
    # synapse_inline_to_ODE_propagators = defaultdict(lambda:set())
    # synapse_inline_to_ODE_update_expressions = defaultdict(lambda:set())
    # synapse_inline_to_ODE_state_variables = defaultdict(lambda:set())
    # synapse_inline_to_ODE_initial_values = defaultdict(lambda:set())
    # synapse_inline_to_parameters = defaultdict(lambda:set())
    #
    
    variables_to_internal_declarations = {}
    internal_variable_name_to_variable = {}
    
    @classmethod
    def enrich_syns_info(cls, neuron: ASTNeuron, cm_syns_info: dict, kernel_name_to_analytic_solver: dict):
        cm_syns_info = cls.add_kernel_analysis(neuron, cm_syns_info, kernel_name_to_analytic_solver)
        cm_syns_info = cls.transform_analytic_solution(neuron, cm_syns_info)
        return cm_syns_info

    """
    cm_syns_info input structure
    
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
    
    output

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
                    "analytic_solution":
                    {
                        'propagators':
                        {
                            '__P__g_ex_AMPA__X__spikesExc__g_ex_AMPA__X__spikesExc':
                                'exp(-__h/tau_syn_AMPA)'    
                        },
                        'update_expressions':
                        {
                            'g_ex_AMPA__X__spikesExc': 
                                '__P__g_ex_AMPA__X__spikesExc__g_ex_AMPA__X__spikesExc*g_ex_AMPA__X__spikesExc'
                        },
                        'state_variables': ['g_ex_AMPA__X__spikesExc'],
                        'initial_values':
                        {
                            'g_ex_AMPA__X__spikesExc': '1',
                        },
                        'solver': "analytical",
                        'parameters':
                        {
                            'tau_syn_AMPA': '0.200000000000000',
                        },
                    }
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
    def add_kernel_analysis(cls, neuron: ASTNeuron, cm_syns_info: dict, kernel_name_to_analytic_solver: dict):
        enriched_syns_info = copy.copy(cm_syns_info)
        for synapse_name, synapse_info in cm_syns_info.items():
            for kernel_name, kernel_info in synapse_info["kernels"].items():
                analytic_solution = kernel_name_to_analytic_solver[neuron.get_name()][kernel_name]
                enriched_syns_info[synapse_name]["kernels"][kernel_name]["analytic_solution"] = analytic_solution
        return enriched_syns_info     
                
                
    """
    cm_syns_info input structure

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
                    "analytic_solution":
                    {
                        'propagators':
                        {
                            '__P__g_ex_AMPA__X__spikesExc__g_ex_AMPA__X__spikesExc':
                                'exp(-__h/tau_syn_AMPA)'    
                        },
                        'update_expressions':
                        {
                            'g_ex_AMPA__X__spikesExc': 
                                '__P__g_ex_AMPA__X__spikesExc__g_ex_AMPA__X__spikesExc*g_ex_AMPA__X__spikesExc'
                        },
                        'state_variables': ['g_ex_AMPA__X__spikesExc'],
                        'initial_values':
                        {
                            'g_ex_AMPA__X__spikesExc': '1',
                        },
                        'solver': "analytical",
                        'parameters':
                        {
                            'tau_syn_AMPA': '0.200000000000000',
                        },
                    }
                }
            }
                
        },
        "GABA":
        {
            ...
        }
        ...
    }
    
    output
    
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
                    "analytic_solution":
                    {
                        'analytic_state_variables': ['g_ex_AMPA__X__spikesExc'],
                        'analytic_state_symbols':
                        {
                            'g_ex_AMPA__X__spikesExc': ASTVariable,
                        },
                        'initial_values':
                        {
                            'g_ex_AMPA__X__spikesExc': '1',
                        },
                        'propagators':
                        {
                            __P__g_ex_AMPA__X__spikesExc__g_ex_AMPA__X__spikesExc: 
                            {
                                "ASTVariable": ASTVariable,
                                "rhs_expression": ASTSimpleExpression,
                            },
                        },
                        'update_expressions':
                        {
                            'g_ex_AMPA__X__spikesExc': ASTExpression
                        },
                    }
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
    def transform_analytic_solution (cls, neuron: ASTNeuron, cm_syns_info: dict):

        enriched_syns_info = copy.copy(cm_syns_info)
        for synapse_name, synapse_info in cm_syns_info.items():
            for kernel_name, kernel_info in synapse_info["kernels"].items():
                analytic_solution = enriched_syns_info[synapse_name]["kernels"][kernel_name]["analytic_solution"]
                analytic_solution_transformed = defaultdict(lambda:defaultdict())

                # state variables generated by analytic solution
                analytic_solution_transformed['analytic_state_variables'] = analytic_solution["state_variables"]
                analytic_solution_transformed['analytic_variable_symbols'] = {sym: neuron.get_equations_block().get_scope().resolve_to_symbol(
                    sym, SymbolKind.VARIABLE) for sym in analytic_solution_transformed['analytic_state_variables']}
                
                for sym, expr in analytic_solution["initial_values"].items():
                    analytic_solution_transformed['initial_values'][sym] = expr
                for sym in analytic_solution_transformed['analytic_state_variables']:
                    expr_str = analytic_solution["update_expressions"][sym]
                    expr_ast = ModelParser.parse_expression(expr_str)
                    # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                    expr_ast.update_scope(neuron.get_equations_blocks().get_scope())
                    expr_ast.accept(ASTSymbolTableVisitor())
                    analytic_solution_transformed['update_expressions'][sym] = expr_ast
                    
                for variable_name, expression_string in analytic_solution["propagators"].items():
                    variable = cls.internal_variable_name_to_variable[variable_name]
                    expression = cls.variables_to_internal_declarations[variable]
                    analytic_solution_transformed['propagators'][variable_name]={
                        "ASTVariable": variable,
                        "rhs_expression": expression,
                    }
                    
                enriched_syns_info[synapse_name]["kernels"][kernel_name]["analytic_solution"] = analytic_solution_transformed

    
    
    
    
    def __init__(self , neuron):
        super(ASTSynsInfoEnricher, self).__init__()
    #     ASTSynsInfoEnricher.cm_syn_info = cm_syns_info
    #     ASTSynsInfoEnricher.kernel_name_to_analytic_solver = kernel_name_to_analytic_solver
    #
    #     self.enrich
    #
    
        self.inside_parameter_block = False
        self.inside_state_block = False
        self.inside_internals_block = False
    #     self.inside_equations_block = False
    #
    #     self.inside_inline_expression = False
    #     self.inside_kernel = False
    #     self.inside_kernel_call = False
        self.inside_declaration = False
    #     self.inside_simple_expression = False
    #     self.inside_expression = False
    #
    #     self.current_inline_expression = None
    #     self.current_kernel = None
    #     self.current_synapse_name = None
        neuron.accept(self)



    # def visit_variable(self, node):
    #     pass
    #
    # def visit_inline_expression(self, node):
    #     self.inside_inline_expression = True
    #     self.current_inline_expression = node
    #
    # def endvisit_inline_expression(self, node):
    #     self.inside_inline_expression = False
    #     self.current_inline_expression = None
    #
    # def visit_equations_block(self, node):
    #     self.inside_equations_block = True
    #
    # def endvisit_equations_block(self, node):
    #     self.inside_equations_block = False
    #
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
    #
    # def visit_simple_expression(self, node):
    #     self.inside_simple_expression = True
    #
    # def endvisit_simple_expression(self, node):
    #     self.inside_simple_expression = False
    #
    
    def visit_declaration(self, node):
        self.inside_declaration = True
        if self.inside_internals_block:
            variable = node.get_variables()[0]
            expression = node.get_expression()
            ASTSynsInfoEnricher.variables_to_internal_declarations[variable] = expression
            ASTSynsInfoEnricher.internal_variable_name_to_variable[variable.get_name()] = variable
    
    def endvisit_declaration(self, node):
        self.inside_declaration = False
    #
    # def visit_expression(self, node):
    #     self.inside_expression = True
    #
    # def endvisit_expression(self, node):
    #     self.inside_expression = False   
        