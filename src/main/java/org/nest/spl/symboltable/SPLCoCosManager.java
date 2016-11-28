/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable;

import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.spl._cocos.*;

/**
 * This class is responsible for the instantiation of the SPL context conditions.
 *
 * @author plotnikov
 */
public class SPLCoCosManager {

  /**
   * @return A checker with all SPL context conditions
   */
  SPLCoCoChecker createDefaultChecker() {
    final SPLCoCoChecker splCoCoChecker = new SPLCoCoChecker();

    createCoCosForSPL(splCoCoChecker);
    return splCoCoChecker;
  }

  private void createCoCosForSPL(final SPLCoCoChecker splCoCoChecker) {
    final VariableDoesNotExist variableExists = new VariableDoesNotExist();
    splCoCoChecker.addCoCo((SPLASTCompound_StmtCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableExists);
    splCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);

    final VariableDefinedMultipleTimes variableDefinedMultipleTimes = new VariableDefinedMultipleTimes();
    splCoCoChecker.addCoCo(variableDefinedMultipleTimes);

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    splCoCoChecker.addCoCo(varHasTypeName);

    final VariableNotDefinedBeforeUse variableNotDefinedBeforeUse = new VariableNotDefinedBeforeUse();

    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) variableNotDefinedBeforeUse);

    final IllegalVarInFor illegalVarInFor = new IllegalVarInFor();
    splCoCoChecker.addCoCo(illegalVarInFor);

    final IllegalExpression illegalExpression = new IllegalExpression();
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTELIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTWHILE_StmtCoCo) illegalExpression);

    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    splCoCoChecker.addCoCo(codeAfterReturn);

    final FunctionDoesNotExist functionDoesNotExist = new FunctionDoesNotExist();
    splCoCoChecker.addCoCo(functionDoesNotExist);

  }

  public void addSPLCocosToNESTMLChecker(final NESTMLCoCoChecker nestmlCoCoChecker) {

    final VariableNotDefinedBeforeUse variableNotDefinedBeforeUse = new VariableNotDefinedBeforeUse();

    nestmlCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableNotDefinedBeforeUse);
    nestmlCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableNotDefinedBeforeUse);
    nestmlCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) variableNotDefinedBeforeUse);

    final VariableDefinedMultipleTimes variableDefinedMultipleTimes = new VariableDefinedMultipleTimes();
    nestmlCoCoChecker.addCoCo(variableDefinedMultipleTimes);

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    nestmlCoCoChecker.addCoCo(varHasTypeName);

    final IllegalVarInFor illegalVarInFor = new IllegalVarInFor();
    nestmlCoCoChecker.addCoCo(illegalVarInFor);

    final IllegalExpression illegalExpression = new IllegalExpression();
    nestmlCoCoChecker.addCoCo((SPLASTAssignmentCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((SPLASTDeclarationCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((SPLASTELIF_ClauseCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((SPLASTIF_ClauseCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((SPLASTWHILE_StmtCoCo) illegalExpression);

    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    nestmlCoCoChecker.addCoCo(codeAfterReturn);

    final FunctionDoesNotExist functionDoesNotExist = new FunctionDoesNotExist();
    nestmlCoCoChecker.addCoCo(functionDoesNotExist);

  }

  public void addVariableExistenceCheck(final NESTMLCoCoChecker nestmlCoCoChecker) {
    final VariableDoesNotExist variableExists = new VariableDoesNotExist();
    nestmlCoCoChecker.addCoCo((SPLASTCompound_StmtCoCo) variableExists);
    nestmlCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableExists);
    nestmlCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableExists);
    nestmlCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo) variableExists);
    nestmlCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);
  }

}
