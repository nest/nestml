/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._cocos.CommonsASTExprCoCo;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._cocos.*;
import org.nest.ode._cocos.ODEASTOdeDeclarationCoCo;
import org.nest.spl._cocos.SPLASTAssignmentCoCo;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl._cocos.VarHasTypeName;
import org.nest.spl._cocos.VariableDefinedMultipleTimes;
import org.nest.spl.symboltable.SPLCoCosManager;
import org.nest.utils.LogHelper;

import java.util.List;

/**
 * This class is responsible for the instantiation of the NESTML context conditions.
 *
 * @author plotnikov
 */
public class NestmlCoCosManager {

  private final NESTMLCoCoChecker variablesExistenceChecker = new NESTMLCoCoChecker();
  private final NESTMLCoCoChecker nestmlCoCoChecker = new NESTMLCoCoChecker();
  private final NESTMLCoCoChecker uniquenessChecker = new NESTMLCoCoChecker();

  public NestmlCoCosManager() {
    registerVariableExistenceChecks();
    registerCocos();
  }

  public List<Finding> analyzeModel(final ASTNESTMLCompilationUnit root) {
    Log.getFindings().clear();
    variablesExistenceChecker.checkAll(root);
    final boolean allVariablesDefined = !Log.getFindings().stream().filter(Finding::isError).findAny().isPresent();

    if (allVariablesDefined) {
      nestmlCoCoChecker.checkAll(root);
    }
    return LogHelper.getModelFindings(Log.getFindings());
  }

  private void registerVariableExistenceChecks() {
    final VariableDoesNotExist variableDoesNotExist = new VariableDoesNotExist();
    nestmlCoCoChecker.addCoCo((ODEASTOdeDeclarationCoCo) variableDoesNotExist);
    nestmlCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo) variableDoesNotExist);
    final SPLCoCosManager splCoCosManager = new SPLCoCosManager();
    splCoCosManager.addVariableExistenceCheck(variablesExistenceChecker);
  }

  private void registerCocos() {
    final AliasHasNoSetter aliasHasNoSetter = new AliasHasNoSetter();
    nestmlCoCoChecker.addCoCo(aliasHasNoSetter);

    final AliasHasDefiningExpression aliasHasDefiningExpression = new AliasHasDefiningExpression();
    nestmlCoCoChecker.addCoCo(aliasHasDefiningExpression);

    final AliasHasOneVar aliasHasOneVar = new AliasHasOneVar();
    nestmlCoCoChecker.addCoCo(aliasHasOneVar);

    final VectorVariableInNonVectorDeclaration vectorVariableInNonVectorDeclaration = new VectorVariableInNonVectorDeclaration();
    nestmlCoCoChecker.addCoCo(vectorVariableInNonVectorDeclaration);

    final ComponentHasNoDynamics componentHasNoDynamics = new ComponentHasNoDynamics();
    nestmlCoCoChecker.addCoCo(componentHasNoDynamics);

    final ComponentWithoutInput componentWithoutInput = new ComponentWithoutInput();
    nestmlCoCoChecker.addCoCo(componentWithoutInput);

    final ComponentWithoutOutput componentWithoutOutput = new ComponentWithoutOutput();
    nestmlCoCoChecker.addCoCo(componentWithoutOutput);

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


    final LiteralsHaveTypes literalsHaveTypes = new LiteralsHaveTypes();
    nestmlCoCoChecker.addCoCo((SPLASTAssignmentCoCo)literalsHaveTypes);
    nestmlCoCoChecker.addCoCo((SPLASTDeclarationCoCo)literalsHaveTypes);
    nestmlCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo)literalsHaveTypes);
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCoCo)literalsHaveTypes);
    nestmlCoCoChecker.addCoCo((CommonsASTExprCoCo)literalsHaveTypes);

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

    final SumHasCorrectParameter _sumHasCorrectParameter = new SumHasCorrectParameter();
    nestmlCoCoChecker.addCoCo(_sumHasCorrectParameter);

    final EquationsOnlyForStateVariables equationsOnlyForStateVariables = new EquationsOnlyForStateVariables();
    nestmlCoCoChecker.addCoCo(equationsOnlyForStateVariables);

    final DerivativeOrderAtLeastOne derivativeOrderAtLeastOne = new DerivativeOrderAtLeastOne();
    nestmlCoCoChecker.addCoCo(derivativeOrderAtLeastOne);

    final AssignmentToAlias assignmentToAlias = new AssignmentToAlias();
    nestmlCoCoChecker.addCoCo(assignmentToAlias);

    final SPLCoCosManager splCoCosManager = new SPLCoCosManager();
    splCoCosManager.addSPLCocosToNESTMLChecker(nestmlCoCoChecker);
  }

  List<Finding> checkVariableUniqueness(final ASTNeuron astNeuron) {
    Log.getFindings().clear();

    uniquenessChecker.addCoCo(new VariableDefinedMultipleTimes());

    final MemberVariableDefinedMultipleTimes memberVariableDefinedMultipleTimes = new MemberVariableDefinedMultipleTimes();
    uniquenessChecker.addCoCo((NESTMLASTComponentCoCo) memberVariableDefinedMultipleTimes);
    uniquenessChecker.addCoCo((NESTMLASTNeuronCoCo) memberVariableDefinedMultipleTimes);
    uniquenessChecker.checkAll(astNeuron);

    return LogHelper.getModelFindings(Log.getFindings());
  }

}
