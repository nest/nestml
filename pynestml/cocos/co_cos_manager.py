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
from pynestml.cocos.co_co_input_port_not_assigned_to import CoCoInputPortNotAssignedTo
from pynestml.cocos.co_co_convolve_cond_correctly_built import CoCoConvolveCondCorrectlyBuilt
from pynestml.cocos.co_co_correct_numerator_of_unit import CoCoCorrectNumeratorOfUnit
from pynestml.cocos.co_co_correct_order_in_equation import CoCoCorrectOrderInEquation
from pynestml.cocos.co_co_continuous_input_port_not_qualified import CoCoContinuousInputPortNotQualified
from pynestml.cocos.co_co_each_neuron_block_unique_and_defined import CoCoEachNeuronBlockUniqueAndDefined
from pynestml.cocos.co_co_each_synapse_block_unique_and_defined import CoCoEachSynapseBlockUniqueAndDefined
from pynestml.cocos.co_co_equations_only_for_init_values import CoCoEquationsOnlyForInitValues
from pynestml.cocos.co_co_function_calls_consistent import CoCoFunctionCallsConsistent
from pynestml.cocos.co_co_function_unique import CoCoFunctionUnique
from pynestml.cocos.co_co_illegal_expression import CoCoIllegalExpression
from pynestml.cocos.co_co_inline_expressions_have_rhs import CoCoInlineExpressionsHaveRhs
from pynestml.cocos.co_co_inline_max_one_lhs import CoCoInlineMaxOneLhs
from pynestml.cocos.co_co_integrate_odes_called_if_equations_defined import CoCoIntegrateOdesCalledIfEquationsDefined
from pynestml.cocos.co_co_invariant_is_boolean import CoCoInvariantIsBoolean
from pynestml.cocos.co_co_neuron_name_unique import CoCoNeuronNameUnique
from pynestml.cocos.co_co_no_nest_name_space_collision import CoCoNoNestNameSpaceCollision
from pynestml.cocos.co_co_no_kernels_except_in_convolve import CoCoNoKernelsExceptInConvolve
from pynestml.cocos.co_co_no_duplicate_compilation_unit_names import CoCoNoDuplicateCompilationUnitNames
from pynestml.cocos.co_co_odes_have_consistent_units import CoCoOdesHaveConsistentUnits
from pynestml.cocos.co_co_kernel_type import CoCoKernelType
from pynestml.cocos.co_co_simple_delta_function import CoCoSimpleDeltaFunction
from pynestml.cocos.co_co_ode_functions_have_consistent_units import CoCoOdeFunctionsHaveConsistentUnits
from pynestml.cocos.co_co_output_port_defined_if_emit_call import CoCoOutputPortDefinedIfEmitCall
from pynestml.cocos.co_co_input_port_data_type import CoCoInputPortDataType
from pynestml.cocos.co_co_parameters_assigned_only_in_parameter_block import \
    CoCoParametersAssignedOnlyInParameterBlock
from pynestml.cocos.co_co_state_variables_initialized import CoCoStateVariablesInitialized
from pynestml.cocos.co_co_sum_has_correct_parameter import CoCoSumHasCorrectParameter
from pynestml.cocos.co_co_input_port_qualifier_unique import CoCoInputPortQualifierUnique
from pynestml.cocos.co_co_user_defined_function_correctly_defined import CoCoUserDefinedFunctionCorrectlyDefined
from pynestml.cocos.co_co_variable_once_per_scope import CoCoVariableOncePerScope
from pynestml.cocos.co_co_vector_variable_in_non_vector_declaration import CoCoVectorVariableInNonVectorDeclaration
from pynestml.cocos.co_co_function_argument_template_types_consistent import CoCoFunctionArgumentTemplateTypesConsistent
from pynestml.cocos.co_co_priorities_correctly_specified import CoCoPrioritiesCorrectlySpecified
from pynestml.meta_model.ast_neuron import ASTNeuron


