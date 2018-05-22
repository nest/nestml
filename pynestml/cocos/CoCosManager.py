#
# CoCosManager.py
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
from pynestml.cocos.CoCoAllVariablesDefined import CoCoAllVariablesDefined
from pynestml.cocos.CoCoBufferNotAssigned import CoCoBufferNotAssigned
from pynestml.cocos.CoCoConvolveCondCorrectlyBuilt import CoCoConvolveCondCorrectlyBuilt
from pynestml.cocos.CoCoCorrectNumeratorOfUnit import CoCoCorrectNumeratorOfUnit
from pynestml.cocos.CoCoCorrectOrderInEquation import CoCoCorrectOrderInEquation
from pynestml.cocos.CoCoCurrentBuffersNotSpecified import CoCoCurrentBuffersNotSpecified
from pynestml.cocos.CoCoEachBlockUniqueAndDefined import CoCoEachBlockUniqueAndDefined
from pynestml.cocos.CoCoEquationsOnlyForInitValues import CoCoEquationsOnlyForInitValues
from pynestml.cocos.CoCoFunctionCallsConsistent import CoCoFunctionCallsConsistent
from pynestml.cocos.CoCoFunctionHaveRhs import CoCoFunctionHaveRhs
from pynestml.cocos.CoCoFunctionMaxOneLhs import CoCoFunctionMaxOneLhs
from pynestml.cocos.CoCoFunctionUnique import CoCoFunctionUnique
from pynestml.cocos.CoCoIllegalExpression import CoCoIllegalExpression
from pynestml.cocos.CoCoInitVarsWithOdesProvided import CoCoInitVarsWithOdesProvided
from pynestml.cocos.CoCoInvariantIsBoolean import CoCoInvariantIsBoolean
from pynestml.cocos.CoCoNeuronNameUnique import CoCoNeuronNameUnique
from pynestml.cocos.CoCoNoNestNameSpaceCollision import CoCoNoNestNameSpaceCollision
from pynestml.cocos.CoCoNoShapesExceptInConvolve import CoCoNoShapesExceptInConvolve
from pynestml.cocos.CoCoNoTwoNeuronsInSetOfCompilationUnits import CoCoNoTwoNeuronsInSetOfCompilationUnits
from pynestml.cocos.CoCoOnlySpikeBufferDataTypes import CoCoOnlySpikeBufferDataTypes
from pynestml.cocos.CoCoParametersAssignedOnlyInParameterBlock import \
    CoCoParametersAssignedOnlyInParameterBlock
from pynestml.cocos.CoCoSumHasCorrectParameter import CoCoSumHasCorrectParameter
from pynestml.cocos.CoCoTypeOfBufferUnique import CoCoTypeOfBufferUnique
from pynestml.cocos.CoCoUserDefinedFunctionCorrectlyDefined import CoCoUserDefinedFunctionCorrectlyDefined
from pynestml.cocos.CoCoVariableOncePerScope import CoCoVariableOncePerScope
from pynestml.cocos.CoCoVectorVariableInNonVectorDeclaration import CoCoVectorVariableInNonVectorDeclaration


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
    def check_type_of_buffer_unique(cls, neuron):
        """
        Checks that all spike buffers have a unique type, i.e., no buffer is defined with redundant keywords.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoTypeOfBufferUnique.check_co_co(neuron)

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
    def check_buffer_types_are_correct(cls, neuron):
        """
        Checks that input buffers have specified the data type if required an no data type if not allowed.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoOnlySpikeBufferDataTypes.check_co_co(neuron)

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
        Checks if all convolve/curr_sum/cond_sum rhs are correctly provided with arguments.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoConvolveCondCorrectlyBuilt.check_co_co(neuron)

    @classmethod
    def check_correct_usage_of_shapes(cls, neuron):
        """
        Checks if all shapes are only used in cond_sum, cur_sum, convolve.
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
        """
        CoCoNoShapesExceptInConvolve.check_co_co(neuron)

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
        Checks that all cond_sum,cur_sum and convolve have variables as arguments.
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
    def post_symbol_table_builder_checks(cls, neuron):
        """
        Checks the following constraints:
            cls.check_function_defined(_neuron)
            cls.check_function_declared_and_correctly_typed(_neuron)
            cls.check_variables_unique_in_scope(_neuron)
            cls.check_variables_defined_before_usage(_neuron)
            cls.check_functions_have_rhs(_neuron)
            cls.check_function_has_max_one_lhs(_neuron)
            cls.check_no_values_assigned_to_buffers(_neuron)
            cls.check_order_of_equations_correct(_neuron)
            cls.check_numerator_of_unit_is_one_if_numeric(_neuron)
            cls.check_no_nest_namespace_collisions(_neuron)
            cls.check_type_of_buffer_unique(_neuron)
            cls.check_parameters_not_assigned_outside_parameters_block(_neuron)
            cls.check_current_buffers_no_keywords(_neuron)
            cls.check_buffer_types_are_correct(_neuron)
            cls.checkUsedDefinedFunctionCorrectlyBuilt(_neuron)
            cls.check_initial_ode_initial_values(_neuron)
            cls.check_invariant_type_correct(_neuron)
            cls.check_vector_in_non_vector_declaration_detected(_neuron)
            cls.check_sum_has_correct_parameter(_neuron)
            cls.check_expression_correct(_neuron)
        :param neuron: a single neuron object.
        :type neuron: ast_neuron
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
        cls.check_type_of_buffer_unique(neuron)
        cls.check_parameters_not_assigned_outside_parameters_block(neuron)
        cls.check_current_buffers_no_keywords(neuron)
        cls.check_buffer_types_are_correct(neuron)
        cls.check_user_defined_function_correctly_built(neuron)
        cls.check_initial_ode_initial_values(neuron)
        cls.check_convolve_cond_curr_is_correct(neuron)
        cls.check_correct_usage_of_shapes(neuron)
        cls.check_invariant_type_correct(neuron)
        cls.check_vector_in_non_vector_declaration_detected(neuron)
        cls.check_sum_has_correct_parameter(neuron)
        cls.check_expression_correct(neuron)
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
