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
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import BlockType
from pynestml.utils.logger import Logger, LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.visitors.ast_visitor import ASTVisitor

from collections import defaultdict


class CoCoCmFunctionsAndVariablesDefined(CoCo):
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
    """

    @classmethod
    def check_co_co(cls, node: ASTNode, after_ast_rewrite: bool):
        """
        Checks if this coco applies for the handed over neuron. 
        Models which do not have cm_p_open_{channelType}
        inside ASTEquationsBlock are not relevant
        :param node: a single neuron instance.
        :type node: ast_neuron
        """
        
        inline_expression_prefix = "cm_p_open_"
        
        # search for inline expressions inside equations block
        inline_expressions_inside_equations_block_collector_visitor = ASTInlineExpressionInsideEquationsBlockCollectorVisitor()
        node.accept(inline_expressions_inside_equations_block_collector_visitor)
        inline_expressions_dict = inline_expressions_inside_equations_block_collector_visitor.inline_expressions_to_variables
        
        # filter for cm_p_open_{channelType}
        relevant_inline_expressions = defaultdict(lambda:list())
        for expression, variables in inline_expressions_dict.items():
            inline_expression_name = expression.variable_name
            if inline_expression_name.startswith(inline_expression_prefix):
                relevant_inline_expressions[expression] = variables
        
        # extract channel name from inline expression name
        # i.e  cm_p_open_Na -> channel name is _Na
        # then calculate function names that must be implemented
        # i.e 
        # m_Na_**3 * h_Na_**1 
        # leads to expect
        # _m_inf_Na(v_comp real) real
        # _tau_m_Na(v_comp real) real
        
        def cm_expression_to_channel_name(expr):
            return expr.variable_name[len(inline_expression_prefix):].strip("_")
        
        def get_pure_variable_name(varname, ic_name):
            varname = varname.strip("_")
            assert(varname.endswith(ic_name))
            return varname[:-len(ic_name)].strip("_")
        
        expected_initial_variables_to_reason = defaultdict(lambda:list())
        channel_names_to_expected_function_names = defaultdict(lambda:list())
        for cm_expression, variables in relevant_inline_expressions.items():
            ion_channel_name = cm_expression_to_channel_name(cm_expression)
            expected_initial_variables_to_reason["gbar_"+ion_channel_name+"_"] = cm_expression
            expected_initial_variables_to_reason["e_"+ion_channel_name+"_"] = cm_expression
            
            expected_function_names = []
            for variable_used in variables:
                variable_name = variable_used.name.strip("_")
                if not variable_name.endswith(ion_channel_name):
                    code, message = Messages.get_cm_inline_expression_variable_name_must_end_with_channel_name(cm_expression, variable_name, ion_channel_name)
                    Logger.log_message(code=code, message=message, error_position=variable_used.get_source_position(), log_level=LoggingLevel.ERROR, node=node)
                    continue

                expected_initial_variables_to_reason[variable_used.name] = variable_used    
                
                pure_variable_name = get_pure_variable_name(variable_name, ion_channel_name)
                expected_inf_function_name = "_"+pure_variable_name+"_inf_"+ion_channel_name
                expected_tau_function_name = "_tau_"+pure_variable_name+"_"+ion_channel_name
                expected_function_names.append(expected_inf_function_name)
                expected_function_names.append(expected_tau_function_name)
            channel_names_to_expected_function_names[ion_channel_name] = expected_function_names
        
        #get functions and collect their names    
        declared_functions = node.get_functions()
        declared_function_names = [declared_function.name for declared_function in declared_functions]
        
        for ion_channel_name, expected_function_names in channel_names_to_expected_function_names.items():
            for expected_function_name in expected_function_names:
                if expected_function_name not in declared_function_names:
                    code, message = Messages.get_expected_cm_function_missing(ion_channel_name, expected_function_name)
                    Logger.log_message(code=code, message=message, error_position=node.get_source_position(), log_level=LoggingLevel.ERROR, node=node)

        relevant_function_names = [f for f in declared_functions if f.name in expected_function_names]    
        #maybe check if function has exactly one argument, but may not be needed
        
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
        self.current_block_with_variables is not None:
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

