/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.se_rwth.commons.SourcePosition;
import org.nest.ode._cocos.DerivativeOrderAtLeastOne;
import org.nest.ode._cocos.EquationsOnlyForStateVariables;
import org.nest.ode._cocos.SumHasCorrectParameter;
import org.nest.units._cocos.UnitDeclarationOnlyOnesAllowed;
import org.nest.utils.AstUtils;

/**
 * Factory for CoCo error strings. The dispatch is done by the static type of the context condition object.
 *
 * @author plotnikov, traeder
 */
public class NestmlErrorStrings {
  private static final NestmlErrorStrings instance = new NestmlErrorStrings();
  private static final String SEPARATOR = " : ";

  private NestmlErrorStrings() {
  }

  public static NestmlErrorStrings getInstance() {
    return instance;
  }

  static String message(final AliasHasOneVar coco) {
    final String ERROR_MSG_FORMAT = "'function' declarations must only declare exactly one variable.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings("unused") // parameter is used for dispatch
  static String code(final AliasHasOneVar coco) {
    return "NESTML_ALIAS_HAS_ONE_VAR";
  }

  static String message(final VectorVariableInNonVectorDeclaration coco, final String usedAlias) {
    final String ERROR_MSG_FORMAT = "A vector '" + usedAlias + "' cannot be used as part of an initial expression of " +
                                    "non-vector variable declaration.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings("unused") // parameter is used for dispatch
  static String code(final VectorVariableInNonVectorDeclaration coco) {
    return "NESTML_ALIAS_IN_NON_ALIAS_DECL";
  }

  static String message(final FunctionParameterHasTypeName coco, final String variable) {
    final String ERROR_MSG_FORMAT = "The function parameter '" + variable +"' has name of an existing NESTML type.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  public static String code(final FunctionParameterHasTypeName coco) {
    return "NESTML_FUNCTION_PARAMETER_HAS_TYPE_NAME";
  }

  public String getErrorMsg(final UnitDeclarationOnlyOnesAllowed coco){
    final String ERROR_MSG_FORMAT = "Literals in Unit types may only be '1' (one)";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }
  @SuppressWarnings({"unused"}) // used for the routing
  public String code(final UnitDeclarationOnlyOnesAllowed coco) {
    return "NESTML_UNIT_DECLARATION_ONLY_ONES_ALLOWED";
  }

  static String getErrorMsg(final AliasHasDefiningExpression coco) {
    final String ERROR_MSG_FORMAT = "'function' must be always defined through an expression.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final AliasHasDefiningExpression coco) {
    return "NESTML_ALIAS_HAS_DEFINING_EXPRESSION";
  }

  static String getErrorMsgInvariantMustBeBoolean(final InvalidTypeOfInvariant coco, final String expressionType) {
    final String ERROR_MSG_FORMAT = "The type of the invariant expression must be boolean and not: " + expressionType;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }


  static String getErrorMsgCannotComputeType(final InvalidTypeOfInvariant coco, final String invariantType) {
    final String ERROR_MSG_FORMAT = "Cannot compute the type: " + invariantType;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(InvalidTypeOfInvariant coco) {
    return "NESTML_INVALID_TYPE_OF_INVARIANT";
  }

  static String getErrorMsg(final BufferNotAssignable coco, final String bufferName) {
    final String ERROR_MSG_FORMAT = "Buffer '" + bufferName + "' cannot be reassigned.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(BufferNotAssignable coco) {
    return  "NESTML_BUFFER_NOT_ASSIGNABLE";
  }

  static String getErrorMsgWrongReturnType(
      final FunctionReturnsIncorrectValue coco,
      final String functionName,
      final String functionReturnTypeName) {
    final String ERROR_MSG_FORMAT = "Function '" + functionName + "' must return a result of type "
                                    + functionReturnTypeName + ".";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static String getErrorMsgCannotConvertReturnValue(FunctionReturnsIncorrectValue coco,
                                                    String expressionTypeName, String functionReturnTypeName) {
    final String ERROR_MSG_FORMAT = "Cannot convert from " + expressionTypeName
                                    + " (type of return expression) to " + functionReturnTypeName
                                    + " (return type).";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static String getErrorMsgCannotDetermineExpressionType(final FunctionReturnsIncorrectValue coco) {
    final String ERROR_MSG_FORMAT = "Cannot determine the type of the expression";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final FunctionReturnsIncorrectValue coco) {
    return "NESTML_FUNCTION_RETURNS_INCORRECT_VALUE";
  }

  String getErrorMsg(final CurrentPortIsInhOrExc coco) {
    final String ERROR_MSG_FORMAT = "Current input can neither be inhibitory nor excitatory.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final CurrentPortIsInhOrExc coco) {
    return "NESTML_CURRENT_PORT_IS_INH_OR_EXC";
  }

  static public String getErrorMsgAssignToNonState(
      final EquationsOnlyForStateVariables coco,
      final String variableName) {
    final String ERROR_MSG_FORMAT = "The variable '" + variableName + "' is not a state"
                                    + " variable and, therefore, cannot be used on the left side of an equation.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static public String getErrorMsgVariableNotDefined(EquationsOnlyForStateVariables coco, final String variableName) {
    final String ERROR_MSG_FORMAT = "The variable " + variableName + " used as left-hand side " +
                                    "of the ode is not defined.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final EquationsOnlyForStateVariables coco) {
    return "NESTML_EQUATIONS_ONLY_FOR_STATE_VARIABLES";
  }

  static String getErrorMsg(final MissingReturnStatementInFunction coco,
                     final String functionName,
                     final String returnType) {
    final String ERROR_MSG_FORMAT = "Function '" + functionName + "' must return a result of type '"
                                             + returnType + "'";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final MissingReturnStatementInFunction coco) {
    return "NESTML_EQUATIONS_ONLY_FOR_STATE_VARIABLES";
  }

  static String getErrorMsgGet_InstanceDefined(GetterSetterFunctionNames coco) {
    final String ERROR_MSG_FORMAT = "The function 'get_instance' is going to be generated. Please use another name.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static String getErrorMsgGeneratedFunctionDefined(GetterSetterFunctionNames coco,
                                                    String functionName, String variableName) {
    final String ERROR_MSG_FORMAT = "The function '" + functionName + "' is going to be generated, since"
                                    + " there is a variable called '" + variableName + "'.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final GetterSetterFunctionNames coco) {
    return "NESTML_GETTER_SETTER_FUNCTION_NAMES";
  }

  public static String getErrorMsg(final SumHasCorrectParameter coco, final String expression) {
    final String ERROR_MSG_FORMAT = "The arguments of the I_sum must be atomic expressions: "
                                    + "e.g. V_m and not : " + expression;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final SumHasCorrectParameter coco) {
    return "NESTML_SUM_HAS_INCORRECT_PARAMETER";
  }

  static String getErrorMsg(final InvalidTypesInDeclaration coco, String typeName) {
    final String ERROR_MSG_FORMAT = "The type " + typeName + " is a neuron/component. No neurons/components allowed " +
                                    "in this place. Use the use-statement.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final InvalidTypesInDeclaration coco) {
    return "NESTML_INVALID_TYPES_DECLARATION";
  }

  static String getErrorMsg(final MemberVariableDefinedMultipleTimes coco,
                     final String varName,
                     int line,
                     int column) {
    final String ERROR_MSG_FORMAT =  "Variable '" + varName + "' is previously defined in line: "
                                     + line + ":" + column;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final MemberVariableDefinedMultipleTimes coco) {
    return "NESTML_MEMBER_VARIABLE_DEFINED_MULTIPLE_TIMES";
  }

  static String getErrorMsgDeclaredInIncorrectOrder(MemberVariablesInitialisedInCorrectOrder coco,
                                                    String varName, String declaredName) {
    final String ERROR_MSG_FORMAT =  "Variable '"
                                     + varName
                                     + "' must be declared before it can be used in declaration of '"
                                     + declaredName + "'.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static String getErrorMsgVariableNotDefined(MemberVariablesInitialisedInCorrectOrder coco, String varName) {
    final String ERROR_MSG_FORMAT =  "Variable '" + varName + "' is undefined.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final MemberVariablesInitialisedInCorrectOrder coco) {
    return "NESTML_MEMBER_VARIABLES_INITIALISED_IN_CORRECT_ORDER";
  }

  static String getErrorMsgNeuronHasNoSymbol(final FunctionDefinedMultipleTimes coco, final String neuronName) {
    final String ERROR_MSG_FORMAT =  "The neuron symbol: " + neuronName + " has no symbol.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static String getErrorMsgParameterDefinedMultipleTimes(final FunctionDefinedMultipleTimes coco, final String funname) {
    final String ERROR_MSG_FORMAT =  "The function '" + funname + " parameter(s) is defined multiple times.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static String getErrorMsgNoScopePresent(final FunctionDefinedMultipleTimes coco) {
    final String ERROR_MSG_FORMAT =  "Run symbol table creator.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final FunctionDefinedMultipleTimes coco) {
    return "NESTML_MULTIPLE_FUNCTIONS_DECLARATIONS";
  }

  static String getErrorMsgMultipleInhibitory(final MultipleInhExcModifiers coco) {
    final String ERROR_MSG_FORMAT = "Multiple occurrences of the keyword 'excitatory' are not allowed.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static String getErrorMsgMultipleExcitatory(MultipleInhExcModifiers coco) {
    final String ERROR_MSG_FORMAT = "Multiple occurrences of the keyword 'excitatory' are not allowed.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final MultipleInhExcModifiers coco) {
    return "NESTML_MULTIPLE_INH_EXC_MODIFIERS";
  }

  static String getErrorMsg(NestFunctionCollision coco, String funName) {
    final String ERROR_MSG_FORMAT = "The function-name '" + funName
                                    + "' is already used by NEST. Please use another name.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final NestFunctionCollision coco) {
    return "NESTML_NEST_FUNCTION_COLLISION";
  }

  static String getErrorMsgDynamicsNotPresent(NeuronWithMultipleOrNoUpdate coco) {
    return code(coco) + SEPARATOR + "Neurons need at least one update block.";
  }

  static String getErrorMsgMultipleDynamics(NeuronWithMultipleOrNoUpdate coco) {
    return code(coco) + SEPARATOR + "Neurons need at most one update.";
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final NeuronWithMultipleOrNoUpdate coco) {
    return "NESTML_NEURON_WITH_MULTIPLE_OR_NO_UPDATE";
  }

  static String errorNoInput(NeuronWithMultipleOrNoInput coco) {
    return code(coco) + SEPARATOR + "There is no input block in the neuron.";
  }

  static String errorMultipleInputs(NeuronWithMultipleOrNoInput coco) {
    return code(coco) + SEPARATOR + "There are more than one input block in the neuron";
  }

  @SuppressWarnings("unused") // parameter is used for dispatch
  static String code(final NeuronWithMultipleOrNoInput coco) {
    return "NESTML_NEURON_WITH_MULTIPLE_OR_NO_INPUT";
  }

  static String errorNoOutput(NeuronWithMultipleOrNoOutput coco) {
    return code(coco) + SEPARATOR + "Neurons need at least one output.";
  }

  static String errorMultipleOutputs(NeuronWithMultipleOrNoOutput coco) {
    return code(coco) + SEPARATOR + "Neurons need at most one output.";
  }

  @SuppressWarnings("unused") // parameter is used for dispatch
  static String code(final NeuronWithMultipleOrNoOutput coco) {
    return "NESTML_NEURON_WITH_MULTIPLE_OR_NO_OUTPUT";
  }

  String getErrorMsg(TypeIsDeclaredMultipleTimes coco, String typeName) {
    return TypeIsDeclaredMultipleTimes.ERROR_CODE + SEPARATOR + "The type '" + typeName + "' is defined multiple times.";
  }

  public String getErrorMsg(final DerivativeOrderAtLeastOne coco, final String variableName) {

    return DerivativeOrderAtLeastOne.ERROR_CODE + SEPARATOR + "The variable on the righthandside of an equation must be derivative variable, e.g. " + variableName + "'";
  }

  public String getErrorMsg(AssignmentToAlias assignmentToAlias, final String variableName) {
    return AssignmentToAlias.ERROR_CODE + SEPARATOR + "You cannot assign a value to an function: " + variableName;
  }

  static String error(final VariableBlockDefinedMultipleTimes coco,
                      final SourcePosition sourcePosition,
                      final String block) {
    return code(coco) + " " + AstUtils.print(sourcePosition) + ": "  + block + "-block defined multiple times. " +
           "It should be defined at most once in the model.";
  }

  static String code(final VariableBlockDefinedMultipleTimes coco) {
    return "NESTML_VARIABLE_BLOCK_DEFINED_MULTIPLE_TIMES";
  }

}
