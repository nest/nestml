/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable;

import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.ode._cocos.ODEASTOdeDeclarationCoCo;
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
    splCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);
    splCoCoChecker.addCoCo((ODEASTOdeDeclarationCoCo) variableExists);

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

  public void addSPLCocosToNESTMLChecker(NESTMLCoCoChecker splCoCoChecker) {
    final VariableDoesNotExist variableExists = new VariableDoesNotExist();
    splCoCoChecker.addCoCo((SPLASTCompound_StmtCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableExists);
    splCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);
    splCoCoChecker.addCoCo((ODEASTOdeDeclarationCoCo) variableExists);

    final VariableDefinedMultipleTimes variableDefinedMultipleTimes
        = new VariableDefinedMultipleTimes();
    splCoCoChecker.addCoCo(variableDefinedMultipleTimes);

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    splCoCoChecker.addCoCo(varHasTypeName);

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

}
