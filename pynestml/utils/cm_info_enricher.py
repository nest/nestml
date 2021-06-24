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


class CmInfoEnricher():
    

    """
    Adds derivative of inline expression to cm_info
    This needs to be done separately from within nest_codegenerator
    because the import of ModelParser will otherwise cause 
    a circular dependency when this is done 
    inside CmProcessing
    
    input:
    
        {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "channel_parameters":
            {
                "gbar": {
                            "expected_name": "gbar_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        },
                "e":  {
                            "expected_name": "e_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        }
            }
            "gating_variables": 
            {
                "m":
                {
                    "ASTVariable": ASTVariable, 
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction, 
                                    "function_name": str, 
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction, 
                                    "function_name": str, 
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                }, 
                "h":  
                {
                    "ASTVariable": ASTVariable, 
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction, 
                                    "function_name": str, 
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction, 
                                    "function_name": str, 
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }
    
    output:
    
        {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "inline_derivative": ASTInlineExpression,
            "channel_parameters":
            {
                "gbar": {
                            "expected_name": "gbar_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        },
                "e":  {
                            "expected_name": "e_Na",
                            "parameter_block_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        }
            }
            "gating_variables": 
            {
                "m":
                {
                    "ASTVariable": ASTVariable, 
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction, 
                                    "function_name": str, 
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction, 
                                    "function_name": str, 
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                }, 
                "h":  
                {
                    "ASTVariable": ASTVariable, 
                    "state_variable": ASTVariable,
                    "expected_functions":
                    {
                        "tau":  {
                                    "ASTFunction": ASTFunction, 
                                    "function_name": str, 
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                },
                        "inf":  {
                                    "ASTFunction": ASTFunction, 
                                    "function_name": str, 
                                    "result_variable_name": str,
                                    "rhs_expression": ASTSimpleExpression or ASTExpression
                                }
                    }
                },
                ...
            }
        },
        "K":
        {
            ...
        }
    }
        
"""

    @classmethod
    def enrich_cm_info(cls, neuron: ASTNeuron, cm_info: dict):
        cm_info_copy = copy.copy(cm_info)
        for ion_channel_name, ion_channel_info in cm_info_copy.items():
            cm_info[ion_channel_name]["inline_derivative"] = cls.computeExpressionDerivative(cm_info[ion_channel_name]["ASTInlineExpression"])
        return cm_info
    
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
  
    
    
    
    
    
    
    
    
    
        