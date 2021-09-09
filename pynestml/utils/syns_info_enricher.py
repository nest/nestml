"""
input: a neuron after ODE-toolbox transformations

the kernel analysis solves all kernels at the same time
this splits the variables on per kernel basis

"""        
from _collections import defaultdict
import copy

from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.model_parser import ModelParser
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.visitors.ast_visitor import ASTVisitor
import sympy


class SynsInfoEnricher(ASTVisitor):
    
    variables_to_internal_declarations = {}
    internal_variable_name_to_variable = {}
    inline_name_to_transformed_inline = {}
    
    # assuming depth first traversal
    # collect declaratins in the order
    # in which they were present in the neuron
    declarations_ordered = []
    
    @classmethod
    def enrich_syns_info(cls, neuron: ASTNeuron, cm_syns_info: dict, kernel_name_to_analytic_solver: dict):
        cm_syns_info = cls.add_kernel_analysis(neuron, cm_syns_info, kernel_name_to_analytic_solver)
        cm_syns_info = cls.transform_analytic_solution(neuron, cm_syns_info)
        cm_syns_info = cls.restoreOrderInternals(neuron, cm_syns_info)
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
            "analytic_helpers":
            {
                "__h":
                {
                    "ASTVariable": ASTVariable,
                    "init_expression": ASTExpression,
                    "is_time_resolution": True,
                },
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
                    expression = ModelParser.parse_expression(expression_string)
                    # pretend that update expressions are in "equations" block, 
                    # which should always be present, as synapses have been defined to get here
                    expression.update_scope(neuron.get_equations_blocks().get_scope())
                    expression.accept(ASTSymbolTableVisitor()) 
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
                SynsInfoEnricher.inline_name_to_transformed_inline[inline_expression_name]
            enriched_syns_info[synapse_name]["inline_expression_d"] = \
                cls.computeExpressionDerivative(enriched_syns_info[synapse_name]["inline_expression"])
            
            # now also identify analytic helper variables such as __h
            enriched_syns_info[synapse_name]["analytic_helpers"] = cls.get_analytic_helper_variable_declarations(enriched_syns_info[synapse_name])
        
        return enriched_syns_info 
    
    """
    input:
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
            "analytic_helpers":
            {
                "__h":
                {
                    "ASTVariable": ASTVariable,
                    "init_expression": ASTExpression,
                    "is_time_resolution": True,
                },
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
    
    output:
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
            },
            "states_used": 
            {
                "v_comp": ASTDeclaration,
            },            
            "internals_used_declared":
            [
                ("td", ASTDeclaration),
                ("g_norm_exc", ASTDeclaration),
            ],
            "total_used_declared": {"e_AMPA", ..., "v_comp", ..., "td", ...}
            ,
            "analytic_helpers":
            {
                "__h":
                {
                    "ASTVariable": ASTVariable,
                    "init_expression": ASTExpression,
                    "is_time_resolution": True,
                },
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
    
    # orders user defined internals
    # back to the order they were originally defined
    # this is important if one such variable uses another
    # user needs to have control over the order
    @classmethod
    def restoreOrderInternals (cls, neuron: ASTNeuron, cm_syns_info: dict):
        
        # assign each variable a rank
        # that corresponds to the order in SynsInfoEnricher.declarations_ordered
        variable_name_to_order = {}
        for index, declaration in enumerate(SynsInfoEnricher.declarations_ordered):
            variable_name = declaration.get_variables()[0].get_name()
            variable_name_to_order[variable_name] = index
            
        enriched_syns_info = copy.copy(cm_syns_info)
        for synapse_name, synapse_info in cm_syns_info.items():
            user_internals = enriched_syns_info[synapse_name]["internals_used_declared"]
            user_internals_sorted = sorted(user_internals.items(), key = lambda x: variable_name_to_order[x[0]])
            enriched_syns_info[synapse_name]["internals_used_declared"] = user_internals_sorted
            
        return enriched_syns_info
            
            
        
    
    @classmethod
    def prettyPrint(cls, syns_info, indent=2):
        print('\t' * indent + "{")
        for key, value in syns_info.items():
            print('\t' * indent + "\""+str(key)+"\":")
            if isinstance(value, dict):
                cls.prettyPrint(value, indent+1)
            else:
                print('\t' * (indent+1) + str(value).replace("\n", '\n'+ '\t' * (indent+1)) + ", ")
        print('\t' * indent + "},")
    
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
    
    @classmethod
    def get_variable_names_used(cls, node) -> set:
        variable_names_extractor = ASTUsedVariableNamesExtractor(node)
        return variable_names_extractor.variable_names
    
    # returns all variable names referenced by the synapse inline
    # and by the analytical solution
    # assumes that the model has already been transformed
    @classmethod
    def get_all_synapse_variables(cls, single_synapse_info):
        # get all variables from transformed inline
        inline_variables = cls.get_variable_names_used(single_synapse_info["inline_expression"])
        
        analytic_solution_vars = set()
        # get all variables from transformed analytic solution
        for convolution_name, convolution_info in single_synapse_info["convolutions"].items():
            analytic_sol = convolution_info["analytic_solution"]
            # get variables from init and update expressions
            # for each kernel
            for kernel_var_name, kernel_info in analytic_sol["kernel_states"].items():
                analytic_solution_vars.add(kernel_var_name)
                
                update_vars = cls.get_variable_names_used(kernel_info["update_expression"])
                init_vars = cls.get_variable_names_used(kernel_info["init_expression"])
        
                analytic_solution_vars.update(update_vars)
                analytic_solution_vars.update(init_vars)
                
            # get variables from init expressions
            # for each propagator   
            # include propagator variable itself         
            for propagator_var_name, propagator_info in analytic_sol["propagators"].items():
                analytic_solution_vars.add(propagator_var_name)
                
                init_vars = cls.get_variable_names_used(propagator_info["init_expression"])

                analytic_solution_vars.update(init_vars)
        
        return analytic_solution_vars.union(inline_variables)
    
    @classmethod
    def get_new_variables_after_transformation(cls, single_synapse_info):
        return cls.get_all_synapse_variables(single_synapse_info).difference(single_synapse_info["total_used_declared"])   

    # get new variables that only occur on the right hand side of analytic solution Expressions
    # but for wich analytic solution does not offer any values
    # this can isolate out additional variables that suddenly appear such as __h
    # whose initial values are not inlcuded in the output of analytic solver
    @classmethod
    def get_analytic_helper_variable_names(cls, single_synapse_info):    
        analytic_lhs_vars = set()
        
        for convolution_name, convolution_info in single_synapse_info["convolutions"].items():
            analytic_sol = convolution_info["analytic_solution"]
            
            # get variables representing convolutions by kernel
            for kernel_var_name, kernel_info in analytic_sol["kernel_states"].items():
                analytic_lhs_vars.add(kernel_var_name)
                
            # get propagator variable names    
            for propagator_var_name, propagator_info in analytic_sol["propagators"].items():
                analytic_lhs_vars.add(propagator_var_name)
                
        return cls.get_new_variables_after_transformation(single_synapse_info).symmetric_difference(analytic_lhs_vars)

    @classmethod
    def get_analytic_helper_variable_declarations(cls, single_synapse_info):
        variable_names = cls.get_analytic_helper_variable_names(single_synapse_info)
        result = dict()
        for variable_name in variable_names:
            if variable_name not in cls.internal_variable_name_to_variable: continue
            variable = cls.internal_variable_name_to_variable[variable_name]
            expression = cls.variables_to_internal_declarations[variable]
            result[variable_name]={
                "ASTVariable": variable,
                "init_expression": expression,
            }
            if expression.is_function_call() and expression.get_function_call().callee_name == PredefinedFunctions.TIME_RESOLUTION:
                result[variable_name]["is_time_resolution"] = True
            else:
                result[variable_name]["is_time_resolution"] = False
                
                
        return result

    def __init__(self , neuron):
        super(SynsInfoEnricher, self).__init__()

        self.inside_parameter_block = False
        self.inside_state_block = False
        self.inside_internals_block = False
        self.inside_inline_expression = False
        self.inside_inline_expression = False
        self.inside_declaration = False
        self.inside_simple_expression = False
        neuron.accept(self)
            
    def visit_inline_expression(self, node):
        self.inside_inline_expression = True
        inline_name = node.variable_name
        SynsInfoEnricher.inline_name_to_transformed_inline[inline_name]=node
        
    def endvisit_inline_expression(self, node):
        self.inside_inline_expression = False
    

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
    
    def endvisit_simple_expression(self, node):
        self.inside_simple_expression = False
    
    def visit_declaration(self, node):
        self.declarations_ordered.append(node)
        self.inside_declaration = True
        if self.inside_internals_block:
            variable = node.get_variables()[0]
            expression = node.get_expression()
            SynsInfoEnricher.variables_to_internal_declarations[variable] = expression
            SynsInfoEnricher.internal_variable_name_to_variable[variable.get_name()] = variable
    
    def endvisit_declaration(self, node):
        self.inside_declaration = False
  
    
class ASTUsedVariableNamesExtractor(ASTVisitor):
    def __init__(self , node):
        super(ASTUsedVariableNamesExtractor, self).__init__()
        self.variable_names = set()
        node.accept(self)
    
    def visit_variable(self, node):
        self.variable_names.add(node.get_name())    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        