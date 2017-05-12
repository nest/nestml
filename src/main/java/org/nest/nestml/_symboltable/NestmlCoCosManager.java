/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._cocos.*;
import org.nest.ode._cocos.DerivativeOrderAtLeastOne;
import org.nest.ode._cocos.EquationsOnlyForStateVariables;
import org.nest.ode._cocos.SumHasCorrectParameter;
import org.nest.ode._cocos.VariableDoesNotExist;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl._cocos.SPLVariableDefinedMultipleTimes;
import org.nest.spl._cocos.VariableHasTypeName;
import org.nest.spl.symboltable.SPLCoCosManager;
import org.nest.units._cocos.UnitDeclarationOnlyOnesAllowed;
import org.nest.utils.LogHelper;

import java.util.List;

/**
 * This class is responsible for the instantiation of the NESTML context conditions.
 *
 * @author plotnikov
 */
public class NestmlCoCosManager {

  private final NESTMLCoCoChecker variablesExistenceChecker = new NESTMLCoCoChecker();
  private final NESTMLCoCoChecker multipleDefinitionChecker = new NESTMLCoCoChecker();
  private final NESTMLCoCoChecker nestmlCoCoChecker = new NESTMLCoCoChecker();

  public NestmlCoCosManager() {
    registerVariableExistenceChecks();
    registerMultipleDefinitionChecksChecks();
    registerCocos();
  }

  public List<Finding> analyzeModel(final ASTNESTMLNode root) {
    Log.getFindings().clear();
    variablesExistenceChecker.checkAll(root);
    final boolean allVariablesDefined = Log.getFindings().stream().noneMatch(Finding::isError);
    if (!allVariablesDefined) {
      return LogHelper.getModelFindings(Log.getFindings());
    }

    multipleDefinitionChecker.checkAll(root);
    final boolean allVariablesDefinedAtMostOnce = Log.getFindings().stream().noneMatch(Finding::isError);
    if (!allVariablesDefinedAtMostOnce) {
      return LogHelper.getModelFindings(Log.getFindings());
    }
    else {
      nestmlCoCoChecker.checkAll(root);
    }

    return LogHelper.getModelFindings(Log.getFindings());
  }

  private void registerVariableExistenceChecks() {
    final VariableDoesNotExist variableDoesNotExist = new VariableDoesNotExist();
    variablesExistenceChecker.addCoCo(variableDoesNotExist);
    SPLCoCosManager.addVariableExistenceCheck(variablesExistenceChecker);
  }


  private void registerMultipleDefinitionChecksChecks() {
    final MemberVariableDefinedMultipleTimes memberVariableDefinedMultipleTimes
        = new MemberVariableDefinedMultipleTimes();
    multipleDefinitionChecker.addCoCo(memberVariableDefinedMultipleTimes);

    final FunctionDefinedMultipleTimes functionDefinedMultipleTimes
        = new FunctionDefinedMultipleTimes();
    multipleDefinitionChecker.addCoCo(functionDefinedMultipleTimes);

    multipleDefinitionChecker.addCoCo(new SPLVariableDefinedMultipleTimes());
  }

