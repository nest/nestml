/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import org.nest.nestml.cocos.*;
import org.nest.nestml.cocos.BufferNotAssignable;
import org.nest.nestml._cocos.*;
import org.nest.spl.cocos.VarHasTypeName;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl.symboltable.SPLCoCosManager;

/**
 * This class is responsible for the instantiation of the NESTML context conditions.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLCoCosManager {

  /**
   * @return A checker with all NESTML context conditions
   */
  public NESTMLCoCoChecker createDefaultChecker() {
    final NESTMLCoCoChecker nestmlCoCoChecker = new NESTMLCoCoChecker();

    final AliasHasNoSetter aliasHasNoSetter = new AliasHasNoSetter();
    nestmlCoCoChecker.addCoCo(aliasHasNoSetter);

    final AliasHasDefiningExpression aliasHasDefiningExpression = new AliasHasDefiningExpression();
    nestmlCoCoChecker.addCoCo(aliasHasDefiningExpression);

    final AliasHasOneVar aliasHasOneVar = new AliasHasOneVar();
    nestmlCoCoChecker.addCoCo(aliasHasOneVar);

    final AliasInNonAliasDecl aliasInNonAliasDecl = new AliasInNonAliasDecl();

    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) aliasInNonAliasDecl);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) aliasInNonAliasDecl);

    final ComponentHasNoDynamics componentHasNoDynamics = new ComponentHasNoDynamics();
    nestmlCoCoChecker.addCoCo(componentHasNoDynamics);

    final ComponentNoInput componentNoInput = new ComponentNoInput();
    nestmlCoCoChecker.addCoCo(componentNoInput);

    final ComponentNoOutput componentNoOutput = new ComponentNoOutput();
    nestmlCoCoChecker.addCoCo(componentNoOutput);

    final CurrentInputIsNotInhExc currentInputIsNotInhExc = new CurrentInputIsNotInhExc();
    nestmlCoCoChecker.addCoCo(currentInputIsNotInhExc);

    final FunctionHasReturnStatement functionHasReturnStatement
        = new FunctionHasReturnStatement();
    nestmlCoCoChecker.addCoCo(functionHasReturnStatement);

    final InvalidTypesInDeclaration invalidTypesInDeclaration
        = new InvalidTypesInDeclaration();
    nestmlCoCoChecker.addCoCo((NESTMLASTUSE_StmtCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((SPLASTDeclarationCoCo) invalidTypesInDeclaration);

    final MemberVariableDefinedMultipleTimes memberVariableDefinedMultipleTimes
        = new MemberVariableDefinedMultipleTimes();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) memberVariableDefinedMultipleTimes);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) memberVariableDefinedMultipleTimes);

    final MemberVariablesInitialisedInCorrectOrder memberVariablesInitialisedInCorrectOrder
            = new MemberVariablesInitialisedInCorrectOrder();
    nestmlCoCoChecker.addCoCo(memberVariablesInitialisedInCorrectOrder);

    final MultipleFunctionDeclarations multipleFunctionDeclarations
            = new MultipleFunctionDeclarations();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) multipleFunctionDeclarations);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) multipleFunctionDeclarations);

    final MultipleInhExcInput multipleInhExcInput = new MultipleInhExcInput();
    nestmlCoCoChecker.addCoCo(multipleInhExcInput);

    final MultipleOutputs multipleOutputs = new MultipleOutputs();
    nestmlCoCoChecker.addCoCo(multipleOutputs);

    final NESTFunctionNameChecker functionNameChecker = new NESTFunctionNameChecker();
    nestmlCoCoChecker.addCoCo(functionNameChecker);

    final GetterSetterFunctionNames getterSetterFunctionNames = new GetterSetterFunctionNames();
    nestmlCoCoChecker.addCoCo(getterSetterFunctionNames);

    final NeuronNeedsDynamics neuronNeedsDynamics = new NeuronNeedsDynamics();
    nestmlCoCoChecker.addCoCo(neuronNeedsDynamics);

    final NeuronWithoutInput neuronWithoutInput = new NeuronWithoutInput();
    nestmlCoCoChecker.addCoCo(neuronWithoutInput);

    final NeuronWithoutOutput neuronWithoutOutput = new NeuronWithoutOutput();
    nestmlCoCoChecker.addCoCo(neuronWithoutOutput);

    final CorrectReturnValues correctReturnValues = new CorrectReturnValues();
    nestmlCoCoChecker.addCoCo(correctReturnValues);

    final TypeIsDeclaredMultipleTimes typeIsDeclaredMultipleTimes = new TypeIsDeclaredMultipleTimes();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) typeIsDeclaredMultipleTimes);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) typeIsDeclaredMultipleTimes);

    // TODO
    // UsesOnlyComponents
    final BufferNotAssignable bufferNotAssignable = new BufferNotAssignable();
    nestmlCoCoChecker.addCoCo(bufferNotAssignable);

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    nestmlCoCoChecker.addCoCo(varHasTypeName);

    return nestmlCoCoChecker;
  }

  public NESTMLCoCoChecker createNESTMLCheckerWithSPLCocos() {
    final NESTMLCoCoChecker nestmlChecker = createDefaultChecker();
    new SPLCoCosManager().addSPLCocosToNESTMLChecker(nestmlChecker);
    return nestmlChecker;
  }

}
