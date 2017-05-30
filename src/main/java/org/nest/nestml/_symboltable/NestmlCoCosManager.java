/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._symboltable;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.nestml._ast.ASTNESTMLNode;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._cocos.*;
import org.nest.nestml._cocos.DerivativeOrderAtLeastOne;
import org.nest.nestml._cocos.EquationsOnlyForStateVariables;
import org.nest.nestml._cocos.SumHasCorrectParameter;
import org.nest.nestml._cocos.VariableDoesNotExist;
import org.nest.nestml._cocos.BlockVariableDefinedMultipleTimes;
import org.nest.nestml._cocos.VariableHasTypeName;
import org.nest.units._cocos.UnitDeclarationOnlyOnesAllowed;
import org.nest.utils.LogHelper;

import java.util.List;

/**
 * This class is responsible for the instantiation of the NESTML context conditions.
 *
 * @author plotnikov
 */
public class NestmlCoCosManager {

  private final NESTMLCoCoChecker existenceChecker = new NESTMLCoCoChecker();
  private final NESTMLCoCoChecker multipleDefinitionChecker = new NESTMLCoCoChecker();
  private final NESTMLCoCoChecker nestmlCoCoChecker = new NESTMLCoCoChecker();

  public NestmlCoCosManager() {
    registerExistenceChecks();
    registerMultipleDefinitionsChecksChecks();
    registerCocos();
  }

  public List<Finding> analyzeModel(final ASTNESTMLNode root) {
    Log.getFindings().clear();
    existenceChecker.checkAll(root);
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

  private void registerExistenceChecks() {
    final VariableDoesNotExist variableDoesNotExist = new VariableDoesNotExist();
    existenceChecker.addCoCo((CommonsASTFunctionCallCoCo) variableDoesNotExist);
    existenceChecker.addCoCo((NESTMLASTAssignmentCoCo) variableDoesNotExist);
    existenceChecker.addCoCo((NESTMLASTCompound_StmtCoCo) variableDoesNotExist);
    existenceChecker.addCoCo((NESTMLASTDeclarationCoCo) variableDoesNotExist);
    existenceChecker.addCoCo((NESTMLASTOdeDeclarationCoCo) variableDoesNotExist);
    existenceChecker.addCoCo((NESTMLASTDeclarationCoCo) variableDoesNotExist);

    final FunctionDoesNotExist functionDoesNotExist = new FunctionDoesNotExist();
    existenceChecker.addCoCo(functionDoesNotExist);
  }


  private void registerMultipleDefinitionsChecksChecks() {
    final MemberVariableDefinedMultipleTimes memberVariableDefinedMultipleTimes
        = new MemberVariableDefinedMultipleTimes();
    multipleDefinitionChecker.addCoCo(memberVariableDefinedMultipleTimes);

    final FunctionDefinedMultipleTimes functionDefinedMultipleTimes
        = new FunctionDefinedMultipleTimes();
    multipleDefinitionChecker.addCoCo(functionDefinedMultipleTimes);

    final VariableHasTypeName variableHasTypeName = new VariableHasTypeName();
    multipleDefinitionChecker.addCoCo(variableHasTypeName);
    multipleDefinitionChecker.addCoCo(new BlockVariableDefinedMultipleTimes());
  }

  private void registerCocos() {


    final VariableNotDefinedBeforeUse variableNotDefinedBeforeUse = new VariableNotDefinedBeforeUse();

    nestmlCoCoChecker.addCoCo((NESTMLASTAssignmentCoCo) variableNotDefinedBeforeUse);
    nestmlCoCoChecker.addCoCo((NESTMLASTDeclarationCoCo) variableNotDefinedBeforeUse);
    nestmlCoCoChecker.addCoCo((NESTMLASTFOR_StmtCoCo) variableNotDefinedBeforeUse);

    final BlockVariableDefinedMultipleTimes variableDefinedMultipleTimes = new BlockVariableDefinedMultipleTimes();
    nestmlCoCoChecker.addCoCo(variableDefinedMultipleTimes);

    final VariableHasTypeName variableHasTypeName = new VariableHasTypeName();
    nestmlCoCoChecker.addCoCo(variableHasTypeName);

    final IllegalExpression illegalExpression = new IllegalExpression();
    nestmlCoCoChecker.addCoCo((NESTMLASTAssignmentCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTDeclarationCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTELIF_ClauseCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTFOR_StmtCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTIF_ClauseCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTWHILE_StmtCoCo) illegalExpression);

    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    nestmlCoCoChecker.addCoCo(codeAfterReturn);


    final AliasHasDefiningExpression aliasHasDefiningExpression = new AliasHasDefiningExpression();
    nestmlCoCoChecker.addCoCo(aliasHasDefiningExpression);

    final AliasHasOneVar aliasHasOneVar = new AliasHasOneVar();
    nestmlCoCoChecker.addCoCo(aliasHasOneVar);

    final VectorVariableInNonVectorDeclaration vectorVariableInNonVectorDeclaration = new VectorVariableInNonVectorDeclaration();
    nestmlCoCoChecker.addCoCo(vectorVariableInNonVectorDeclaration);

    final CurrentPortIsInhOrExc currentPortIsInhOrExc = new CurrentPortIsInhOrExc();
    nestmlCoCoChecker.addCoCo(currentPortIsInhOrExc);

    final MissingReturnStatementInFunction missingReturnStatementInFunction = new MissingReturnStatementInFunction();
    nestmlCoCoChecker.addCoCo(missingReturnStatementInFunction);

    final InvalidTypesInDeclaration invalidTypesInDeclaration = new InvalidTypesInDeclaration();
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((NESTMLASTDeclarationCoCo) invalidTypesInDeclaration);


    final UnitDeclarationOnlyOnesAllowed unitDeclarationOnlyOnesAllowed = new UnitDeclarationOnlyOnesAllowed();
    nestmlCoCoChecker.addCoCo(unitDeclarationOnlyOnesAllowed);


    final MemberVariablesInitialisedInCorrectOrder memberVariablesInitialisedInCorrectOrder
            = new MemberVariablesInitialisedInCorrectOrder();
    nestmlCoCoChecker.addCoCo(memberVariablesInitialisedInCorrectOrder);

    final FunctionDefinedMultipleTimes functionDefinedMultipleTimes = new FunctionDefinedMultipleTimes();
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
  }

  List<Finding> checkThatVariablesDefinedOnce(final ASTNeuron astNeuron) {
    Log.getFindings().clear();

    existenceChecker.checkAll(astNeuron);
    multipleDefinitionChecker.checkAll(astNeuron);

    return LogHelper.getModelFindings(Log.getFindings());
  }

}
