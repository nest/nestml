# -*- coding: utf-8 -*-
#
# co_co_cm_functions_and_initial_values_defined.py
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

from pynestml.cocos.co_co import CoCo
from pynestml.codegeneration.nest_printer import NestPrinter
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor


class CoCoCmFunctionsAndVariablesDefined(CoCo):
    
    inline_expression_prefix = "cm_p_open_"
    padding_character = "_"
    inf_string = "inf"
    tau_sring = "tau"
    gbar_string = "gbar"
    e_string = "e"
    
    neuron_to_cm_info = {}
    
    """
    This class represents a constraint condition which ensures that 
    all variables x as used in the inline expression cm_p_open_{channelType}
    (which is searched for inside ASTEquationsBlock)
    have the following compartmental model functions defined

        _x_inf_{channelType}(v_comp real) real
        _tau_x_{channelType}(v_comp real) real
    

    Example:
        equations: 
            inline cm_p_open_Na real = m_Na_**3 * h_Na_**1
        end
        
        #causes to require
        function _h_inf_Na(v_comp real) real:
            return 1.0/(exp(0.16129032258064516*v_comp + 10.483870967741936) + 1.0)
        end
    
        function _tau_h_Na(v_comp real) real: 
            return 0.3115264797507788/((-0.0091000000000000004*v_comp - 0.68261830000000012)/(1.0 - 3277527.8765015295*exp(0.20000000000000001*v_comp)) + (0.024*v_comp + 1.200312)/(1.0 - 4.5282043263959816e-5*exp(-0.20000000000000001*v_comp)))
        end
        
    Moreover it checks if all expected initial values are defined
    And that variables are properly named
    Example:
        inline cm_p_open_Na real = m_Na_**3 * h_Na_**1
        
        #causes to requirement for following entries in the initial values block
        
        gbar_Na
        e_Na
        m_Na_
        h_Na_
    
    """
    
    

    """
    analyzes any inline cm_p_open_{channelType}
    and returns returns
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "inner_variables": [ASTVariable, ASTVariable, ASTVariable, ...],
            
        },
        "K":
        {
            ...
        }
    }
    """
    @classmethod
    def calcRelevantInlineExpressions(cls, node):
        # search for inline expressions inside equations block
        inline_expressions_inside_equations_block_collector_visitor = ASTInlineExpressionInsideEquationsBlockCollectorVisitor()
        node.accept(inline_expressions_inside_equations_block_collector_visitor)
        inline_expressions_dict = inline_expressions_inside_equations_block_collector_visitor.inline_expressions_to_variables
        
        is_compartmental_model = False
        # filter for cm_p_open_{channelType}
        relevant_inline_expressions_to_variables = defaultdict(lambda:list())
        for expression, variables in inline_expressions_dict.items():
            inline_expression_name = expression.variable_name
            if inline_expression_name.startswith(cls.inline_expression_prefix):
                is_compartmental_model = True
                relevant_inline_expressions_to_variables[expression] = variables
        
        #create info structure
        cm_info = defaultdict()        
        for inline_expression, inner_variables in relevant_inline_expressions_to_variables.items():
            info = defaultdict()
            channel_name = cls.cm_expression_to_channel_name(inline_expression)
            info["ASTInlineExpression"] = inline_expression
            info["inner_variables"] = inner_variables
            cm_info[channel_name] = info
        node.is_compartmental_model = is_compartmental_model
        return cm_info
    
    @classmethod
    def cm_expression_to_channel_name(cls, expr):
        assert(isinstance(expr, ASTInlineExpression))
        return expr.variable_name[len(cls.inline_expression_prefix):].strip(cls.padding_character)

    # extract channel name from inline expression name
    # i.e  cm_p_open_Na -> channel name is Na
    @classmethod
    def extract_pure_variable_name(cls, varname, ic_name):
        varname = varname.strip(cls.padding_character)
        assert(varname.endswith(ic_name))
        return varname[:-len(ic_name)].strip(cls.padding_character)
    
    @classmethod
    def getExpectedGbarName(cls, ion_channel_name):
        return cls.gbar_string+cls.padding_character+ion_channel_name+cls.padding_character
    
    @classmethod
    def getExpectedEquilibirumVarName(cls, ion_channel_name):
        return cls.e_string+cls.padding_character+ion_channel_name+cls.padding_character
    
    @classmethod
    def getExpectedTauFunctionName(cls, ion_channel_name, pure_variable_name):
        return cls.padding_character+cls.getExpectedTauResultVariableName(ion_channel_name, pure_variable_name)
    
    
    @classmethod
    def getExpectedInfFunctionName(cls, ion_channel_name, pure_variable_name):
        return cls.padding_character+cls.getExpectedInfResultVariableName(ion_channel_name, pure_variable_name)

    @classmethod
    def getExpectedTauResultVariableName(cls, ion_channel_name, pure_variable_name):
        return cls.tau_sring+cls.padding_character+pure_variable_name+cls.padding_character+ion_channel_name
    
    
    @classmethod
    def getExpectedInfResultVariableName(cls, ion_channel_name, pure_variable_name):
        return pure_variable_name+cls.padding_character+cls.inf_string+cls.padding_character + ion_channel_name
    
    
    # calculate function names that must be implemented
    # i.e 
    # m_Na_**3 * h_Na_**1 
    # leads to expect
    # _m_inf_Na(v_comp real) real
    # _tau_m_Na(v_comp real) real
    """
    analyzes any inline cm_p_open_{channelType} for expected function names
    input:
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "inner_variables": [ASTVariable, ASTVariable, ASTVariable, ...]
            
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
            "inner_variables": 
            {
                "m":
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": str,
                        "inf": str
                    }
                }, 
                "someinvalidname" 
                {
                    "ASTVariable": ASTVariable
                    "is_valid": False,
                },
                "h":  
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": str,
                        "inf": str
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
    def calcExpectedFunctionNamesForChannels(cls, cm_info):
        variables_procesed = defaultdict()
        
        for ion_channel_name, channel_info in cm_info.items():
            cm_expression = channel_info["ASTInlineExpression"]
            variables = channel_info["inner_variables"]
            variable_names_seen = set()
            
            variables_info = defaultdict()

            for variable_used in variables:
                variable_name = variable_used.name.strip(cls.padding_character)
                if not variable_name.endswith(ion_channel_name):
                    variables_info[variable_name]=defaultdict()
                    variables_info[variable_name]["ASTVariable"] = variable_used
                    variables_info[variable_name]["is_valid"] = False
                    continue
                
                # enforce unique variable names per channel, i.e n and m , not n and n
                if variable_name in variable_names_seen:
                    code, message = Messages.get_cm_inline_expression_variable_used_mulitple_times(cm_expression, variable_name, ion_channel_name)
                    Logger.log_message(code=code, message=message, error_position=variable_used.get_source_position(), log_level=LoggingLevel.ERROR, node=variable_used)
                    continue
                else:
                    variable_names_seen.add(variable_name)
                
                pure_variable_name = cls.extract_pure_variable_name(variable_name, ion_channel_name)
                expected_inf_function_name = cls.getExpectedInfFunctionName(ion_channel_name, pure_variable_name)
                expected_tau_function_name = cls.getExpectedTauFunctionName(ion_channel_name, pure_variable_name)
                
                variables_info[pure_variable_name]=defaultdict(lambda: defaultdict())
                variables_info[pure_variable_name]["expected_functions"][cls.inf_string] = expected_inf_function_name
                variables_info[pure_variable_name]["expected_functions"][cls.tau_sring] = expected_tau_function_name
                variables_info[pure_variable_name]["ASTVariable"] = variable_used
                variables_info[pure_variable_name]["is_valid"] = True
                
            variables_procesed[ion_channel_name] = copy.copy(variables_info)
            
        for ion_channel_name, variables_info in variables_procesed.items():
            cm_info[ion_channel_name]["inner_variables"] = variables_info
        
        return cm_info

    """
    input:
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "inner_variables": 
            {
                "m":
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                }, 
                "someinvalidname" 
                {
                    "ASTVariable": ASTVariable
                    "is_valid": False,
                },
                "h":  
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
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
            "channel_variables":
            {
                "gbar":{"expected_name": "gbar_Na_"},
                "e":{"expected_name": "e_Na_"}
            }
            "inner_variables": 
            {
                "m":
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                }, 
                "someinvalidname" 
                {
                    "ASTVariable": ASTVariable
                    "is_valid": False,
                },
                "h":  
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
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
    def getAndCheckExpectedVariableNamesAndReasons(cls, node, cm_info):
        ret = copy.copy(cm_info)

        channel_variables = defaultdict()
        for ion_channel_name, channel_info in cm_info.items():
            channel_variables[ion_channel_name] = defaultdict()
            channel_variables[ion_channel_name][cls.gbar_string] = defaultdict()
            channel_variables[ion_channel_name][cls.gbar_string]["expected_name"] = cls.getExpectedGbarName(ion_channel_name)
            channel_variables[ion_channel_name][cls.e_string] = defaultdict()
            channel_variables[ion_channel_name][cls.e_string]["expected_name"] = cls.getExpectedEquilibirumVarName(ion_channel_name)

            for pure_variable_name, variable_info in channel_info["inner_variables"].items():
                variable_used = variable_info["ASTVariable"]
                is_valid= variable_info["is_valid"]
                if not is_valid:
                    code, message = Messages.get_cm_inline_expression_variable_name_must_end_with_channel_name(channel_info["ASTInlineExpression"], variable_used.name, ion_channel_name)
                    Logger.log_message(code=code, message=message, error_position=variable_used.get_source_position(), log_level=LoggingLevel.ERROR, node=node)
                    continue
                
        for ion_channel_name, channel_info in cm_info.items():
            ret[ion_channel_name]["channel_variables"] = channel_variables[ion_channel_name]
                
        return ret 
    
    """
    input
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "inner_variables": 
            {
                "m":
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": str,
                        "inf": str
                    }
                }, 
                "someinvalidname" 
                {
                    "ASTVariable": ASTVariable
                    "is_valid": False,
                },
                "h":  
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": str,
                        "inf": str
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
    
    output
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "inner_variables": 
            {
                "m":
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                }, 
                "someinvalidname" 
                {
                    "ASTVariable": ASTVariable
                    "is_valid": False,
                },
                "h":  
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
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
    def checkAndFindFunctions(cls, node, cm_info):
        ret = copy.copy(cm_info)
        # get functions and collect their names    
        declared_functions = node.get_functions()
        
        function_name_to_function = {}
        for declared_function in declared_functions:
            function_name_to_function[declared_function.name] = declared_function
        
        
        # check for missing functions
        for ion_channel_name, channel_info in cm_info.items():
            for pure_variable_name, variable_info in channel_info["inner_variables"].items():
                if "expected_functions" in  variable_info.keys():
                    for function_type, expected_function_name in variable_info["expected_functions"].items():
                        if expected_function_name not in function_name_to_function.keys():
                            code, message = Messages.get_expected_cm_function_missing(ion_channel_name, variable_info["ASTVariable"], expected_function_name)
                            Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR, node=node)
                        else:
                            ret[ion_channel_name]["inner_variables"][pure_variable_name]["expected_functions"][function_type] = defaultdict()
                            ret[ion_channel_name]["inner_variables"][pure_variable_name]["expected_functions"][function_type]["ASTFunction"] = function_name_to_function[expected_function_name]
                            ret[ion_channel_name]["inner_variables"][pure_variable_name]["expected_functions"][function_type]["function_name"] = expected_function_name
                            
                            # function must have exactly one argument
                            astfun = ret[ion_channel_name]["inner_variables"][pure_variable_name]["expected_functions"][function_type]["ASTFunction"]
                            if len(astfun.parameters) != 1:
                                code, message = Messages.get_expected_cm_function_wrong_args_count(ion_channel_name, variable_info["ASTVariable"], astfun)
                                Logger.log_message(code=code, message=message, error_position=astfun.get_source_position(), log_level=LoggingLevel.ERROR, node=astfun)
                        
                            # function must return real
                            if not astfun.get_return_type().is_real:
                                code, message = Messages.get_expected_cm_function_bad_return_type(ion_channel_name, astfun)
                                Logger.log_message(code=code, message=message, error_position=astfun.get_source_position(), log_level=LoggingLevel.ERROR, node=astfun)
                        
                            if function_type == "tau":                                              
                                ret[ion_channel_name]["inner_variables"][pure_variable_name]["expected_functions"][function_type]["result_variable_name"] = cls.getExpectedTauResultVariableName(ion_channel_name,pure_variable_name)
                            elif function_type == "inf":
                                ret[ion_channel_name]["inner_variables"][pure_variable_name]["expected_functions"][function_type]["result_variable_name"] = cls.getExpectedInfResultVariableName(ion_channel_name,pure_variable_name)
                            else:
                                raise RuntimeError('This should never happen! Unsupported function type '+function_type+' from variable ' + pure_variable_name)    
        
        return ret
    
    @classmethod
    def check_co_co(cls, node: ASTNode):
        """
        Checks if this coco applies for the handed over neuron. 
        Models which do not have inline cm_p_open_{channelType}
        inside ASTEquationsBlock are not relevant
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        
        cm_info = cls.calcRelevantInlineExpressions(node)
        
        cm_info = cls.calcExpectedFunctionNamesForChannels(cm_info)
        cm_info = cls.checkAndFindFunctions(node, cm_info)
        cm_info = cls.getAndCheckExpectedVariableNamesAndReasons(node, cm_info)
        
        #now check for existence of expected_initial_variables and add their ASTVariable objects to cm_info
        initial_values_missing_visitor = InitialValueMissingVisitor(cm_info)
        node.accept(initial_values_missing_visitor)
        
        cls.neuron_to_cm_info[node.name] = initial_values_missing_visitor.cm_info