  private void registerCocos() {
    final AliasHasDefiningExpression aliasHasDefiningExpression = new AliasHasDefiningExpression();
    nestmlCoCoChecker.addCoCo(aliasHasDefiningExpression);

    final AliasHasOneVar aliasHasOneVar = new AliasHasOneVar();
    nestmlCoCoChecker.addCoCo(aliasHasOneVar);

    final VectorVariableInNonVectorDeclaration vectorVariableInNonVectorDeclaration = new VectorVariableInNonVectorDeclaration();
    nestmlCoCoChecker.addCoCo(vectorVariableInNonVectorDeclaration);

    final CurrentPortIsInhOrExc currentPortIsInhOrExc = new CurrentPortIsInhOrExc();
    nestmlCoCoChecker.addCoCo(currentPortIsInhOrExc);

    final MissingReturnStatementInFunction missingReturnStatementInFunction
        = new MissingReturnStatementInFunction();
    nestmlCoCoChecker.addCoCo(missingReturnStatementInFunction);

    final InvalidTypesInDeclaration invalidTypesInDeclaration
        = new InvalidTypesInDeclaration();
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((SPLASTDeclarationCoCo) invalidTypesInDeclaration);


    final UnitDeclarationOnlyOnesAllowed unitDeclarationOnlyOnesAllowed = new UnitDeclarationOnlyOnesAllowed();
    nestmlCoCoChecker.addCoCo(unitDeclarationOnlyOnesAllowed);


    final MemberVariablesInitialisedInCorrectOrder memberVariablesInitialisedInCorrectOrder
            = new MemberVariablesInitialisedInCorrectOrder();
    nestmlCoCoChecker.addCoCo(memberVariablesInitialisedInCorrectOrder);

    final FunctionDefinedMultipleTimes functionDefinedMultipleTimes
            = new FunctionDefinedMultipleTimes();
    nestmlCoCoChecker.addCoCo(functionDefinedMultipleTimes);

    final MultipleInhExcModifiers multipleInhExcModifiers = new MultipleInhExcModifiers();
    nestmlCoCoChecker.addCoCo(multipleInhExcModifiers);

    final NeuronWithMultipleOrNoOutput neuronWithMultipleOrNoOutput = new NeuronWithMultipleOrNoOutput();
    nestmlCoCoChecker.addCoCo(neuronWithMultipleOrNoOutput);

    final NestFunctionCollision functionNameChecker = new NestFunctionCollision();
    nestmlCoCoChecker.addCoCo(functionNameChecker);

    final FunctionParameterHasTypeName FunctionParameterHasTypeName = new FunctionParameterHasTypeName();
    nestmlCoCoChecker.addCoCo(FunctionParameterHasTypeName);

    final GetterSetterFunctionNames getterSetterFunctionNames = new GetterSetterFunctionNames();
    nestmlCoCoChecker.addCoCo(getterSetterFunctionNames);

    final NeuronWithMultipleOrNoUpdate neuronWithMultipleOrNoUpdate = new NeuronWithMultipleOrNoUpdate();
    nestmlCoCoChecker.addCoCo(neuronWithMultipleOrNoUpdate);

    final NeuronWithMultipleOrNoInput neuronWithMultipleOrNoInput = new NeuronWithMultipleOrNoInput();
    nestmlCoCoChecker.addCoCo(neuronWithMultipleOrNoInput);

    final RestrictUseOfShapes restrictUseOfShapes = new RestrictUseOfShapes();
    nestmlCoCoChecker.addCoCo(restrictUseOfShapes);

    final FunctionReturnsIncorrectValue functionReturnsIncorrectValue = new FunctionReturnsIncorrectValue();
    nestmlCoCoChecker.addCoCo(functionReturnsIncorrectValue);

    final TypeIsDeclaredMultipleTimes typeIsDeclaredMultipleTimes = new TypeIsDeclaredMultipleTimes();
    nestmlCoCoChecker.addCoCo(typeIsDeclaredMultipleTimes);


    final BufferNotAssignable bufferNotAssignable = new BufferNotAssignable();
    nestmlCoCoChecker.addCoCo(bufferNotAssignable);

    final VariableHasTypeName variableHasTypeName = new VariableHasTypeName();
    nestmlCoCoChecker.addCoCo(variableHasTypeName);

    final SumHasCorrectParameter _sumHasCorrectParameter = new SumHasCorrectParameter();
    nestmlCoCoChecker.addCoCo(_sumHasCorrectParameter);

    final EquationsOnlyForStateVariables equationsOnlyForStateVariables = new EquationsOnlyForStateVariables();
    nestmlCoCoChecker.addCoCo(equationsOnlyForStateVariables);

    final DerivativeOrderAtLeastOne derivativeOrderAtLeastOne = new DerivativeOrderAtLeastOne();
    nestmlCoCoChecker.addCoCo(derivativeOrderAtLeastOne);

    final AssignmentToAlias assignmentToAlias = new AssignmentToAlias();
    nestmlCoCoChecker.addCoCo(assignmentToAlias);

    final VariableBlockDefinedMultipleTimes variableBlockDefinedMultipleTimes = new VariableBlockDefinedMultipleTimes();
    nestmlCoCoChecker.addCoCo(variableBlockDefinedMultipleTimes);

    final SPLCoCosManager splCoCosManager = new SPLCoCosManager();
    splCoCosManager.addSPLCocosToNESTMLChecker(nestmlCoCoChecker);
  }

  List<Finding> checkThatVariablesDefinedOnce(final ASTNeuron astNeuron) {
    Log.getFindings().clear();

    variablesExistenceChecker.checkAll(astNeuron);
    multipleDefinitionChecker.checkAll(astNeuron);

    return LogHelper.getModelFindings(Log.getFindings());
  }


}
