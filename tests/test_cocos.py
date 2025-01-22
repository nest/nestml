# -*- coding: utf-8 -*-
#
# test_cocos.py
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

from typing import Optional

import os
import pytest

from pynestml.meta_model.ast_model import ASTModel
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.predefined_units import PredefinedUnits
from pynestml.symbols.predefined_variables import PredefinedVariables
from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.utils.logger import LoggingLevel, Logger
from pynestml.utils.model_parser import ModelParser


class TestCoCos:

    @pytest.fixture(scope="module", autouse=True)
    def setUp(self):
        SymbolTable.initialize_symbol_table(
            ASTSourceLocation(
                start_line=0,
                start_column=0,
                end_line=0,
                end_column=0))
        PredefinedUnits.register_units()
        PredefinedTypes.register_types()
        PredefinedVariables.register_variables()
        PredefinedFunctions.register_functions()

    def test_invalid_element_defined_after_usage(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoVariableDefinedAfterUsage.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_element_defined_after_usage(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoVariableDefinedAfterUsage.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_element_in_same_line(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoElementInSameLine.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_element_in_same_line(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoElementInSameLine.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_integrate_odes_called_if_equations_defined(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoIntegrateOdesCalledIfEquationsDefined.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_integrate_odes_called_if_equations_defined(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoIntegrateOdesCalledIfEquationsDefined.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_element_not_defined_in_scope(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoVariableNotDefined.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 6

    def test_valid_element_not_defined_in_scope(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoVariableNotDefined.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_variable_with_same_name_as_unit(self):
        Logger.set_logging_level(LoggingLevel.NO)
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoVariableWithSameNameAsUnit.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.WARNING)) == 3

    def test_invalid_variable_redeclaration(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoVariableRedeclared.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_variable_redeclaration(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoVariableRedeclared.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_each_block_unique(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoEachBlockUnique.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_each_block_unique(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoEachBlockUnique.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_function_unique_and_defined(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoFunctionNotUnique.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 8

    def test_valid_function_unique_and_defined(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoFunctionNotUnique.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_inline_expressions_have_rhs(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoInlineExpressionHasNoRhs.nestml'))
        assert model is None    # parse error

    def test_valid_inline_expressions_have_rhs(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoInlineExpressionHasNoRhs.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_inline_expression_has_several_lhs(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoInlineExpressionWithSeveralLhs.nestml'))
        assert model is None    # parse error

    def test_valid_inline_expression_has_several_lhs(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoInlineExpressionWithSeveralLhs.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_no_values_assigned_to_input_ports(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoValueAssignedToInputPort.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_no_values_assigned_to_input_ports(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoValueAssignedToInputPort.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_order_of_equations_correct(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoNoOrderOfEquations.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_order_of_equations_correct(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoNoOrderOfEquations.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_numerator_of_unit_one(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoUnitNumeratorNotOne.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_numerator_of_unit_one(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoUnitNumeratorNotOne.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_names_of_neurons_unique(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoMultipleNeuronsWithEqualName.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_names_of_neurons_unique(self):
        self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')),  'CoCoMultipleNeuronsWithEqualName.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(None, LoggingLevel.ERROR)) == 0

    def test_invalid_no_nest_collision(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoNestNamespaceCollision.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_no_nest_collision(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoNestNamespaceCollision.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_redundant_input_port_keywords_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoInputPortWithRedundantTypes.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_redundant_input_port_keywords_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoInputPortWithRedundantTypes.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_parameters_assigned_only_in_parameters_block(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoParameterAssignedOutsideBlock.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_parameters_assigned_only_in_parameters_block(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoParameterAssignedOutsideBlock.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_inline_expressions_assigned_only_in_declaration(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoAssignmentToInlineExpression.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_invalid_internals_assigned_only_in_internals_block(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoInternalAssignedOutsideBlock.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_internals_assigned_only_in_internals_block(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoInternalAssignedOutsideBlock.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_function_with_wrong_arg_number_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoFunctionCallNotConsistentWrongArgNumber.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_function_with_wrong_arg_number_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoFunctionCallNotConsistentWrongArgNumber.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_init_values_have_rhs_and_ode(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoInitValuesWithoutOde.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.WARNING)) == 2

    def test_valid_init_values_have_rhs_and_ode(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoInitValuesWithoutOde.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.WARNING)) == 3

    def test_invalid_incorrect_return_stmt_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoIncorrectReturnStatement.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 8

    def test_valid_incorrect_return_stmt_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoIncorrectReturnStatement.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_ode_vars_outside_init_block_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoOdeVarNotInInitialValues.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_ode_vars_outside_init_block_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoOdeVarNotInInitialValues.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_convolve_correctly_defined(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoConvolveNotCorrectlyProvided.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_convolve_correctly_defined(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoConvolveNotCorrectlyProvided.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_vector_in_non_vector_declaration_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoVectorInNonVectorDeclaration.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_vector_in_non_vector_declaration_detected(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoVectorInNonVectorDeclaration.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_vector_parameter_declaration(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoVectorParameterDeclaration.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_vector_parameter_declaration(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoVectorParameterDeclaration.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_vector_parameter_type(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoVectorParameterType.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_vector_parameter_type(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoVectorParameterType.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_vector_parameter_size(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoVectorDeclarationSize.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_vector_parameter_size(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoVectorDeclarationSize.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_convolve_correctly_parameterized(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoConvolveNotCorrectlyParametrized.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_convolve_correctly_parameterized(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoConvolveNotCorrectlyParametrized.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_invariant_correctly_typed(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoInvariantNotBool.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_invariant_correctly_typed(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoInvariantNotBool.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_expression_correctly_typed(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoIllegalExpression.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_expression_correctly_typed(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoIllegalExpression.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_compound_expression_correctly_typed(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CompoundOperatorWithDifferentButCompatibleUnits.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 10

    def test_valid_compound_expression_correctly_typed(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CompoundOperatorWithDifferentButCompatibleUnits.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_ode_correctly_typed(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoOdeIncorrectlyTyped.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) > 0

    def test_valid_ode_correctly_typed(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoOdeCorrectlyTyped.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_output_block_defined_if_emit_call(self):
        """test that an error is raised when the emit_spike() function is called by the neuron, but an output block is not defined"""
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoOutputPortDefinedIfEmitCall.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) > 0

    def test_invalid_output_port_defined_if_emit_call(self):
        """test that an error is raised when the emit_spike() function is called by the neuron, but a spiking output port is not defined"""
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoOutputPortDefinedIfEmitCall-2.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) > 0

    def test_valid_output_port_defined_if_emit_call(self):
        """test that no error is raised when the output block is missing, but not emit_spike() functions are called"""
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoOutputPortDefinedIfEmitCall.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_output_port_type_if_emit_call(self):
        """test that an error is raised when the emit_spike() function is called with different parameter types than are defined in the spiking output port"""
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoOutputPortTypeIfEmitCall.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) > 0

    def test_invalid_output_port_type_if_emit_call(self):
        """test that an error is raised when the emit_spike() function is called with different parameter types than are defined in the spiking output port"""
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoOutputPortTypeIfEmitCall-2.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) > 0

    def test_valid_output_port_type_if_emit_call(self):
        """test that a warning is raised when the emit_spike() function is called with parameter types castable to the types defined in the spiking output port"""
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoOutputPortTypeIfEmitCall-3.nestml'))
        assert model is not None
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.WARNING)) > 0

    def test_invalid_output_port_type_continuous(self):
        """test that an error is raised when a continous-time output port is defined as having attributes."""
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoOutputPortTypeContinuous.nestml'))
        assert model is None    # should result in a parse error

    def test_valid_coco_kernel_type(self):
        """
        Test the functionality of CoCoKernelType.
        """
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoKernelType.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_coco_kernel_type(self):
        """
        Test the functionality of CoCoKernelType.
        """
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoKernelType.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_invalid_coco_kernel_type_initial_values(self):
        """
        Test the functionality of CoCoKernelType.
        """
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoKernelTypeInitialValues.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 4

    def test_valid_coco_state_variables_initialized(self):
        """
        Test that the CoCo condition is applicable for all the variables in the state block initialized with a value
        """
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoStateVariablesInitialized.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_coco_state_variables_initialized(self):
        """
        Test that the CoCo condition is applicable for all the variables in the state block not initialized
        """
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoStateVariablesInitialized.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_invalid_co_co_priorities_correctly_specified(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoPrioritiesCorrectlySpecified.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def test_valid_co_co_priorities_correctly_specified(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoPrioritiesCorrectlySpecified.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_co_co_resolution_legally_used(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoResolutionLegallyUsed.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 2

    def test_valid_co_co_resolution_legally_used(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoResolutionLegallyUsed.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_valid_co_co_vector_input_port(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'valid')), 'CoCoVectorInputPortSizeAndType.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 0

    def test_invalid_co_co_vector_input_port(self):
        model = self._parse_and_validate_model(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'invalid')), 'CoCoVectorInputPortSizeAndType.nestml'))
        assert len(Logger.get_all_messages_of_level_and_or_node(model, LoggingLevel.ERROR)) == 1

    def _parse_and_validate_model(self, fname: str) -> Optional[str]:
        from pynestml.frontend.pynestml_frontend import generate_target

        Logger.init_logger(LoggingLevel.DEBUG)

        generate_target(input_path=fname, target_platform="NONE", logging_level="DEBUG")

        ast_compilation_unit = ModelParser.parse_file(fname)
        if ast_compilation_unit is None or len(ast_compilation_unit.get_model_list()) == 0:
            return None

        model: ASTModel = ast_compilation_unit.get_model_list()[0]
        model_name = model.get_name()

        return model_name
