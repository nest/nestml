/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

/**
 * Factory for CoCo error strings.
 *
 * @author traeder
 */
public class CocoErrorStrings {
    private static CocoErrorStrings instance = new CocoErrorStrings();

    private CocoErrorStrings() {
    }

    public static CocoErrorStrings getInstance() {
        return instance;
    }

    public String getErrorMsg(AliasHasDefiningExpression coco) {
        return coco.ERROR_CODE + ":" + "'alias' must be defined through an expression.";
    }

    public String getErrorMsg(AliasHasNoSetter coco, String aliasVar, String varTypeName) {
        return coco.ERROR_CODE + ":" + "Alias-variable '" + aliasVar + "' needs a setter-function: set_"
                + aliasVar + "(v " + varTypeName + ")";
    }

    public String getErrorMsg(AliasHasOneVar coco) {
        return coco.ERROR_CODE + ":" + "'alias' declarations must only declare one variable.";
    }

    public String getErrorMsg(AliasInNonAliasDecl coco, String usedAlias) {
        return coco.ERROR_CODE + ":" + "Alias variable '"
                + usedAlias
                + "' cannot be used in default-value declaration of non-alias variables.";
    }

    public String getErrorMsgInvariantMustBeBoolean(BooleanInvariantExpressions coco, String expressionType) {
        return coco.ERROR_CODE + ":" + "The type of the invariant expression must be boolean and not: " +
                expressionType;
    }

    public String getErrorMsgCannotComputeType(BooleanInvariantExpressions coco, String invariantType) {
        return coco.ERROR_CODE + ":" + "Cannot compute the type: " + invariantType;
    }

    public String getErrorMsg(BufferNotAssignable coco, String bufferName) {
        return coco.ERROR_CODE + ":" + "Buffer '" + bufferName + "' cannot be reassigned.";
    }

    public String getErrorMsg(ComponentHasNoDynamics coco) {
        return coco.ERROR_CODE + ":" + "Components do not have dynamics function.";
    }

    public String getErrorMsg(ComponentNoInput coco) {
        return coco.ERROR_CODE + ":" + "Components cannot have inputs, since they are not elements of a "
                + "neuronal network.";
    }

    public String getErrorMsg(ComponentNoOutput coco) {
        return coco.ERROR_CODE + ":" + "Components do not have outputs, only neurons have outputs.";
    }

    public String getErrorMsgWrongReturnType(CorrectReturnValues coco,
                              String functionName, String functionReturnTypeName) {
        return coco.ERROR_CODE + ":" + "Function '" + functionName + "' must return a result of type "
                + functionReturnTypeName + ".";
    }

    public String getErrorMsgCannotConvertReturnValue(CorrectReturnValues coco,
                              String expressionTypeName, String functionReturnTypeName) {
        return coco.ERROR_CODE + ":" + "Cannot convert from " + expressionTypeName
                + " (type of return expression) to " + functionReturnTypeName
                + " (return type), since the first is real domain and the second is in the integer "
                + "domain and conversion reduces the precision.";
    }

    public String getErrorMsgCannotDetermineExpressionType(CorrectReturnValues coco) {
        return coco.ERROR_CODE + ":" + "Cannot determine the type of the expression";
    }

    public String getErrorMsg(CurrentInputIsNotInhExc coco) {
        return coco.ERROR_CODE + ":" + "Current input can neither be inhibitory nor excitatory.";
    }

    public String getErrorMsgAssignToNonState(EquationsOnlyForStateVariables coco,
                              String variableName) {
        return coco.ERROR_CODE + ":" + "The variable '" + variableName + "' is not a state"
                + " variable and, therefore, cannot be used on the left side of an equation.";
    }

    public String getErrorMsgVariableNotDefined(EquationsOnlyForStateVariables coco) {
        return coco.ERROR_CODE + ":" + "Variable is not defined in the current scope.";
    }

    public String getErrorMsg(FunctionHasReturnStatement coco, String functionName, String returnType) {
        return coco.ERROR_CODE + ":" + "Function '" + functionName
                + "' must return a result of type '"
                + returnType;
    }

    public String getErrorMsgGet_InstanceDefined(GetterSetterFunctionNames coco) {
        return coco.ERROR_CODE + ":" + "The function 'get_instance' is going to be generated. Please use another name.";
    }

