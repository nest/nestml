# -*- coding: utf-8 -*-
#
# cocos_test.py
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

from __future__ import print_function

import os
import unittest

from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.model_parser import ModelParser


class CoCosTest(unittest.TestCase):

    def setUp(self):
        Logger.init_logger(LoggingLevel.INFO)
        SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedVariables.register_variables()
        PredefinedFunctions.register_functions()

    def test_invalid_element_defined_after_usage(self):
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoVariableDefinedAfterUsage.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 2)

    def test_valid_element_defined_after_usage(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoVariableDefinedAfterUsage.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_element_in_same_line(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoElementInSameLine.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_element_in_same_line(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoElementInSameLine.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_element_not_defined_in_scope(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoVariableNotDefined.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0],
                                                                          LoggingLevel.ERROR)), 5)

    def test_valid_element_not_defined_in_scope(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoVariableNotDefined.nestml'))
        self.assertEqual(
            len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)),
            0)

    def test_variable_with_same_name_as_unit(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoVariableWithSameNameAsUnit.nestml'))
        self.assertEqual(
            len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.WARNING)),
            3)

    def test_invalid_variable_redeclaration(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoVariableRedeclared.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_variable_redeclaration(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoVariableRedeclared.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_each_block_unique(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoEachBlockUnique.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 2)

    def test_valid_each_block_unique(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoEachBlockUnique.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_function_unique_and_defined(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoFunctionNotUnique.nestml'))
        self.assertEqual(
            len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 4)

    def test_valid_function_unique_and_defined(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoFunctionNotUnique.nestml'))
        self.assertEqual(
            len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_inline_expressions_have_rhs(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoInlineExpressionHasNoRhs.nestml'))
        assert model is None

    def test_valid_inline_expressions_have_rhs(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoInlineExpressionHasNoRhs.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_inline_expression_has_several_lhs(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoInlineExpressionWithSeveralLhs.nestml'))
        assert model is None

    def test_valid_inline_expression_has_several_lhs(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoInlineExpressionWithSeveralLhs.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_no_values_assigned_to_buffers(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoValueAssignedToBuffer.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 2)

    def test_valid_no_values_assigned_to_buffers(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoValueAssignedToBuffer.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_order_of_equations_correct(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoNoOrderOfEquations.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 2)

    def test_valid_order_of_equations_correct(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoNoOrderOfEquations.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_numerator_of_unit_one(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoUnitNumeratorNotOne.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0],
                                                                          LoggingLevel.ERROR)), 2)

    def test_valid_numerator_of_unit_one(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoUnitNumeratorNotOne.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_names_of_neurons_unique(self):
        Logger.init_logger(LoggingLevel.INFO)
        ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoMultipleNeuronsWithEqualName.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(None, LoggingLevel.ERROR)), 1)

    def test_valid_names_of_neurons_unique(self):
        Logger.init_logger(LoggingLevel.INFO)
        ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoMultipleNeuronsWithEqualName.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(None, LoggingLevel.ERROR)), 0)

    def test_invalid_no_nest_collision(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoNestNamespaceCollision.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_no_nest_collision(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoNestNamespaceCollision.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_redundant_buffer_keywords_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoBufferWithRedundantTypes.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_redundant_buffer_keywords_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoBufferWithRedundantTypes.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_parameters_assigned_only_in_parameters_block(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoParameterAssignedOutsideBlock.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_parameters_assigned_only_in_parameters_block(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoParameterAssignedOutsideBlock.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_current_buffers_not_specified_with_keywords(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoCurrentBufferQualifierSpecified.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_current_buffers_not_specified(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoCurrentBufferQualifierSpecified.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_spike_buffer_without_datatype(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoSpikeBufferWithoutType.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 2)

    def test_valid_spike_buffer_without_datatype(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoSpikeBufferWithoutType.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_function_with_wrong_arg_number_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoFunctionCallNotConsistentWrongArgNumber.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_function_with_wrong_arg_number_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoFunctionCallNotConsistentWrongArgNumber.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_init_values_have_rhs_and_ode(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoInitValuesWithoutOde.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.WARNING)), 3)

    def test_valid_init_values_have_rhs_and_ode(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoInitValuesWithoutOde.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.WARNING)), 2)

    def test_invalid_incorrect_return_stmt_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoIncorrectReturnStatement.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 4)

    def test_valid_incorrect_return_stmt_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoIncorrectReturnStatement.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_ode_vars_outside_init_block_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoOdeVarNotInInitialValues.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_ode_vars_outside_init_block_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoOdeVarNotInInitialValues.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_convolve_correctly_defined(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoConvolveNotCorrectlyProvided.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0],
                                                                          LoggingLevel.ERROR)), 3)

    def test_valid_convolve_correctly_defined(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoConvolveNotCorrectlyProvided.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_vector_in_non_vector_declaration_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoVectorInNonVectorDeclaration.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_vector_in_non_vector_declaration_detected(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoVectorInNonVectorDeclaration.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_convolve_correctly_parameterized(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoConvolveNotCorrectlyParametrized.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_convolve_correctly_parameterized(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoConvolveNotCorrectlyParametrized.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0],
                                                                          LoggingLevel.ERROR)), 0)

    def test_invalid_invariant_correctly_typed(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoInvariantNotBool.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_valid_invariant_correctly_typed(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoInvariantNotBool.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_expression_correctly_typed(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoIllegalExpression.nestml'))
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0],
                                                                          LoggingLevel.ERROR)), 6)

    def test_valid_expression_correctly_typed(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoIllegalExpression.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_ode_correctly_typed(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoOdeIncorrectlyTyped.nestml'))
        self.assertTrue(len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0],
                                                                         LoggingLevel.ERROR)) > 0)

    def test_valid_ode_correctly_typed(self):
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoOdeCorrectlyTyped.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_output_block_defined_if_emit_call(self):
        """test that an error is raised when the emit_spike() function is called by the neuron, but an output block is not defined"""
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoOutputPortDefinedIfEmitCall.nestml'))
        self.assertTrue(len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0],
                                                                         LoggingLevel.ERROR)) > 0)

    def test_invalid_output_port_defined_if_emit_call(self):
        """test that an error is raised when the emit_spike() function is called by the neuron, but a spiking output port is not defined"""
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoOutputPortDefinedIfEmitCall-2.nestml'))
        self.assertTrue(len(Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0],
                                                                         LoggingLevel.ERROR)) > 0)

    def test_valid_output_port_defined_if_emit_call(self):
        """test that no error is raised when the output block is missing, but not emit_spike() functions are called"""
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoOutputPortDefinedIfEmitCall.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_valid_coco_kernel_type(self):
        """
        Test the functionality of CoCoKernelType.
        """
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),
                         'CoCoKernelType.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 0)

    def test_invalid_coco_kernel_type(self):
        """
        Test the functionality of CoCoKernelType.
        """
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoKernelType.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 1)

    def test_invalid_coco_kernel_type_initial_values(self):
        """
        Test the functionality of CoCoKernelType.
        """
        Logger.set_logging_level(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')),
                         'CoCoKernelTypeInitialValues.nestml'))
        self.assertEqual(len(
            Logger.get_all_messages_of_level_and_or_node(model.get_neuron_list()[0], LoggingLevel.ERROR)), 4)
