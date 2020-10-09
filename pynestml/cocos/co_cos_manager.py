# -*- coding: utf-8 -*-
#
# co_cos_manager.py
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
from pynestml.cocos.co_co_all_variables_defined import CoCoAllVariablesDefined
from pynestml.cocos.co_co_buffer_not_assigned import CoCoBufferNotAssigned
from pynestml.cocos.co_co_convolve_cond_correctly_built import CoCoConvolveCondCorrectlyBuilt
from pynestml.cocos.co_co_correct_numerator_of_unit import CoCoCorrectNumeratorOfUnit
from pynestml.cocos.co_co_correct_order_in_equation import CoCoCorrectOrderInEquation
from pynestml.cocos.co_co_current_buffers_not_specified import CoCoCurrentBuffersNotSpecified
from pynestml.cocos.co_co_each_block_unique_and_defined import CoCoEachBlockUniqueAndDefined
from pynestml.cocos.co_co_equations_only_for_init_values import CoCoEquationsOnlyForInitValues
from pynestml.cocos.co_co_function_calls_consistent import CoCoFunctionCallsConsistent
from pynestml.cocos.co_co_function_have_rhs import CoCoFunctionHaveRhs
from pynestml.cocos.co_co_function_max_one_lhs import CoCoFunctionMaxOneLhs
from pynestml.cocos.co_co_function_unique import CoCoFunctionUnique
from pynestml.cocos.co_co_illegal_expression import CoCoIllegalExpression
from pynestml.cocos.co_co_init_vars_with_odes_provided import CoCoInitVarsWithOdesProvided
from pynestml.cocos.co_co_invariant_is_boolean import CoCoInvariantIsBoolean
from pynestml.cocos.co_co_neuron_name_unique import CoCoNeuronNameUnique
from pynestml.cocos.co_co_no_nest_name_space_collision import CoCoNoNestNameSpaceCollision
from pynestml.cocos.co_co_no_kernels_except_in_convolve import CoCoNoKernelsExceptInConvolve
from pynestml.cocos.co_co_no_two_neurons_in_set_of_compilation_units import CoCoNoTwoNeuronsInSetOfCompilationUnits
from pynestml.cocos.co_co_odes_have_consistent_units import CoCoOdesHaveConsistentUnits
from pynestml.cocos.co_co_kernel_type import CoCoKernelType
from pynestml.cocos.co_co_simple_delta_function import CoCoSimpleDeltaFunction
from pynestml.cocos.co_co_ode_functions_have_consistent_units import CoCoOdeFunctionsHaveConsistentUnits
from pynestml.cocos.co_co_output_port_defined_if_emit_call import CoCoOutputPortDefinedIfEmitCall
from pynestml.cocos.co_co_buffer_data_type import CoCoBufferDataType
from pynestml.cocos.co_co_parameters_assigned_only_in_parameter_block import \
    CoCoParametersAssignedOnlyInParameterBlock
from pynestml.cocos.co_co_sum_has_correct_parameter import CoCoSumHasCorrectParameter
from pynestml.cocos.co_co_buffer_qualifier_unique import CoCoBufferQualifierUnique
from pynestml.cocos.co_co_user_defined_function_correctly_defined import CoCoUserDefinedFunctionCorrectlyDefined
from pynestml.cocos.co_co_variable_once_per_scope import CoCoVariableOncePerScope
from pynestml.cocos.co_co_vector_variable_in_non_vector_declaration import CoCoVectorVariableInNonVectorDeclaration
from pynestml.cocos.co_co_function_argument_template_types_consistent import CoCoFunctionArgumentTemplateTypesConsistent
from pynestml.meta_model.ast_neuron import ASTNeuron


