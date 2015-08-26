/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable;

import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.spl.cocos.*;
import org.nest.spl._cocos.*;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

/**
 * This class is responsible for the instantiation of the NESTML context conditions.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class SPLCoCosManager {

  private final PredefinedTypesFactory predefinedTypesFactory;

  public SPLCoCosManager(PredefinedTypesFactory predefinedTypesFactory) {
    this.predefinedTypesFactory = predefinedTypesFactory;
  }

  /**
   * @return A checker with all SPL context conditions
   */
  public SPLCoCoChecker createDefaultChecker() {
    final SPLCoCoChecker splCoCoChecker = new SPLCoCoChecker();

    createCoCosForSPL(splCoCoChecker);
    return splCoCoChecker;
  }

  public void createCoCosForSPL(SPLCoCoChecker splCoCoChecker) {
    final VariableDoesNotExist variableExists = new VariableDoesNotExist();
    splCoCoChecker.addCoCo((SPLASTCompound_StmtCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTFunctionCallCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);

    final VariableDefinedMultipleTimes variableDefinedMultipleTimes = new VariableDefinedMultipleTimes();
    splCoCoChecker.addCoCo(variableDefinedMultipleTimes);

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    splCoCoChecker.addCoCo(varHasTypeName);

    final VariableNotDefinedBeforeUse variableNotDefinedBeforeUse = new VariableNotDefinedBeforeUse();

    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) variableNotDefinedBeforeUse);

    final IllegalVarInFor illegalVarInFor = new IllegalVarInFor(predefinedTypesFactory);
    splCoCoChecker.addCoCo(illegalVarInFor);

    final IllegalExpression illegalExpression = new IllegalExpression(predefinedTypesFactory);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTELIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTWHILE_StmtCoCo) illegalExpression);

    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    splCoCoChecker.addCoCo(codeAfterReturn);

    final FunctionDoesntExist functionDoesntExist = new FunctionDoesntExist(predefinedTypesFactory);
    splCoCoChecker.addCoCo(functionDoesntExist);

    final CheckMultipleSignsBeforeFactor checkMultipleSignsBeforeFactor
        = new CheckMultipleSignsBeforeFactor();
    splCoCoChecker.addCoCo((SPLASTBlockCoCo) checkMultipleSignsBeforeFactor);
    splCoCoChecker.addCoCo((SPLASTBlockCoCo) checkMultipleSignsBeforeFactor);
  }

  public void addSPLCocosToNESTMLChecker(NESTMLCoCoChecker splCoCoChecker) {
    final VariableDoesNotExist variableExists = new VariableDoesNotExist();
    splCoCoChecker.addCoCo((SPLASTCompound_StmtCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTFunctionCallCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);

    final VariableDefinedMultipleTimes variableDefinedMultipleTimes
        = new VariableDefinedMultipleTimes();
    splCoCoChecker.addCoCo(variableDefinedMultipleTimes);

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    splCoCoChecker.addCoCo(varHasTypeName);

    final IllegalVarInFor illegalVarInFor = new IllegalVarInFor(predefinedTypesFactory);
    splCoCoChecker.addCoCo(illegalVarInFor);

    final IllegalExpression illegalExpression = new IllegalExpression(predefinedTypesFactory);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTELIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTWHILE_StmtCoCo) illegalExpression);

    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    splCoCoChecker.addCoCo(codeAfterReturn);

    final FunctionDoesntExist functionDoesntExist = new FunctionDoesntExist(predefinedTypesFactory);
    splCoCoChecker.addCoCo(functionDoesntExist);

    final CheckMultipleSignsBeforeFactor checkMultipleSignsBeforeFactor
        = new CheckMultipleSignsBeforeFactor();
    splCoCoChecker.addCoCo((SPLASTBlockCoCo) checkMultipleSignsBeforeFactor);
    splCoCoChecker.addCoCo((SPLASTExprCoCo) checkMultipleSignsBeforeFactor);
  }

}
