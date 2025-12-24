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

from typing import Union

from pynestml.cocos.co_co_all_variables_defined import CoCoAllVariablesDefined
from pynestml.cocos.co_co_cm_channel_model import CoCoCmChannelModel
from pynestml.cocos.co_co_cm_concentration_model import CoCoCmConcentrationModel
from pynestml.cocos.co_co_cm_continuous_input_model import CoCoCmContinuousInputModel
from pynestml.cocos.co_co_cm_synapse_model import CoCoCmSynapseModel
from pynestml.cocos.co_co_convolve_has_correct_parameter import CoCoConvolveHasCorrectParameter
from pynestml.cocos.co_co_convolve_cond_correctly_built import CoCoConvolveCondCorrectlyBuilt
from pynestml.cocos.co_co_correct_numerator_of_unit import CoCoCorrectNumeratorOfUnit
from pynestml.cocos.co_co_correct_order_in_equation import CoCoCorrectOrderInEquation
from pynestml.cocos.co_co_each_block_defined_at_most_once import CoCoEachBlockDefinedAtMostOnce
from pynestml.cocos.co_co_equations_only_for_init_values import CoCoEquationsOnlyForInitValues
from pynestml.cocos.co_co_function_argument_template_types_consistent import CoCoFunctionArgumentTemplateTypesConsistent
from pynestml.cocos.co_co_function_calls_consistent import CoCoFunctionCallsConsistent
from pynestml.cocos.co_co_function_unique import CoCoFunctionUnique
from pynestml.cocos.co_co_illegal_expression import CoCoIllegalExpression
from pynestml.cocos.co_co_input_port_not_assigned_to import CoCoInputPortNotAssignedTo
from pynestml.cocos.co_co_integrate_odes_params_correct import CoCoIntegrateODEsParamsCorrect
from pynestml.cocos.co_co_inline_expressions_have_rhs import CoCoInlineExpressionsHaveRhs
from pynestml.cocos.co_co_inline_expression_not_assigned_to import CoCoInlineExpressionNotAssignedTo
from pynestml.cocos.co_co_inline_max_one_lhs import CoCoInlineMaxOneLhs
from pynestml.cocos.co_co_input_port_not_assigned_to import CoCoInputPortNotAssignedTo
from pynestml.cocos.co_co_input_port_qualifier_unique import CoCoInputPortQualifierUnique
from pynestml.cocos.co_co_internals_assigned_only_in_internals_block import CoCoInternalsAssignedOnlyInInternalsBlock
from pynestml.cocos.co_co_integrate_odes_called_if_equations_defined import CoCoIntegrateOdesCalledIfEquationsDefined
from pynestml.cocos.co_co_invariant_is_boolean import CoCoInvariantIsBoolean
from pynestml.cocos.co_co_kernel_type import CoCoKernelType
from pynestml.cocos.co_co_model_name_unique import CoCoModelNameUnique
from pynestml.cocos.co_co_nest_random_functions_legally_used import CoCoNestRandomFunctionsLegallyUsed
from pynestml.cocos.co_co_no_kernels_except_in_convolve import CoCoNoKernelsExceptInConvolve
from pynestml.cocos.co_co_no_nest_name_space_collision import CoCoNoNestNameSpaceCollision
from pynestml.cocos.co_co_no_duplicate_compilation_unit_names import CoCoNoDuplicateCompilationUnitNames
from pynestml.cocos.co_co_odes_have_consistent_units import CoCoOdesHaveConsistentUnits
from pynestml.cocos.co_co_ode_functions_have_consistent_units import CoCoOdeFunctionsHaveConsistentUnits
from pynestml.cocos.co_co_output_port_defined_if_emit_call import CoCoOutputPortDefinedIfEmitCall
from pynestml.cocos.co_co_parameters_assigned_only_in_parameter_block import CoCoParametersAssignedOnlyInParameterBlock
from pynestml.cocos.co_co_priorities_correctly_specified import CoCoPrioritiesCorrectlySpecified
from pynestml.cocos.co_co_resolution_func_legally_used import CoCoResolutionFuncLegallyUsed
from pynestml.cocos.co_co_resolution_func_used import CoCoResolutionOrStepsFuncUsed
from pynestml.cocos.co_co_simple_delta_function import CoCoSimpleDeltaFunction
from pynestml.cocos.co_co_state_variables_initialized import CoCoStateVariablesInitialized
from pynestml.cocos.co_co_timestep_function_legally_used import CoCoTimestepFuncLegallyUsed
from pynestml.cocos.co_co_user_defined_function_correctly_defined import CoCoUserDefinedFunctionCorrectlyDefined
from pynestml.cocos.co_co_v_comp_exists import CoCoVCompDefined
from pynestml.cocos.co_co_variable_once_per_scope import CoCoVariableOncePerScope
from pynestml.cocos.co_co_vector_declaration_right_size import CoCoVectorDeclarationRightSize
from pynestml.cocos.co_co_vector_input_port_correct_size_type import CoCoVectorInputPortsCorrectSizeType
from pynestml.cocos.co_co_vector_parameter_declared_in_right_block import CoCoVectorParameterDeclaredInRightBlock
from pynestml.cocos.co_co_vector_variable_in_non_vector_declaration import CoCoVectorVariableInNonVectorDeclaration
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_model import ASTModel
from pynestml.utils.logger import Logger