"""
    cm_info input
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "channel_variables":
            {
                "gbar":{"expected_name": "gbar_Na_"},
                "e":{"expected_name": "e_Na_"}
            }
            "inner_variables": 
            {
                "m":
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
                    }
                }, 
                "someinvalidname" 
                {
                    "ASTVariable": ASTVariable
                    "is_valid": False,
                },
                "h":  
                {
                    "ASTVariable": ASTVariable, 
                    "is_valid": True,
                    "expected_functions":
                    {
                        "tau": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str},
                        "inf": {"ASTFunction": ASTFunction, "function_name": str, "result_variable_name": str}
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
    
    cm_info output
    {
        "Na":
        {
            "ASTInlineExpression": ASTInlineExpression,
            "channel_variables":
            {
                "gbar": {
                            "expected_name": "gbar_Na_",
                            "initial_value_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        },
                "e":  {
                            "expected_name": "e_Na_",
                            "initial_value_variable": ASTVariable,
                            "rhs_expression": ASTSimpleExpression or ASTExpression
                        }
            }
            "inner_variables": 
            {
                "m":
                {
                    "ASTVariable": ASTVariable, 
                    "initial_value_variable": ASTVariable,
                    "is_valid": True,
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
                "someinvalidname" 
                {
                    "ASTVariable": ASTVariable
                    "is_valid": False,
                },
                "h":  
                {
                    "ASTVariable": ASTVariable, 
                    "initial_value_variable": ASTVariable,
                    "is_valid": True,
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
class InitialValueMissingVisitor(ASTVisitor):

    def __init__(self, cm_info):
        super(InitialValueMissingVisitor, self).__init__()
        self.cm_info = cm_info
        
        # store ASTElement that causes the expecation of existence of an initial value
        # needed to generate sufficiently informative error message
        self.expected_to_object = defaultdict() 
        
        self.values_expected_from_channel = set()
        for ion_channel_name, channel_info in self.cm_info.items():
            for channel_variable_type, channel_variable_info in channel_info["channel_variables"].items():
                self.values_expected_from_channel.add(channel_variable_info["expected_name"])
                self.expected_to_object[channel_variable_info["expected_name"]] = channel_info["ASTInlineExpression"]
                
        self.values_expected_from_variables = set() 
        for ion_channel_name, channel_info in self.cm_info.items():
            for pure_variable_type, variable_info in channel_info["inner_variables"].items():
                if variable_info["is_valid"]:
                    self.values_expected_from_variables.add(variable_info["ASTVariable"].name)
                    self.expected_to_object[variable_info["ASTVariable"].name] = variable_info["ASTVariable"]
        
        self.not_yet_found_variables = set(self.values_expected_from_channel).union(self.values_expected_from_variables)
        
        self.inside_block_with_variables = False
        self.inside_declaration = False
        self.current_block_with_variables = None
        self.current_declaration = None
        
    def visit_declaration(self, node):
        self.inside_declaration = True
        self.current_declaration = node
        
    def endvisit_declaration(self, node):
        self.inside_declaration = False
        self.current_declaration = None
        
    def visit_variable(self, node):
        if self.inside_block_with_variables and \
        self.inside_declaration and\
        self.current_block_with_variables is not None and\
        self.current_block_with_variables.is_initial_values:
            varname = node.name
            if varname in self.not_yet_found_variables:
                Logger.log_message(message="Expected initial variable '"+varname+"' found" ,
                               log_level=LoggingLevel.INFO)
                self.not_yet_found_variables.difference_update({varname})
                
                # make a copy because we can't write into the structure directly
                # while iterating over it
                cm_info_updated = copy.copy(self.cm_info)
                
                # thought: in my opinion initial values for state variables (m,n,h...)
                # should be in the state block
                # and initial values for channel parameters (gbar, e) 
                # may be meant for the parameters block
                
                # now that we found the initial value defintion, extract information into cm_info
                
                # channel parameters
                if varname in self.values_expected_from_channel:
                    for ion_channel_name, channel_info in self.cm_info.items():
                        for variable_type, variable_info in channel_info["channel_variables"].items():
                            if variable_info["expected_name"] == varname:
                                cm_info_updated[ion_channel_name]["channel_variables"][variable_type]["initial_value_variable"] = node
                                cm_info_updated[ion_channel_name]["channel_variables"][variable_type]["rhs_expression"] = self.current_declaration.get_expression()
                # state variables
                elif varname in self.values_expected_from_variables:
                    for ion_channel_name, channel_info in self.cm_info.items():
                        for pure_variable_name, variable_info in channel_info["inner_variables"].items():
                            if variable_info["ASTVariable"].name == varname:
                                cm_info_updated[ion_channel_name]["inner_variables"][pure_variable_name]["initial_value_variable"] = node
                                cm_info_updated[ion_channel_name]["inner_variables"][pure_variable_name]["rhs_expression"] = self.current_declaration.get_expression()
                
                self.cm_info = cm_info_updated             

    def endvisit_neuron(self, node):
        if self.not_yet_found_variables:
            code, message = Messages.get_expected_cm_initial_values_missing(self.not_yet_found_variables, self.expected_to_object)
            Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR, node=node)

        
    def visit_block_with_variables(self, node):
        self.inside_block_with_variables = True
        self.current_block_with_variables = node
    
    def endvisit_block_with_variables(self, node):
        self.inside_block_with_variables = False
        self.current_block_with_variables = None

class ASTInlineExpressionInsideEquationsBlockCollectorVisitor(ASTVisitor):

    def __init__(self):
        super(ASTInlineExpressionInsideEquationsBlockCollectorVisitor, self).__init__()
        self.inline_expressions_to_variables = defaultdict(lambda:list())
        self.inside_equations_block = False
        self.inside_inline_expression = False
        self.current_inline_expression = None

    def visit_variable(self, node):
        if self.inside_equations_block and \
            self.inside_inline_expression and \
            self.current_inline_expression is not None:
                self.inline_expressions_to_variables[self.current_inline_expression].append(node)
                
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
                

