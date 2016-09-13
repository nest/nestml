/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import de.se_rwth.commons.logging.Log;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;
import org.nest.spl.symboltable.SPLScopeCreator;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.getFindings;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.utils.LogHelper.countErrorsByPrefix;

/**
 * Test every context context conditions. For each implemented context condition there is one model that contains exactly one tested error.
 *
 * @author plotnikov
 */
public class SPLCoCosTest {
  private static final String TEST_MODEL_PATH = "src/test/resources/";
  private static final String TEST_MODELS_FOLDER = "src/test/resources/org/nest/spl/_cocos/";
  private final SPLScopeCreator splScopeCreator = new SPLScopeCreator(TEST_MODEL_PATH);
  private SPLCoCoChecker splCoCoChecker;
  /**
   * Parses the model and returns ast.
   */
  private ASTSPLFile getAstRoot(String modelPath)  {
    final SPLParser p = new SPLParser();
    final Optional<ASTSPLFile> ast;
    try {
      ast = p.parse(modelPath);
      assertTrue(ast.isPresent());
      return ast.get();
    }
    catch (IOException e) {
      throw new RuntimeException(e);
    }

  }

  @BeforeClass
  public static void initLog() {
    Log.enableFailQuick(false);
  }

  @Before
  public void setup() {
    getFindings().clear();
    splCoCoChecker = new SPLCoCoChecker();
  }

  @Test
  public void testVariableDoesNotExist() throws IOException {
    final VariableDoesNotExist variableExists = new VariableDoesNotExist();
    splCoCoChecker.addCoCo((SPLASTCompound_StmtCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableExists);
    splCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);

    checkModelAndAssertWithErrors(
        Paths.get(TEST_MODELS_FOLDER, "varNotDefined.simple"),
        splCoCoChecker,
        VariableDoesNotExist.ERROR_CODE,
        5);
  }


  @Test
  public void testVarDefinedMultipleTimes() throws IOException {
    final VariableDefinedMultipleTimes variableDefinedMultipleTimes = new VariableDefinedMultipleTimes();
    splCoCoChecker.addCoCo(variableDefinedMultipleTimes);

    checkModelAndAssertWithErrors(
        Paths.get(TEST_MODELS_FOLDER, "varDefinedMultipleTimes.simple"),
        splCoCoChecker,
        VariableDefinedMultipleTimes.ERROR_CODE,
        6);
  }

  @Test
  public void testVarHasTypeName() throws IOException {
    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    splCoCoChecker.addCoCo(varHasTypeName);

    checkModelAndAssertWithErrors(
        Paths.get(TEST_MODELS_FOLDER, "varWithTypeName.simple"),
        splCoCoChecker,
        VarHasTypeName.ERROR_CODE,
        2);
  }

  @Test
  public void testVariableIsNotDefinedBeforeUse() throws IOException {
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "varNotDefinedBeforeUse.simple");
    splScopeCreator.runSymbolTableCreator(ast);

    final VariableNotDefinedBeforeUse variableNotDefinedBeforeUse = new VariableNotDefinedBeforeUse();

    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) variableNotDefinedBeforeUse);

    checkModelAndAssertWithErrors(
        Paths.get(TEST_MODELS_FOLDER, "varNotDefinedBeforeUse.simple"),
        splCoCoChecker,
        VariableNotDefinedBeforeUse.ERROR_CODE,
        5);
  }

  @Test
  public void testIllegalVarInFor() throws IOException {
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "illegalVarInFor.simple");
    splScopeCreator.runSymbolTableCreator(ast);

    final IllegalVarInFor illegalVarInFor = new IllegalVarInFor();
    splCoCoChecker.addCoCo(illegalVarInFor);

    checkModelAndAssertWithErrors(
        Paths.get(TEST_MODELS_FOLDER, "illegalVarInFor.simple"),
        splCoCoChecker,
        IllegalVarInFor.ERROR_CODE,
        1);
  }

  @Test
  public void testIllegalExpression() throws IOException {
    final IllegalExpression illegalExpression = new IllegalExpression();
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTELIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTWHILE_StmtCoCo) illegalExpression);

    checkModelAndAssertWithErrors(
        Paths.get(TEST_MODELS_FOLDER, "illegalNumberExpressions.simple"),
        splCoCoChecker,
        IllegalExpression.ERROR_CODE,
        10);
  }

  @Test
  public void testCodeAfterReturn() throws IOException {
    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    splCoCoChecker.addCoCo(codeAfterReturn);

    checkModelAndAssertWithErrors(
        Paths.get(TEST_MODELS_FOLDER, "codeAfterReturn.simple"),
        splCoCoChecker,
        CodeAfterReturn.ERROR_CODE,
        1);
  }

  @Test
  public void testFunctionExists() throws IOException {
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "funNotDefined.simple");
    splScopeCreator.runSymbolTableCreator(ast);

    final FunctionDoesNotExist functionDoesNotExist = new FunctionDoesNotExist();
    splCoCoChecker.addCoCo(functionDoesNotExist);

    splCoCoChecker.checkAll(ast);

    final Integer errorsFound = countErrorsByPrefix(FunctionDoesNotExist.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(3), errorsFound);
  }

  private void checkModelAndAssertNoErrors(
      final Path pathToModel,
      final SPLCoCoChecker splCoCoChecker,
      final String expectedErrorCode) {
    checkModelAndAssertWithErrors(pathToModel, splCoCoChecker, expectedErrorCode, 0);

  }

  private void checkModelAndAssertWithErrors(
      final Path pathToModel,
      final SPLCoCoChecker nestmlCoCoChecker,
      final String expectedErrorCode,
      final Integer expectedNumberCount) {
    final ASTSPLFile ast = getAstRoot(pathToModel.toString());
    splScopeCreator.runSymbolTableCreator(ast);

    nestmlCoCoChecker.checkAll(ast);

    Integer errorsFound = countErrorsByPrefix(expectedErrorCode, getFindings());
    assertEquals(expectedNumberCount, errorsFound);

  }
}
