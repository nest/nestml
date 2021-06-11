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
import sympy

from build.lib.pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression


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
    inline_name_to_transformed_inline = {}
    
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
            "buffers_used": {"b_spikes"},
            "parameters_used": 
            {
                "e_AMPA": ASTDeclaration,
                "tau_syn_AMPA": ASTDeclaration
            }
            "convolutions":
            {
                "g_ex_AMPA__X__b_spikes": 
                {
                    "kernel": 
                    {
                        "name": "g_ex_AMPA",
                        "ASTKernel": ASTKernel
                    }
                    "spikes": 
                    {
                        "name": "b_spikes",
                        "ASTInputPort": ASTInputPort
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
            "buffers_used": {"b_spikes"},
            "parameters_used": 
            {
                "e_AMPA": ASTDeclaration,
                "tau_syn_AMPA": ASTDeclaration
            }
            "convolutions":
            {
                "g_ex_AMPA__X__b_spikes": 
                {
                    "kernel": 
                    {
                        "name": "g_ex_AMPA",
                        "ASTKernel": ASTKernel
                    }
                    "spikes": 
                    {
                        "name": "b_spikes",
                        "ASTInputPort": ASTInputPort
                    }
                    "analytic_solution":
                    {
                        'propagators':
                        {
                            '__P__g_ex_AMPA__X__b_spikes__g_ex_AMPA__X__b_spikes':
                                'exp(-__h/tau_syn_AMPA)'    
                        },
                        'update_expressions':
                        {
                            'g_ex_AMPA__X__b_spikes': 
                                '__P__g_ex_AMPA__X__b_spikes__g_ex_AMPA__X__b_spikes*g_ex_AMPA__X__b_spikes'
                        },
                        'state_variables': ['g_ex_AMPA__X__b_spikes'],
                        'initial_values':
                        {
                            'g_ex_AMPA__X__b_spikes': '1',
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
            for convolution_name, convolution_info in synapse_info["convolutions"].items():
                kernel_name = convolution_info["kernel"]["name"]
                analytic_solution = kernel_name_to_analytic_solver[neuron.get_name()][kernel_name]
                enriched_syns_info[synapse_name]["convolutions"][convolution_name]["analytic_solution"] = analytic_solution
        return enriched_syns_info     
                
                
    """
    cm_syns_info input structure

    {
        "AMPA":
        {
            "inline_expression": ASTInlineExpression,
            "buffers_used": {"b_spikes"},
            "parameters_used": 
            {
                "e_AMPA": ASTDeclaration,
                "tau_syn_AMPA": ASTDeclaration
            }
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
                    "analytic_solution":
                    {
                        'propagators':
                        {
                            '__P__g_ex_AMPA__X__b_spikes__g_ex_AMPA__X__b_spikes':
                                'exp(-__h/tau_syn_AMPA)'    
                        },
                        'update_expressions':
                        {
                            'g_ex_AMPA__X__b_spikes': 
                                '__P__g_ex_AMPA__X__b_spikes__g_ex_AMPA__X__b_spikes*g_ex_AMPA__X__b_spikes'
                        },
                        'state_variables': ['g_ex_AMPA__X__b_spikes'],
                        'initial_values':
                        {
                            'g_ex_AMPA__X__b_spikes': '1',
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
            "inline_expression": ASTInlineExpression, #transformed version
            "inline_expression_d": ASTExpression,
            "buffer_name": "b_spikes",
            "parameters_used": 
            {
                "e_AMPA": ASTDeclaration,
                "tau_syn_AMPA": ASTDeclaration
            }
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
                    "analytic_solution":
                    {
                        'kernel_states':
                        {
                            "g_ex_AMPA__X__b_spikes":
                            {
                                "ASTVariable": ASTVariable,
                                "init_expression": AST(Simple)Expression,
                                "update_expression": ASTExpression,
                            }
                        },
                        'propagators':
                        {
                            __P__g_ex_AMPA__X__b_spikes__g_ex_AMPA__X__b_spikes: 
                            {
                                "ASTVariable": ASTVariable,
                                "init_expression": ASTExpression,
                            },
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
            for convolution_name in synapse_info["convolutions"].keys():
                analytic_solution = enriched_syns_info[synapse_name]["convolutions"][convolution_name]["analytic_solution"]
                analytic_solution_transformed = defaultdict(lambda:defaultdict())

                for variable_name, expression_str in analytic_solution["initial_values"].items():
                    variable = neuron.get_equations_block().get_scope().resolve_to_symbol(variable_name, SymbolKind.VARIABLE)
                    
                    expression = ModelParser.parse_expression(expression_str)
                    # pretend that update expressions are in "equations" block, 
                    # which should always be present, as synapses have been defined to get here
                    expression.update_scope(neuron.get_equations_blocks().get_scope())
                    expression.accept(ASTSymbolTableVisitor())                  
                                        
                    update_expr_str = analytic_solution["update_expressions"][variable_name]
                    update_expr_ast = ModelParser.parse_expression(update_expr_str)
                    # pretend that update expressions are in "equations" block, which should always be present, as differential equations must have been defined to get here
                    update_expr_ast.update_scope(neuron.get_equations_blocks().get_scope())
                    update_expr_ast.accept(ASTSymbolTableVisitor())
                    
                    analytic_solution_transformed['kernel_states'][variable_name]={
                        "ASTVariable": variable,
                        "init_expression": expression,
                        "update_expression": update_expr_ast,
                    }
                    
                for variable_name, expression_string in analytic_solution["propagators"].items():
                    variable = cls.internal_variable_name_to_variable[variable_name]
                    expression = cls.variables_to_internal_declarations[variable]
                    analytic_solution_transformed['propagators'][variable_name]={
                        "ASTVariable": variable,
                        "init_expression": expression,
                    }
                    
                enriched_syns_info[synapse_name]["convolutions"][convolution_name]["analytic_solution"] = analytic_solution_transformed
        
            # only one buffer allowed, so allow direct access 
            # to it instead of a list
            if "buffer_name" not in enriched_syns_info[synapse_name]:
                buffers_used = list(enriched_syns_info[synapse_name]["buffers_used"])
                del enriched_syns_info[synapse_name]["buffers_used"]
                enriched_syns_info[synapse_name]["buffer_name"] = buffers_used[0]
            
            inline_expression_name = enriched_syns_info[synapse_name]["inline_expression"].variable_name    
            enriched_syns_info[synapse_name]["inline_expression"] = \
                ASTSynsInfoEnricher.inline_name_to_transformed_inline[inline_expression_name]
            enriched_syns_info[synapse_name]["inline_expression_d"] = \
                cls.computeExpressionDerivative(enriched_syns_info[synapse_name]["inline_expression"])
        
        return enriched_syns_info 
    
    @classmethod
    def computeExpressionDerivative(cls, inline_expression: ASTInlineExpression) -> ASTExpression:
        expr_str = str(inline_expression.get_expression())
        sympy_expr = sympy.parsing.sympy_parser.parse_expr(expr_str)
        sympy_expr = sympy.diff(sympy_expr, "v_comp")
        
        ast_expression_d = ModelParser.parse_expression(str(sympy_expr))
        # copy scope of the original inline_expression into the the derivative
        ast_expression_d.update_scope(inline_expression.get_scope())
        ast_expression_d.accept(ASTSymbolTableVisitor())  
        
        return ast_expression_d
    
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
        self.inside_inline_expression = False
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
    def visit_inline_expression(self, node):
        inline_name = node.variable_name
        ASTSynsInfoEnricher.inline_name_to_transformed_inline[inline_name]=node
    
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
        