    public String getErrorMsgGeneratedFunctionDefined(GetterSetterFunctionNames coco,
                              String functionName, String variableName) {
        return coco.ERROR_CODE + ":" + "The function '" + functionName + "' is going to be generated, since"
                + " there is a variable called '" + variableName + "'.";
    }

    public String getErrorMsg(I_SumHasCorrectParameter coco, String expression) {
        return coco.ERROR_CODE + ":" + "The arguments of the I_sum must be atomic expressions: "
                + "e.g. V_m and not : " + expression;
    }

    public String getErrorMsg(InvalidTypesInDeclaration coco, String typeName) {
        return coco.ERROR_CODE + ":" + "The type "+ typeName+ " is a neuron/component. No neurons/components allowed " +
                "in this place. Use the use-statement.";
    }

    public String getErrorMsg(MemberVariableDefinedMultipleTimes coco, String varName,
                              int line, int column) {
        return coco.ERROR_CODE + ":" + "Variable '" + varName + "' defined previously defined i line: "
                + line + ":" + column;
    }

    public String getErrorMsgDeclaredInIncorrectOrder(MemberVariablesInitialisedInCorrectOrder coco,
                              String varName, String declaredName) {
        return coco.ERROR_CODE + ":" + "Variable '"
                + varName
                + "' must be declared before it can be used in declaration of '"
                + declaredName + "'.";
    }

    public String getErrorMsgVariableNotDefined(MemberVariablesInitialisedInCorrectOrder coco,
                                                      String pos, String varName) {
        return coco.ERROR_CODE + ":" + pos + ": Variable '" +
                varName + "' is undefined.";
    }

    public String getErrorMsgNeuronHasNoSymbol(MultipleFunctionDeclarations coco, String neuronName) {
        return coco.ERROR_CODE + ":" + "The neuron symbol: " + neuronName+ " has no symbol.";
    }

    public String getErrorMsgParameterDefinedMultipleTimes(MultipleFunctionDeclarations coco, String funname) {
        return coco.ERROR_CODE + ":" + "The function '" + funname
                + " parameter(s) is defined multiple times.";
    }

    public String getErrorMsgNoScopePresent(MultipleFunctionDeclarations coco) {
        return coco.ERROR_CODE + ":" + "Run symbol table creator.";
    }

    public String getErrorMsgMultipleInhibitory(MultipleInhExcInput coco) {
        return coco.ERROR_CODE + ":" + "Multiple occurrences of the keyword 'inhibitory' are not allowed.";
    }

    public String getErrorMsgMultipleExcitatory(MultipleInhExcInput coco) {
        return coco.ERROR_CODE + ":" + "Multiple occurrences of the keyword 'excitatory' are not allowed.";
    }

    public String getErrorMsg(MultipleOutputs coco, int numOutput) {
        return coco.ERROR_CODE + ":" + "Neurons have at most one output and not " + numOutput + ".";
    }

    public String getErrorMsg(NESTFunctionNameChecker coco, String funName) {
        return coco.ERROR_CODE + ":" + "The function-name '" + funName
                + "' is already used by NEST. Please use another name.";
    }

    public String getErrorMsgDynamicsNotPresent(NeuronNeedsDynamics coco) {
        return coco.ERROR_CODE + ":" + "Neurons need at least one dynamics function.";
    }

    public String getErrorMsgMultipleDynamics(NeuronNeedsDynamics coco) {
        return coco.ERROR_CODE + ":" + "Neurons need at most one dynamics function.";
    }

    public String getErrorMsg(NeuronWithoutInput coco) {
        return coco.ERROR_CODE + ":" + "Neurons need some inputs.";
    }

    public String getErrorMsg(NeuronWithoutOutput coco) {
        return coco.ERROR_CODE + ":" + "Neurons need some outputs.";
    }

    public String getErrorMsg(TypeIsDeclaredMultipleTimes coco, String typeName) {
        return coco.ERROR_CODE + ":" + "The type '" + typeName + "' is defined multiple times.";
    }

    public String getErrorMsgOnlyComponentsForNeurons(UsesOnlyComponents coco, String typeName,
                                                      String predefinedTypeName) {
        return coco.ERROR_CODE + ":" + "Only components can be used by neurons/components and not " + typeName + " of the type: " +
                predefinedTypeName + " .";
    }

    public String getErrorMsgOnlyComponentsForComponents(UsesOnlyComponents coco, String typeName) {
        return coco.ERROR_CODE + ":" + "Only components can be used by components and not " + typeName + " that is a neuron, not a "
                + "component";
    }
}
