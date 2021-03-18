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
from pynestml.cocos.co_co import CoCo
from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression

from collections import defaultdict


class CoCoCmFunctionsAndVariablesDefined(CoCo):
    
    inline_expression_prefix = "cm_p_open_"
    padding_character = "_"
    
    
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
    
    
    #returns any inline cm_p_open_{channelType} found in the node
    @classmethod
    def getRelevantInlineExpressions(cls, node):
        # search for inline expressions inside equations block
        inline_expressions_inside_equations_block_collector_visitor = ASTInlineExpressionInsideEquationsBlockCollectorVisitor()
        node.accept(inline_expressions_inside_equations_block_collector_visitor)
        inline_expressions_dict = inline_expressions_inside_equations_block_collector_visitor.inline_expressions_to_variables
        
        # filter for cm_p_open_{channelType}
        relevant_inline_expressions = defaultdict(lambda:list())
        for expression, variables in inline_expressions_dict.items():
            inline_expression_name = expression.variable_name
            if inline_expression_name.startswith(cls.inline_expression_prefix):
                relevant_inline_expressions[expression] = variables
                
        return relevant_inline_expressions
    
    @classmethod
    def cm_expression_to_channel_name(cls, expr):
        assert(isinstance(expr, ASTInlineExpression))
        return expr.variable_name[len(cls.inline_expression_prefix):].strip(cls.padding_character)

    # extract channel name from inline expression name
    # i.e  cm_p_open_Na -> channel name is Na
    @classmethod
    def extract_pure_cm_variable_name(cls, varname, ic_name):
        varname = varname.strip(cls.padding_character)
        assert(varname.endswith(ic_name))
        return varname[:-len(ic_name)].strip(cls.padding_character)
    
    @classmethod
    def getExpectedGbarName(cls, ion_channel_name):
        return "gbar"+cls.padding_character+ion_channel_name+cls.padding_character
    
    @classmethod
    def getExpectedEquilibirumVarName(cls, ion_channel_name):
        return "e"+cls.padding_character+ion_channel_name+cls.padding_character
    
    @classmethod
    def getExpectedTauFunctionName(cls, ion_channel_name, pure_cm_variable_name):
        return cls.padding_character+"tau"+cls.padding_character+pure_cm_variable_name+cls.padding_character+ion_channel_name
    
    
    @classmethod
    def getExpectedInfFunctionName(cls, ion_channel_name, pure_cm_variable_name):
        return cls.padding_character+pure_cm_variable_name+cls.padding_character+"inf"+cls.padding_character + ion_channel_name
    
    
    # calculate function names that must be implemented
    # i.e 
    # m_Na_**3 * h_Na_**1 
    # leads to expect
    # _m_inf_Na(v_comp real) real
    # _tau_m_Na(v_comp real) real
    @classmethod
    def getExpectedFunctionNamesForChannels(cls, relevant_inline_expressions_to_variables):
        expected_function_names_to_channels = defaultdict()
        
        for cm_expression, variables in relevant_inline_expressions_to_variables.items():
            ion_channel_name = cls.cm_expression_to_channel_name(cm_expression)

            for variable_used in variables:
                variable_name = variable_used.name.strip(cls.padding_character)
                if not variable_name.endswith(ion_channel_name):
                    continue
                
                pure_cm_variable_name = cls.extract_pure_cm_variable_name(variable_name, ion_channel_name)
                
                expected_inf_function_name = cls.getExpectedInfFunctionName(ion_channel_name, pure_cm_variable_name)
                expected_function_names_to_channels[expected_inf_function_name] = ion_channel_name
                expected_tau_function_name = cls.getExpectedTauFunctionName(ion_channel_name, pure_cm_variable_name)
                expected_function_names_to_channels[expected_tau_function_name] = ion_channel_name
        
        return expected_function_names_to_channels

    @classmethod
    def getAndCheckExpectedVariableNamesAndReasons(cls, node, relevant_inline_expressions_to_variables):
        expected_initial_variables_to_reason = defaultdict()

        for cm_expression, variables in relevant_inline_expressions_to_variables.items():
            ion_channel_name = cls.cm_expression_to_channel_name(cm_expression)
            
            expected_initial_variables_to_reason[cls.getExpectedGbarName(ion_channel_name)] = cm_expression
            expected_initial_variables_to_reason[cls.getExpectedEquilibirumVarName(ion_channel_name)] = cm_expression
            
            for variable_used in variables:
                variable_name = variable_used.name.strip(cls.padding_character)
                if not variable_name.endswith(ion_channel_name):
                    code, message = Messages.get_cm_inline_expression_variable_name_must_end_with_channel_name(cm_expression, variable_name, ion_channel_name)
                    Logger.log_message(code=code, message=message, error_position=variable_used.get_source_position(), log_level=LoggingLevel.ERROR, node=node)
                    continue

                expected_initial_variables_to_reason[variable_used.name] = variable_used 
                
        return expected_initial_variables_to_reason   

    @classmethod
    def check_co_co(cls, node: ASTNode, after_ast_rewrite: bool):
        """
        Checks if this coco applies for the handed over neuron. 
        Models which do not have inline cm_p_open_{channelType}
        inside ASTEquationsBlock are not relevant
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        
        # get inline cm_p_open_{channelType} expressions
        relevant_inline_expressions_to_variables = cls.getRelevantInlineExpressions(node)

        # get a dict {expected_function_name : channel_name_that_caused_expectation}
        expected_function_names_for_channels = cls.getExpectedFunctionNamesForChannels(relevant_inline_expressions_to_variables)

        # get functions and collect their names    
        declared_functions = node.get_functions()
        declared_function_names = [declared_function.name for declared_function in declared_functions]
        
        # check for missing functions
        for expected_function_name, ion_channel_name in expected_function_names_for_channels.items():
            if expected_function_name not in declared_function_names:
                code, message = Messages.get_expected_cm_function_missing(ion_channel_name, expected_function_name)
                Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR, node=node)

        # maybe check if function has exactly one argument, but may not be needed to do
        # relevant_function_names = [f for f in declared_functions if f.name in expected_function_names_for_channels.keys()]    
        
        # get expected variables and also throw errors if naming expecations not met
        # a dict {expected_variable_name : ASTVariable_or_ASTInlineExpression_that_caused_expectation}
        expected_initial_variables_to_reason = cls.getAndCheckExpectedVariableNamesAndReasons(node, relevant_inline_expressions_to_variables)
        
        #now check for existence of expected_initial_variables_to_reason
        initial_values_missing_visitor = InitialValueMissingVisitor(expected_initial_variables_to_reason)
        node.accept(initial_values_missing_visitor)


class InitialValueMissingVisitor(ASTVisitor):

    def __init__(self, expected_initial_variables_to_reason):
        super(InitialValueMissingVisitor, self).__init__()
        self.expected_initial_variables_to_reason = expected_initial_variables_to_reason
        self.not_yet_found_variables = set(expected_initial_variables_to_reason.keys())
        
        self.inside_block_with_variables = False
        self.inside_declaration = False
        self.current_block_with_variables = None
        
    def visit_declaration(self, node):
        self.inside_declaration = True
        
    def endvisit_declaration(self, node):
        self.inside_declaration = False
        
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

    def endvisit_neuron(self, node):
        if self.not_yet_found_variables:
            code, message = Messages.get_expected_cm_initial_values_missing(self.not_yet_found_variables, self.expected_initial_variables_to_reason)
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

