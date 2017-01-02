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
public class SplCoCosTest {
  private static final String TEST_MODEL_PATH = "src/test/resources/";
  private static final String TEST_VALID_MODELS_FOLDER = "src/test/resources/org/nest/spl/_cocos/valid";
  private static final String TEST_INVALID_MODELS_FOLDER = "src/test/resources/org/nest/spl/_cocos/invalid";
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

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "varNotDefined.simple"),
        splCoCoChecker,
        SplErrorStrings.code(variableExists)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "varNotDefined.simple"),
        splCoCoChecker,
        SplErrorStrings.code(variableExists),
        9);
  }


  @Test
  public void testVarDefinedMultipleTimes() throws IOException {
    final SPLVariableDefinedMultipleTimes SPLVariableDefinedMultipleTimes = new SPLVariableDefinedMultipleTimes();
    splCoCoChecker.addCoCo(SPLVariableDefinedMultipleTimes);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "varDefinedMultipleTimes.simple"),
        splCoCoChecker,
        SplErrorStrings.code(SPLVariableDefinedMultipleTimes)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "varDefinedMultipleTimes.simple"),
        splCoCoChecker,
        SplErrorStrings.code(SPLVariableDefinedMultipleTimes),
        12); // TODO must be 6! Some declrations are checked multiple times
  }

  @Test
  public void testVarHasTypeName() throws IOException {
    final VariableHasTypeName variableHasTypeName = new VariableHasTypeName();
    splCoCoChecker.addCoCo(variableHasTypeName);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "varWithTypeName.simple"),
        splCoCoChecker,
        SplErrorStrings.code(variableHasTypeName)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "varWithTypeName.simple"),
        splCoCoChecker,
        SplErrorStrings.code(variableHasTypeName),
        2);
  }

  @Test
  public void testVariableIsNotDefinedBeforeUse() throws IOException {
    final VariableNotDefinedBeforeUse variableNotDefinedBeforeUse = new VariableNotDefinedBeforeUse();

    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTWHILE_StmtCoCo) variableNotDefinedBeforeUse);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "varNotDefinedBeforeUse.simple"),
        splCoCoChecker,
        SplErrorStrings.code(variableNotDefinedBeforeUse)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "varNotDefinedBeforeUse.simple"),
        splCoCoChecker,
        SplErrorStrings.code(variableNotDefinedBeforeUse),
        10);
  }

  @Test
  public void testIllegalVarInFor() throws IOException {

    final IllegalExpression illegalVarInFor = new IllegalExpression();
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) illegalVarInFor);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "illegalVarInFor.simple"),
        splCoCoChecker,
        SplErrorStrings.code(illegalVarInFor)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "illegalVarInFor.simple"),
        splCoCoChecker,
        SplErrorStrings.code(illegalVarInFor),
        3);
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
        Paths.get(TEST_INVALID_MODELS_FOLDER, "illegalNumberExpressions.simple"),
        splCoCoChecker,
        "SPL_",
        9);
  }

  @Test
  public void testCodeAfterReturn() throws IOException {
    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    splCoCoChecker.addCoCo(codeAfterReturn);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "codeAfterReturn.simple"),
        splCoCoChecker,
        SplErrorStrings.code(codeAfterReturn)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "codeAfterReturn.simple"),
        splCoCoChecker,
        SplErrorStrings.code(codeAfterReturn),
        1);
  }

  @Test
  public void testFunctionExists() throws IOException {
    final FunctionDoesNotExist functionDoesNotExist = new FunctionDoesNotExist();
    splCoCoChecker.addCoCo(functionDoesNotExist);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "funNotDefined.simple"),
        splCoCoChecker,
        SplErrorStrings.code(functionDoesNotExist)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "funNotDefined.simple"),
        splCoCoChecker,
        SplErrorStrings.code(functionDoesNotExist),
        3);
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
