/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.se_rwth.commons.SourcePosition;
import org.nest.nestml._symboltable.unitrepresentation.UnitRepresentation;
import org.nest.nestml._visitor.DotOperatorVisitor;
import org.nest.nestml._visitor.FunctionCallVisitor;
import org.nest.nestml._visitor.ODEPostProcessingVisitor;
import org.nest.nestml._visitor.UnitsSIVisitor;
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

  public String message(final UnitDeclarationOnlyOnesAllowed coco){
    final String ERROR_MSG_FORMAT = "Literals in Unit types may only be '1' (one)";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }
  @SuppressWarnings({"unused"}) // used for the routing
  public String code(final UnitDeclarationOnlyOnesAllowed coco) {
    return "NESTML_UNIT_DECLARATION_ONLY_ONES_ALLOWED";
  }

  static String message(final AliasHasDefiningExpression coco) {
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

  static String message(final BufferNotAssignable coco, final String bufferName) {
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

  String message(final CurrentPortIsInhOrExc coco) {
    final String ERROR_MSG_FORMAT = "Current input can neither be inhibitory nor excitatory.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final CurrentPortIsInhOrExc coco) {
    return "NESTML_CURRENT_PORT_IS_INH_OR_EXC";
  }

  static public String message(
      final EquationsOnlyForInitialValues coco,
      final String variableName) {
    final String ERROR_MSG_FORMAT = "The variable " + variableName + " must defined in the 'initial_values' block"
                                    + " for being used on the left side of an ODE.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static public String getErrorMsgVariableNotDefined(EquationsOnlyForInitialValues coco, final String variableName) {
    final String ERROR_MSG_FORMAT = "The variable " + variableName + " used as left-hand side " +
                                    "of the ode is not defined.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final EquationsOnlyForInitialValues coco) {
    return "NESTML_EQUATIONS_ONLY_FOR_STATE_VARIABLES";
  }

  static String message(final MissingReturnStatementInFunction coco,
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

  public static String message(final ConvolveHasCorrectParameter coco, final String expression) {
    final String ERROR_MSG_FORMAT = "The arguments of the I_sum must be atomic expressions: "
                                    + "e.g. V_m and not : " + expression;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final ConvolveHasCorrectParameter coco) {
    return "NESTML_CONVOLVE_HAS_INCORRECT_PARAMETER";
  }

  static String message(final InvalidTypesInDeclaration coco, String typeName) {
    final String ERROR_MSG_FORMAT = "The type " + typeName + " is a neuron/component. No neurons/components allowed " +
                                    "in this place. Use the use-statement.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final InvalidTypesInDeclaration coco) {
    return "NESTML_INVALID_TYPES_DECLARATION";
  }

  static String message(final MemberVariableDefinedMultipleTimes coco,
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

  static String message(NestFunctionCollision coco, String funName) {
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

  static String message(TypeIsDeclaredMultipleTimes coco, String typeName) {
    return code(coco) + SEPARATOR + "The type '" + typeName + "' is defined multiple times.";
  }

  @SuppressWarnings("unused") // parameter is used for dispatch
  static String code(final TypeIsDeclaredMultipleTimes coco) {
    return "NESTML_TYPES_DECLARED_MULTIPLE_TIMES";
  }

  static public String message(final DerivativeOrderAtLeastOne coco, final String variableName) {

    return code(coco) + SEPARATOR + "The variable on the righthandside of an equation must be derivative variable, e.g. "
           + variableName + "'";
  }

  @SuppressWarnings("unused") // parameter is used for dispatch
  static String code(final DerivativeOrderAtLeastOne coco) {
    return "NESTML_DERIVATIVE_ORDER_AT_LEAST_ONE";
  }

  static String error(final VariableBlockDefinedMultipleTimes coco,
                      final SourcePosition sourcePosition,
                      final String block) {
    return code(coco) + " " + AstUtils.print(sourcePosition) + ": "  + block + "-block defined multiple times. " +
           "It should be defined at most once in the model.";
  }

  @SuppressWarnings("unused") // parameter is used for dispatch
  static String code(final VariableBlockDefinedMultipleTimes coco) {
    return "NESTML_VARIABLE_BLOCK_DEFINED_MULTIPLE_TIMES";
  }

  static public String messageVariableNotDefined(final UsageOfAmbiguousName coco, final String variableName) {
    final String ERROR_MSG_FORMAT = "The variable " + variableName + " is not defined";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static public String messageVariableDefinedMultipleTimes(final UsageOfAmbiguousName coco, final String variableName) {
    final String ERROR_MSG_FORMAT = "The variable " + variableName + " is defined multiple times";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static public String messageFunctionDefinedMultipleTimes(final UsageOfAmbiguousName coco, final String variableName) {
    final String ERROR_MSG_FORMAT = "The function " + variableName + " is defined multiple times";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings("unused") // parameter is used for dispatch
  static String code(final UsageOfAmbiguousName coco) {
    return "NESTML_NAME_IS_NOT_UNIQUE";
  }

  static public String message(final RestrictUseOfShapes coco) {
    //TODO: adapt for removal of curr_sum and cond_sum
    final String ERROR_MSG_FORMAT = "Shapes may not be used in this fashion";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings("unused") // parameter is used for dispatch
  static String code(final RestrictUseOfShapes coco) {
    return "NESTML_RESTRICT_USE_OF_SHAPES";
  }

  public static String expressionCalculation(final ODEPostProcessingVisitor coco, final String description) {
    final String ERROR_MSG_FORMAT = "Error in expression type calculation: " + description;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String expressionNonNumeric(final ODEPostProcessingVisitor coco) {
    final String ERROR_MSG_FORMAT = "Type of LHS Variable in ODE is neither a Unit nor real at.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String expressionMissmatch(
      final ODEPostProcessingVisitor coco,
      final String odeVariable,
      final String odeType,
      final String rhsType) {
    final String ERROR_MSG_FORMAT = "The type of (derived) variable " + odeVariable + " is: " + odeType +
                                    ". This does not match Type of RHS expression: " + rhsType;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final ODEPostProcessingVisitor coco) {
    return "NESTML_POST_PROCESSING_ERROR";
  }

  public static String message(final UnitsSIVisitor coco, final String unit) {
    final String ERROR_MSG_FORMAT = "The unit " + unit + " is not a valid SI unit.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final UnitsSIVisitor coco) {
    return "NESTML_SI_VISITOR";
  }

  public static String message(final FunctionCallVisitor coco, final String functionName) {
    final String ERROR_MSG_FORMAT = "Function " + functionName + " with the return-type 'Void'"
                                    + " cannot be used in expressions.";

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final FunctionCallVisitor coco) {
    return "NESTML_FUNCTION_CALL_VISITOR";
  }


  @SuppressWarnings({"unused"}) // used for the routing
  static String code(final DotOperatorVisitor coco) {
    return "NESTML_FUNCTION_CALL_VISITOR";
  }
  public static String message(final UnitRepresentation coco, final String representation) {
    final String ERROR_MSG_FORMAT = "Cannot factorize the Unit " + representation;

    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  @SuppressWarnings({"unused"}) // used for the routing
  public static String code(final UnitRepresentation coco) {
    return "NESTML_UNIT_REPRESENTATION";
  }

  public static String errorAssignmentToParameter(final IllegalAssignment coco,
                                                  final String lhsName,
                                                  final SourcePosition sourcePositionStart) {
    final String ERROR_MSG_FORMAT = "Cannot assign value to parameter symbol " + lhsName + " at " +sourcePositionStart;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  static String code(IllegalAssignment coco) {
    return "NESTML_ILLEGAL_ASSIGNMENT";
  }

  public static String errorAssignmentToAlias(final IllegalAssignment coco,
                                              final String lhsName,
                                              final SourcePosition sourcePositionStart) {
    final String ERROR_MSG_FORMAT = "Cannot assign value to alias symbol " + lhsName + " at " +sourcePositionStart;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String errorAssignmentToEquation( final IllegalAssignment coco,
                                                  final String lhsName,
                                                  final SourcePosition sourcePositionStart) {
    final String ERROR_MSG_FORMAT = "Cannot assign value to equation symbol " + lhsName + " at " +sourcePositionStart;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String errorAssignmentToInternal( final IllegalAssignment coco,
                                                  final String lhsName,
                                                  final SourcePosition sourcePositionStart) {
    final String ERROR_MSG_FORMAT = "Cannot assign value to internal symbol " + lhsName + " at " +sourcePositionStart;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String errorConvolveParameterNotAVariable(FunctionCallVisitor coco) {
    final String ERROR_MSG_FORMAT = "convolve() function needs a buffer parameter";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String errorConvolveParameterNotResolvable(FunctionCallVisitor coco, String bufferName) {
    final String ERROR_MSG_FORMAT = "Cannot resolve the variable: "+bufferName;
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String errorConvolveParameterMustBeBuffer(FunctionCallVisitor coco) {
    final String ERROR_MSG_FORMAT = "Parameter to the convolve() function is not a buffer.";
    return code(coco) + SEPARATOR + ERROR_MSG_FORMAT;
  }

  public static String errorCannotCalculateConvolveResult(FunctionCallVisitor coco) {
    final String ERROR_MSG_FORMAT = "Cannot calculate return type of convolve(). See other error messages.";
    return code(coco)  + SEPARATOR + ERROR_MSG_FORMAT;
  }
}