class CoCosManager:
    """
    This class provides a set of context conditions which have to hold for each neuron instance.
    """

    @classmethod
    def check_function_defined(cls, neuron: ASTNeuron):
        """
        Checks for the handed over neuron that each used function it is defined.
        """
        CoCoFunctionUnique.check_co_co(neuron)

    @classmethod
    def check_each_block_unique_and_defined(cls, neuron: ASTNeuron):
        """
        Checks if in the handed over neuron each block is defined at most once and mandatory blocks are defined.
        :param neuron: a single neuron instance
        """
        CoCoEachNeuronBlockUniqueAndDefined.check_co_co(neuron)

    @classmethod
    def check_each_synapse_block_unique_and_defined(cls, neuron):
        """
        Checks if in the handed over neuron each block is defined at most once and mandatory blocks are defined.
        :param neuron: a single neuron instance
        :type neuron: ast_neuron
        """
        CoCoEachSynapseBlockUniqueAndDefined.check_co_co(neuron)

    @classmethod
    def check_function_declared_and_correctly_typed(cls, neuron: ASTNeuron):
        """
        Checks if in the handed over neuron all function calls use existing functions and the arguments are
        correctly typed.
        :param neuron: a single neuron instance
        """
        CoCoFunctionCallsConsistent.check_co_co(neuron)

    @classmethod
    def check_variables_unique_in_scope(cls, neuron: ASTNeuron):
        """
        Checks that all variables have been declared at most once per scope.
        :param neuron: a single neuron instance
        """
        CoCoVariableOncePerScope.check_co_co(neuron)

    @classmethod
    def check_state_variables_initialized(cls, neuron: ASTNeuron):
        """
        Checks if all the variables declared in state block are initialized with a value
        :param neuron: a single neuron instance
        """
        CoCoStateVariablesInitialized.check_co_co(neuron)

    @classmethod
    def check_variables_defined_before_usage(cls, neuron: ASTNeuron, after_ast_rewrite: bool) -> None:
        """
        Checks that all variables are defined before being used.
        :param neuron: a single neuron.
        """
        CoCoAllVariablesDefined.check_co_co(neuron, after_ast_rewrite)

    @classmethod
    def check_inline_expressions_have_rhs(cls, neuron: ASTNeuron):
        """
        Checks that all inline expressions have a right-hand side.
        :param neuron: a single neuron object
        """
        CoCoInlineExpressionsHaveRhs.check_co_co(neuron)

    @classmethod
    def check_inline_has_max_one_lhs(cls, neuron: ASTNeuron):
        """
        Checks that all inline expressions have exactly one left-hand side.
        :param neuron: a single neuron object.
        """
        CoCoInlineMaxOneLhs.check_co_co(neuron)

    @classmethod
    def check_input_ports_not_assigned_to(cls, neuron: ASTNeuron):
        """
        Checks that no values are assigned to input ports.
        :param neuron: a single neuron object.
        """
        CoCoInputPortNotAssignedTo.check_co_co(neuron)

    @classmethod
    def check_order_of_equations_correct(cls, neuron: ASTNeuron):
        """
        Checks that all equations specify the order of the variable.
        :param neuron: a single neuron object.
        """
        CoCoCorrectOrderInEquation.check_co_co(neuron)

    @classmethod
    def check_numerator_of_unit_is_one_if_numeric(cls, neuron: ASTNeuron):
        """
        Checks that all units which have a numeric numerator use 1.
        :param neuron: a single neuron object.
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
    def check_no_nest_namespace_collisions(cls, neuron: ASTNeuron):
        """
        Checks that all units which have a numeric numerator use 1.
        :param neuron: a single neuron object.
        """
        CoCoNoNestNameSpaceCollision.check_co_co(neuron)

    @classmethod
    def check_input_port_qualifier_unique(cls, neuron: ASTNeuron):
        """
        Checks that no spiking input ports are defined with redundant qualifiers.
        :param neuron: a single neuron object.
        """
        CoCoInputPortQualifierUnique.check_co_co(neuron)

    @classmethod
    def check_kernel_type(cls, neuron: ASTNeuron) -> None:
        """
        Checks that all defined kernels have type real.
        """
        CoCoKernelType.check_co_co(neuron)

    @classmethod
    def check_parameters_not_assigned_outside_parameters_block(cls, neuron: ASTNeuron):
        """
        Checks that parameters are not assigned outside the parameters block.
        :param neuron: a single neuron object.
        """
        CoCoParametersAssignedOnlyInParameterBlock.check_co_co(neuron)

    @classmethod
    def check_continuous_input_ports_not_qualified(cls, neuron: ASTNeuron):
        """
        Checks that continuous time input ports have not been specified with keywords, e.g., inhibitory.
        :param neuron: a single neuron object.
        """
        CoCoContinuousInputPortNotQualified.check_co_co(neuron)

    @classmethod
    def check_output_port_defined_if_emit_call(cls, neuron: ASTNeuron):
        """
        Checks that if emit_spike() function is called, an spiking output port is defined.
        :param neuron: a single neuron object.
        :type neuron: ASTNeuron
        """
        CoCoOutputPortDefinedIfEmitCall.check_co_co(neuron)

    @classmethod
    def check_odes_have_consistent_units(cls, neuron: ASTNeuron):
        """
        Checks that all ODE lhs and rhs have consistent units.
        :param neuron: a single neuron object.
        """
        CoCoOdesHaveConsistentUnits.check_co_co(neuron)

    @classmethod
    def check_ode_functions_have_consistent_units(cls, neuron: ASTNeuron):
        """
        Checks that all ODE function lhs and rhs have consistent units.
        :param neuron: a single neuron object.
        """
        CoCoOdeFunctionsHaveConsistentUnits.check_co_co(neuron)

    @classmethod
    def check_input_port_data_type(cls, neuron: ASTNeuron):
        """
        Checks that input ports have specified the data type if required and no data type if not allowed.
        :param neuron: a single neuron object.
        """
        CoCoInputPortDataType.check_co_co(neuron)

    @classmethod
    def check_integrate_odes_called_if_equations_defined(cls, neuron: ASTNeuron):
        """
        Ensures that integrate_odes() is called if one or more dynamical equations are defined.
        """
        CoCoIntegrateOdesCalledIfEquationsDefined.check_co_co(neuron)

    @classmethod
    def check_user_defined_function_correctly_built(cls, neuron: ASTNeuron):
        """
        Checks that all user defined functions are correctly constructed, i.e., have a return statement if declared
        and that the type corresponds to the declared one.
        :param neuron: a single neuron object.
        """
        CoCoUserDefinedFunctionCorrectlyDefined.check_co_co(neuron)

    @classmethod
    def check_initial_ode_initial_values(cls, neuron: ASTNeuron):
        """
        Checks if variables of odes are declared in the state block.
        :param neuron: a single neuron object.
        """
        CoCoEquationsOnlyForInitValues.check_co_co(neuron)

    @classmethod
    def check_convolve_cond_curr_is_correct(cls, neuron: ASTNeuron):
        """
        Checks if all convolve rhs are correctly provided with arguments.
        :param neuron: a single neuron object.
        """
        CoCoConvolveCondCorrectlyBuilt.check_co_co(neuron)

    @classmethod
    def check_correct_usage_of_kernels(cls, neuron: ASTNeuron):
        """
        Checks if all kernels are only used in convolve.
        :param neuron: a single neuron object.
        """
        CoCoNoKernelsExceptInConvolve.check_co_co(neuron)

    @classmethod
    def check_no_duplicate_compilation_unit_names(cls, compilation_units):
        """
        Checks if in a set of compilation units, two nodes have the same name.
        :param compilation_units: a list of compilation units
        :type compilation_units: list(ASTNestMLCompilationUnit)
        """
        CoCoNoDuplicateCompilationUnitNames.check_co_co(compilation_units)

    @classmethod
    def check_invariant_type_correct(cls, neuron: ASTNeuron):
        """
        Checks if all invariants are of type boolean.
        :param neuron: a single neuron object.
        """
        CoCoInvariantIsBoolean.check_co_co(neuron)

    @classmethod
    def check_vector_in_non_vector_declaration_detected(cls, neuron: ASTNeuron):
        """
        Checks if no declaration a vector value is added to a non vector one.
        :param neuron: a single neuron object.
        """
        CoCoVectorVariableInNonVectorDeclaration.check_co_co(neuron)

    @classmethod
    def check_sum_has_correct_parameter(cls, neuron: ASTNeuron):
        """
        Checks that all convolve function calls have variables as arguments.
        :param neuron: a single neuron object.
        """
        CoCoSumHasCorrectParameter.check_co_co(neuron)

    @classmethod
    def check_expression_correct(cls, neuron: ASTNeuron):
        """
        Checks that all rhs in the model are correctly constructed, e.g. type(lhs)==type(rhs).
        :param neuron: a single neuron
        """
        CoCoIllegalExpression.check_co_co(neuron)

    @classmethod
    def check_simple_delta_function(cls, neuron: ASTNeuron) -> None:
        CoCoSimpleDeltaFunction.check_co_co(neuron)

    @classmethod
    def check_function_argument_template_types_consistent(cls, neuron: ASTNeuron):
        """
        Checks if no declaration a vector value is added to a non vector one.
        :param neuron: a single neuron object.
        """
        CoCoFunctionArgumentTemplateTypesConsistent.check_co_co(neuron)

    @classmethod
    def check_co_co_priorities_correctly_specified(cls, neuron: ASTNeuron):
        """
        :param neuron: a single neuron object.
        """
        CoCoPrioritiesCorrectlySpecified.check_co_co(neuron)

    @classmethod
    def post_symbol_table_builder_checks(cls, neuron: ASTNeuron, after_ast_rewrite: bool = False):
        """
        Checks all context conditions.
        :param neuron: a single neuron object.
        """
        cls.check_function_defined(neuron)
        cls.check_function_declared_and_correctly_typed(neuron)
        cls.check_variables_unique_in_scope(neuron)
        cls.check_state_variables_initialized(neuron)
        cls.check_variables_defined_before_usage(neuron, after_ast_rewrite)
        cls.check_inline_expressions_have_rhs(neuron)
        cls.check_inline_has_max_one_lhs(neuron)
        cls.check_input_ports_not_assigned_to(neuron)
        cls.check_order_of_equations_correct(neuron)
        cls.check_numerator_of_unit_is_one_if_numeric(neuron)
        cls.check_no_nest_namespace_collisions(neuron)
        cls.check_input_port_qualifier_unique(neuron)
        cls.check_parameters_not_assigned_outside_parameters_block(neuron)
        cls.check_continuous_input_ports_not_qualified(neuron)
        cls.check_input_port_data_type(neuron)
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
            cls.check_integrate_odes_called_if_equations_defined(neuron)
        cls.check_invariant_type_correct(neuron)
        cls.check_vector_in_non_vector_declaration_detected(neuron)
        cls.check_sum_has_correct_parameter(neuron)
        cls.check_expression_correct(neuron)
        cls.check_simple_delta_function(neuron)
        cls.check_function_argument_template_types_consistent(neuron)
        cls.check_co_co_priorities_correctly_specified(neuron)