class CoCosManager(object):
    """
    This class provides a set of context conditions which have to hold for each neuron instance.
    """

    @classmethod
    def check_function_defined(cls, neuron):
        """
        Checks for the handed over neuron that each used function it is defined.
        """
        CoCoFunctionUnique.check_co_co(neuron)

    @classmethod
    def check_each_block_unique_and_defined(cls, neuron):
        """
        Checks if in the handed over neuron each block ist defined at most once and mandatory blocks are defined.
        :param neuron: a single neuron instance
        :type neuron: ast_neuron
        """
        CoCoEachBlockUniqueAndDefined.check_co_co(neuron)

    @classmethod
    def check_function_declared_and_correctly_typed(cls, neuron):
        """
        Checks if in the handed over neuron all function calls use existing functions and the arguments are
        correctly typed.
        :param neuron: a single neuron instance
        :type neuron: ast_neuron
        """
        CoCoFunctionCallsConsistent.check_co_co(neuron)

    @classmethod
    def check_variables_unique_in_scope(cls, neuron):
        """
        Checks that all variables have been declared at most once per scope.
        :param neuron: a single neuron instance
        :type neuron: ast_neuron
        """
        CoCoVariableOncePerScope.check_co_co(neuron)

    @classmethod
    def check_variables_defined_before_usage(cls, neuron):
        """
        Checks that all variables are defined before being used.
        :param neuron: a single neuron.
        :type neuron: ast_neuron
        """
        CoCoAllVariablesDefined.check_co_co(neuron)

    @classmethod
    def check_functions_have_rhs(cls, neuron):
        """
        Checks that all functions have a right-hand side, e.g., function V_reset mV = V_m - 55mV
        :param neuron: a single neuron object
        :type neuron: ast_neuron
        """
        CoCoFunctionHaveRhs.check_co_co(neuron)

    @classmethod
    def check_function_has_max_one_lhs(cls, neuron):
        """
        Checks that all functions have exactly one left-hand side, e.g., function V_reset mV = V_m - 55mV
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoFunctionMaxOneLhs.check_co_co(neuron)

    @classmethod
    def check_no_values_assigned_to_buffers(cls, neuron):
        """
        Checks that no values are assigned to buffers.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoBufferNotAssigned.check_co_co(neuron)

    @classmethod
    def check_order_of_equations_correct(cls, neuron):
        """
        Checks that all equations specify the order of the variable.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoCorrectOrderInEquation.check_co_co(neuron)

    @classmethod
    def check_numerator_of_unit_is_one_if_numeric(cls, neuron):
        """
        Checks that all units which have a numeric numerator use 1.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoCorrectNumeratorOfUnit.check_co_co(neuron)

    @classmethod
    def check_neuron_names_unique(cls, compilation_unit):
        """
        Checks that all declared neurons in a compilation unit have a unique name.
        :param compilation_unit: a single compilation unit.
        :type compilation_unit: ASTCompilationUnit
        """
        CoCoNeuronNameUnique.check_co_co(compilation_unit)

    @classmethod
    def check_no_nest_namespace_collisions(cls, neuron):
        """
        Checks that all units which have a numeric numerator use 1.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoNoNestNameSpaceCollision.check_co_co(neuron)

    @classmethod
    def check_buffer_qualifier_unique(cls, neuron):
        """
        Checks that all spike buffers have a unique type, i.e., no buffer is defined with redundant keywords.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoBufferQualifierUnique.check_co_co(neuron)

    @classmethod
    def check_kernel_type(cls, neuron: ASTNeuron) -> None:
        """
        Checks that all defined kernels have type real.
        """
        CoCoKernelType.check_co_co(neuron)

    @classmethod
    def check_parameters_not_assigned_outside_parameters_block(cls, neuron):
        """
        Checks that parameters are not assigned outside the parameters block.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoParametersAssignedOnlyInParameterBlock.check_co_co(neuron)

    @classmethod
    def check_current_buffers_no_keywords(cls, neuron):
        """
        Checks that input current buffers have not been specified with keywords, e.g., inhibitory.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoCurrentBuffersNotSpecified.check_co_co(neuron)

    @classmethod
    def check_output_port_defined_if_emit_call(cls, neuron):
        """
        Checks that if emit_spike() function is called, an spiking output port is defined.
        :param neuron: a single neuron object.
        :type neuron: ASTNeuron
        """
        CoCoOutputPortDefinedIfEmitCall.check_co_co(neuron)

    @classmethod
    def check_odes_have_consistent_units(cls, neuron):
        """
        Checks that all ODE lhs and rhs have consistent units.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoOdesHaveConsistentUnits.check_co_co(neuron)

    @classmethod
    def check_ode_functions_have_consistent_units(cls, neuron):
        """
        Checks that all ODE function lhs and rhs have consistent units.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoOdeFunctionsHaveConsistentUnits.check_co_co(neuron)

    @classmethod
    def check_buffer_types_are_correct(cls, neuron):
        """
        Checks that input buffers have specified the data type if required an no data type if not allowed.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoBufferDataType.check_co_co(neuron)

    @classmethod
    def check_init_vars_with_odes_provided(cls, neuron):
        """
        Checks that all initial variables have a rhs and are provided with the corresponding ode declaration.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoInitVarsWithOdesProvided.check_co_co(neuron)

    @classmethod
    def check_user_defined_function_correctly_built(cls, neuron):
        """
        Checks that all user defined functions are correctly constructed, i.e., have a return statement if declared
        and that the type corresponds to the declared one.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoUserDefinedFunctionCorrectlyDefined.check_co_co(neuron)

    @classmethod
    def check_initial_ode_initial_values(cls, neuron):
        """
        Checks if variables of odes are declared in the initial_values block.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoEquationsOnlyForInitValues.check_co_co(neuron)

    @classmethod
    def check_convolve_cond_curr_is_correct(cls, neuron):
        """
        Checks if all convolve rhs are correctly provided with arguments.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoConvolveCondCorrectlyBuilt.check_co_co(neuron)

    @classmethod
    def check_correct_usage_of_kernels(cls, neuron):
        """
        Checks if all kernels are only used in convolve.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoNoKernelsExceptInConvolve.check_co_co(neuron)

    @classmethod
    def check_not_two_neurons_across_units(cls, compilation_units):
        """
        Checks if in a set of compilation units, two neurons have the same name.
        :param compilation_units: a  list of compilation units
        :type compilation_units: list(ASTNestMLCompilationUnit)
        """
        CoCoNoTwoNeuronsInSetOfCompilationUnits.check_co_co(compilation_units)

    @classmethod
    def check_invariant_type_correct(cls, neuron):
        """
        Checks if all invariants are of type boolean.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoInvariantIsBoolean.check_co_co(neuron)

    @classmethod
    def check_vector_in_non_vector_declaration_detected(cls, neuron):
        """
        Checks if no declaration a vector value is added to a non vector one.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoVectorVariableInNonVectorDeclaration.check_co_co(neuron)

    @classmethod
    def check_sum_has_correct_parameter(cls, neuron):
        """
        Checks that all convolve function calls have variables as arguments.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoSumHasCorrectParameter.check_co_co(neuron)

    @classmethod
    def check_expression_correct(cls, neuron):
        """
        Checks that all rhs in the model are correctly constructed, e.g. type(lhs)==type(rhs).
        :param neuron: a single neuron
        :type neuron: ast_neuron
        """
        CoCoIllegalExpression.check_co_co(neuron)

    @classmethod
    def check_simple_delta_function(cls, neuron: ASTNeuron) -> None:
        CoCoSimpleDeltaFunction.check_co_co(neuron)

    @classmethod
    def post_symbol_table_builder_checks(cls, neuron: ASTNeuron, after_ast_rewrite: bool = False):
        """
        Checks all context conditions.
        :param neuron: a single neuron object.
        :type neuron: ASTNeuron
        """
        cls.check_function_defined(neuron)
        cls.check_function_declared_and_correctly_typed(neuron)
        cls.check_variables_unique_in_scope(neuron)
        cls.check_variables_defined_before_usage(neuron)
        cls.check_functions_have_rhs(neuron)
        cls.check_function_has_max_one_lhs(neuron)
        cls.check_no_values_assigned_to_buffers(neuron)
        cls.check_order_of_equations_correct(neuron)
        cls.check_numerator_of_unit_is_one_if_numeric(neuron)
        cls.check_no_nest_namespace_collisions(neuron)
        cls.check_buffer_qualifier_unique(neuron)
        cls.check_parameters_not_assigned_outside_parameters_block(neuron)
        cls.check_current_buffers_no_keywords(neuron)
        cls.check_buffer_types_are_correct(neuron)
        cls.check_user_defined_function_correctly_built(neuron)
        cls.check_initial_ode_initial_values(neuron)
        cls.check_kernel_type(neuron)
        cls.check_convolve_cond_curr_is_correct(neuron)
        cls.check_output_port_defined_if_emit_call(neuron)
        if not after_ast_rewrite:
            # units might be incorrect due to e.g. refactoring convolve call (Real type assigned)
            cls.check_odes_have_consistent_units(neuron)
            cls.check_ode_functions_have_consistent_units(neuron)        # ODE functions have been removed at this point
            cls.check_correct_usage_of_kernels(neuron)
        cls.check_invariant_type_correct(neuron)
        cls.check_vector_in_non_vector_declaration_detected(neuron)
        cls.check_sum_has_correct_parameter(neuron)
        cls.check_expression_correct(neuron)
        cls.check_simple_delta_function(neuron)
        cls.check_function_argument_template_types_consistent(neuron)
        return

    @classmethod
    def post_ode_specification_checks(cls, neuron):
        """
        Checks the following constraints:
            cls.check_init_vars_with_odes_provided
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        cls.check_init_vars_with_odes_provided(neuron)

    @classmethod
    def check_function_argument_template_types_consistent(cls, neuron):
        """
        Checks if no declaration a vector value is added to a non vector one.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoFunctionArgumentTemplateTypesConsistent.check_co_co(neuron)