class CoCosManager:
    """
    This class provides a set of context conditions which have to hold for each model instance.
    """
    @classmethod
    def check_function_defined(cls, model: ASTModel):
        """
        Checks for the handed over model that each used function it is defined.
        """
        CoCoFunctionUnique.check_co_co(model)

    @classmethod
    def check_inline_expression_not_assigned_to(cls, model: ASTModel):
        """
        Checks for the handed over model that inline expressions are not assigned to.
        """
        CoCoInlineExpressionNotAssignedTo.check_co_co(model)

    @classmethod
    def check_each_block_defined_at_most_once(cls, node: ASTModel):
        """
        Checks if in the handed over model, each block is defined at most once and mandatory blocks are defined.
        :param node: a single model instance
        """
        CoCoEachBlockDefinedAtMostOnce.check_co_co(node)

    @classmethod
    def check_function_declared_and_correctly_typed(cls, model: ASTModel):
        """
        Checks if in the handed over model all function calls use existing functions and the arguments are
        correctly typed.
        :param model: a single model instance
        """
        CoCoFunctionCallsConsistent.check_co_co(model)

    @classmethod
    def check_variables_unique_in_scope(cls, model: ASTModel):
        """
        Checks that all variables have been declared at most once per scope.
        :param model: a single model instance
        """
        CoCoVariableOncePerScope.check_co_co(model)

    @classmethod
    def check_state_variables_initialized(cls, model: ASTModel):
        """
        Checks if all the variables declared in state block are initialized with a value
        :param model: a single model instance
        """
        CoCoStateVariablesInitialized.check_co_co(model)

    @classmethod
    def check_variables_defined_before_usage(cls, model: ASTModel) -> None:
        """
        Checks that all variables are defined before being used.
        :param model: a single model.
        """
        CoCoAllVariablesDefined.check_co_co(model)

    @classmethod
    def check_v_comp_requirement(cls, neuron: ASTModel):
        """
        In compartmental case, checks if v_comp variable was defined
        :param neuron: a single neuron object
        """
        CoCoVCompDefined.check_co_co(neuron)

    @classmethod
    def check_compartmental_model(cls, neuron: ASTModel) -> None:
        """
        collects all relevant information for the different compartmental mechanism classes for later code-generation

        searches for inlines or odes with decorator @mechanism::<type> and performs a base and, depending on type,
        specific information collection process. See nestml documentation on compartmental code generation.
        """
        CoCoCmChannelModel.check_co_co(neuron)
        CoCoCmConcentrationModel.check_co_co(neuron)
        CoCoCmSynapseModel.check_co_co(neuron)
        CoCoCmContinuousInputModel.check_co_co(neuron)

    @classmethod
    def check_inline_expressions_have_rhs(cls, model: ASTModel):
        """
        Checks that all inline expressions have a right-hand side.
        :param model: a single model object
        """
        CoCoInlineExpressionsHaveRhs.check_co_co(model)

    @classmethod
    def check_inline_has_max_one_lhs(cls, model: ASTModel):
        """
        Checks that all inline expressions have exactly one left-hand side.
        :param model: a single model object.
        """
        CoCoInlineMaxOneLhs.check_co_co(model)

    @classmethod
    def check_input_ports_not_assigned_to(cls, model: ASTModel):
        """
        Checks that no values are assigned to input ports.
        :param model: a single model object.
        """
        CoCoInputPortNotAssignedTo.check_co_co(model)

    @classmethod
    def check_order_of_equations_correct(cls, model: ASTModel):
        """
        Checks that all equations specify the order of the variable.
        :param model: a single model object.
        """
        CoCoCorrectOrderInEquation.check_co_co(model)

    @classmethod
    def check_numerator_of_unit_is_one_if_numeric(cls, model: ASTModel):
        """
        Checks that all units which have a numeric numerator use 1.
        :param model: a single model object.
        """
        CoCoCorrectNumeratorOfUnit.check_co_co(model)

    @classmethod
    def check_model_names_unique(cls, compilation_unit):
        """
        Checks that all declared models in a compilation unit have a unique name.
        :param compilation_unit: a single compilation unit.
        :type compilation_unit: ASTCompilationUnit
        """
        CoCoModelNameUnique.check_co_co(compilation_unit)

    @classmethod
    def check_no_nest_namespace_collisions(cls, model: ASTModel):
        """
        Checks that all units which have a numeric numerator use 1.
        :param model: a single model object.
        """
        CoCoNoNestNameSpaceCollision.check_co_co(model)

    @classmethod
    def check_input_port_qualifier_unique(cls, model: ASTModel):
        """
        Checks that no spiking input ports are defined with redundant qualifiers.
        :param model: a single model object.
        """
        CoCoInputPortQualifierUnique.check_co_co(model)

    @classmethod
    def check_kernel_type(cls, model: ASTModel) -> None:
        """
        Checks that all defined kernels have type real.
        """
        CoCoKernelType.check_co_co(model)

    @classmethod
    def check_parameters_not_assigned_outside_parameters_block(cls, model: ASTModel):
        """
        Checks that parameters are not assigned outside the parameters block.
        :param model: a single model object.
        """
        CoCoParametersAssignedOnlyInParameterBlock.check_co_co(model)

    @classmethod
    def check_internals_not_assigned_outside_internals_block(cls, model: ASTModel):
        """
        Checks that internals are not assigned outside the internals block.
        :param model: a single model object.
        """
        CoCoInternalsAssignedOnlyInInternalsBlock.check_co_co(model)

    @classmethod
    def check_output_port_defined_if_emit_call(cls, model: ASTModel):
        """
        Checks that if emit_spike() function is called, an spiking output port is defined.
        :param model: a single model object.
        """
        CoCoOutputPortDefinedIfEmitCall.check_co_co(model)

    @classmethod
    def check_odes_have_consistent_units(cls, model: ASTModel):
        """
        Checks that all ODE lhs and rhs have consistent units.
        :param model: a single model object.
        """
        CoCoOdesHaveConsistentUnits.check_co_co(model)

    @classmethod
    def check_ode_functions_have_consistent_units(cls, model: ASTModel):
        """
        Checks that all ODE function lhs and rhs have consistent units.
        :param model: a single model object.
        """
        CoCoOdeFunctionsHaveConsistentUnits.check_co_co(model)

    @classmethod
    def check_integrate_odes_called_if_equations_defined(cls, model: ASTModel):
        """
        Ensures that integrate_odes() is called if one or more dynamical equations are defined.
        """
        CoCoIntegrateOdesCalledIfEquationsDefined.check_co_co(model)

    @classmethod
    def check_user_defined_function_correctly_built(cls, model: ASTModel):
        """
        Checks that all user defined functions are correctly constructed, i.e., have a return statement if declared
        and that the type corresponds to the declared one.
        :param model: a single model object.
        """
        CoCoUserDefinedFunctionCorrectlyDefined.check_co_co(model)

    @classmethod
    def check_initial_ode_initial_values(cls, model: ASTModel):
        """
        Checks if variables of odes are declared in the state block.
        :param model: a single model object.
        """
        CoCoEquationsOnlyForInitValues.check_co_co(model)

    @classmethod
    def check_convolve_cond_curr_is_correct(cls, model: ASTModel):
        """
        Checks if all convolve rhs are correctly provided with arguments.
        :param model: a single model object.
        """
        CoCoConvolveCondCorrectlyBuilt.check_co_co(model)

    @classmethod
    def check_integrate_odes_params_correct(cls, model: ASTModel):
        """
        Checks if all integrate_odes() calls have correct parameters.
        :param model: a single model object.
        """
        CoCoIntegrateODEsParamsCorrect.check_co_co(model)

    @classmethod
    def check_correct_usage_of_kernels(cls, model: ASTModel):
        """
        Checks if all kernels are only used in convolve.
        :param model: a single model object.
        """
        CoCoNoKernelsExceptInConvolve.check_co_co(model)

    @classmethod
    def check_no_duplicate_compilation_unit_names(cls, compilation_units):
        """
        Checks if in a set of compilation units, two nodes have the same name.
        :param compilation_units: a list of compilation units
        :type compilation_units: list(ASTNestMLCompilationUnit)
        """
        CoCoNoDuplicateCompilationUnitNames.check_co_co(compilation_units)

    @classmethod
    def check_invariant_type_correct(cls, model: ASTModel):
        """
        Checks if all invariants are of type boolean.
        :param model: a single model object.
        """
        CoCoInvariantIsBoolean.check_co_co(model)

    @classmethod
    def check_resolution_func_used(cls, model: ASTModel):
        """
        Checks if all invariants are of type boolean.
        :param model: a single model object.
        """
        CoCoResolutionOrStepsFuncUsed.check_co_co(model)

    @classmethod
    def check_vector_in_non_vector_declaration_detected(cls, model: ASTModel):
        """
        Checks if no declaration a vector value is added to a non vector one.
        :param model: a single model object.
        """
        CoCoVectorVariableInNonVectorDeclaration.check_co_co(model)

    @classmethod
    def check_convolve_has_correct_parameter(cls, model: ASTModel):
        """
        Checks that all convolve function calls have variables as arguments.
        :param model: a single model object.
        """
        CoCoConvolveHasCorrectParameter.check_co_co(model)

    @classmethod
    def check_expression_correct(cls, model: ASTModel):
        """
        Checks that all rhs in the model are correctly constructed, e.g. type(lhs)==type(rhs).
        :param model: a single model
        """
        CoCoIllegalExpression.check_co_co(model)

    @classmethod
    def check_simple_delta_function(cls, model: ASTModel) -> None:
        CoCoSimpleDeltaFunction.check_co_co(model)

    @classmethod
    def check_function_argument_template_types_consistent(cls, model: ASTModel):
        """
        Checks if no declaration a vector value is added to a non vector one.
        :param model: a single model object.
        """
        CoCoFunctionArgumentTemplateTypesConsistent.check_co_co(model)

    @classmethod
    def check_vector_parameter_declaration(cls, model: ASTModel):
        """
        Checks if the vector parameter is declared in the right block
        :param model: a single model object
        """
        CoCoVectorParameterDeclaredInRightBlock.check_co_co(model)

    @classmethod
    def check_vector_declaration_size(cls, model: ASTModel):
        """
        Checks if the vector is declared with a size greater than 0
        :param model: a single model object
        """
        CoCoVectorDeclarationRightSize.check_co_co(model)

    @classmethod
    def check_co_co_priorities_correctly_specified(cls, model: ASTModel):
        """
        :param model: a single model object.
        """
        CoCoPrioritiesCorrectlySpecified.check_co_co(model)

    @classmethod
    def check_resolution_func_legally_used(cls, model: ASTModel):
        """
        :param model: a single model object.
        """
        CoCoResolutionFuncLegallyUsed.check_co_co(model)

    @classmethod
    def check_timestep_func_legally_used(cls, model: ASTModel):
        """
        :param model: a single model object.
        """
        CoCoTimestepFuncLegallyUsed.check_co_co(model)

    @classmethod
    def check_input_port_size_type(cls, model: ASTModel):
        """
        :param model: a single model object
        """
        CoCoVectorInputPortsCorrectSizeType.check_co_co(model)

    @classmethod
    def check_co_co_nest_random_functions_legally_used(cls, model: ASTModel):
        """
        Checks if the random number functions are used only in the update block.
        :param model: a single model object.
        """
        CoCoNestRandomFunctionsLegallyUsed.check_co_co(model)

    @classmethod
    def check_cocos(cls, model: ASTModel, after_ast_rewrite: bool = False):
        """
        Checks all context conditions.
        :param model: a single model object.
        """
        Logger.set_current_node(model)

        cls.check_each_block_defined_at_most_once(model)
        cls.check_function_defined(model)
        cls.check_variables_unique_in_scope(model)
        cls.check_inline_expression_not_assigned_to(model)
        cls.check_state_variables_initialized(model)
        cls.check_variables_defined_before_usage(model)
        if FrontendConfiguration.get_target_platform().upper() == 'NEST_COMPARTMENTAL':
            # XXX: TODO: refactor this out; define a ``cocos_from_target_name()`` in the frontend instead.
            cls.check_v_comp_requirement(model)
            cls.check_compartmental_model(model)
        cls.check_inline_expressions_have_rhs(model)
        cls.check_inline_has_max_one_lhs(model)
        cls.check_input_ports_not_assigned_to(model)
        cls.check_order_of_equations_correct(model)
        cls.check_numerator_of_unit_is_one_if_numeric(model)
        cls.check_no_nest_namespace_collisions(model)
        cls.check_input_port_qualifier_unique(model)
        cls.check_parameters_not_assigned_outside_parameters_block(model)
        cls.check_internals_not_assigned_outside_internals_block(model)
        cls.check_user_defined_function_correctly_built(model)
        cls.check_initial_ode_initial_values(model)
        cls.check_kernel_type(model)
        cls.check_convolve_cond_curr_is_correct(model)
        cls.check_integrate_odes_params_correct(model)
        cls.check_output_port_defined_if_emit_call(model)
        if not after_ast_rewrite:
            # units might be incorrect due to e.g. refactoring convolve call (Real type assigned)
            cls.check_odes_have_consistent_units(model)
            # ODE functions have been removed at this point
            cls.check_function_declared_and_correctly_typed(model)
            cls.check_ode_functions_have_consistent_units(model)
            cls.check_correct_usage_of_kernels(model)
            cls.check_resolution_func_used(model)    # ``__h = resolution()`` is added after transformations; put this check inside the ``if`` to make sure it's not always triggered
            if FrontendConfiguration.get_target_platform().upper() != 'NEST_COMPARTMENTAL':
                cls.check_integrate_odes_called_if_equations_defined(model)
        cls.check_invariant_type_correct(model)
        cls.check_vector_in_non_vector_declaration_detected(model)
        cls.check_convolve_has_correct_parameter(model)
        cls.check_expression_correct(model)
        cls.check_simple_delta_function(model)
        cls.check_function_argument_template_types_consistent(model)
        cls.check_vector_parameter_declaration(model)
        cls.check_vector_declaration_size(model)
        cls.check_co_co_priorities_correctly_specified(model)
        cls.check_resolution_func_legally_used(model)
        cls.check_input_port_size_type(model)
        cls.check_timestep_func_legally_used(model)

        Logger.set_current_node(None)
