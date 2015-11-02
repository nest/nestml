/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.cocos;

import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.junit.*;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._cocos.*;
import org.nest.spl._parser.SPLFileMCParser;
import org.nest.spl._parser.SPLParserFactory;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.IOException;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.getFindings;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.utils.LogHelper.countErrorsByPrefix;

/**
 * Test every context context conditions. For each implemented context condition there is one model that contains exactly one tested error.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class SPLCoCosTest {

  public static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String TEST_MODELS_FOLDER = "src/test/resources/org/nest/spl/cocos/";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  final SPLScopeCreator splScopeCreator = new SPLScopeCreator(TEST_MODEL_PATH, typesFactory);

  private SPLCoCoChecker splCoCoChecker;
  /**
   * Parses the model and returns ast.
   * @throws java.io.IOException
   */
  private Optional<ASTSPLFile> getAstRoot(String modelPath) throws IOException {
    SPLFileMCParser p = SPLParserFactory.createSPLFileMCParser();
    Optional<ASTSPLFile> ast = p.parse(modelPath);
    assertTrue(ast.isPresent());
    return ast;
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

  @After
  public void printErrorMessage() {
    getFindings().forEach(e -> System.out.println("Error found: " + e));
  }

  @Test
  public void testVariableDoesNotExist() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "varNotDefined.simple");
    Assert.assertTrue(ast.isPresent());
    splScopeCreator.runSymbolTableCreator(ast.get());

    final VariableDoesNotExist variableExists = new VariableDoesNotExist();
    splCoCoChecker.addCoCo((SPLASTCompound_StmtCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTFunctionCallCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);

    splCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(VariableDoesNotExist.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(2), errorsFound);
  }

  @Test
  public void testVarNotDefinedInTest() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "varNotDefinedInTest.simple");
    Assert.assertTrue(ast.isPresent());
    splScopeCreator.runSymbolTableCreator(ast.get());

    final VariableDoesNotExist variableExists = new VariableDoesNotExist();
    splCoCoChecker.addCoCo((SPLASTCompound_StmtCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTFunctionCallCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);

    splCoCoChecker.checkAll(ast.get());

    final Integer errorsFound = countErrorsByPrefix(VariableDoesNotExist.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(2), errorsFound);
  }

  @Test
  public void testVarDefinedMultipleTimes() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "varDefinedMultipleTimes.simple");
    Assert.assertTrue(ast.isPresent());

    final VariableDefinedMultipleTimes variableDefinedMultipleTimes = new VariableDefinedMultipleTimes();
    splCoCoChecker.addCoCo(variableDefinedMultipleTimes);

    splCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(VariableDefinedMultipleTimes.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testVarHasTypeName() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "varWithTypeName.simple");
    Assert.assertTrue(ast.isPresent());
    splScopeCreator.runSymbolTableCreator(ast.get());

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    splCoCoChecker.addCoCo(varHasTypeName);

    splCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(VarHasTypeName.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testVariableIsNotDefinedBeforeUse() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "varNotDefinedBeforeUse.simple");
    Assert.assertTrue(ast.isPresent());
    splScopeCreator.runSymbolTableCreator(ast.get());

    final VariableNotDefinedBeforeUse variableNotDefinedBeforeUse = new VariableNotDefinedBeforeUse();

    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) variableNotDefinedBeforeUse);

    splCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(VariableNotDefinedBeforeUse.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(5), errorsFound);
  }

  @Test
  public void testIllegalVarInFor() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "illegalVarInFor.simple");
    Assert.assertTrue(ast.isPresent());
    splScopeCreator.runSymbolTableCreator(ast.get());

    final IllegalVarInFor illegalVarInFor = new IllegalVarInFor(splScopeCreator.getTypesFactory());
    splCoCoChecker.addCoCo(illegalVarInFor);

    splCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(IllegalVarInFor.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testIllegalExpression() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "illegalNumberExpressions.simple");
    Assert.assertTrue(ast.isPresent());
    splScopeCreator.runSymbolTableCreator(ast.get());

    final IllegalExpression illegalExpression = new IllegalExpression(splScopeCreator.getTypesFactory());
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTELIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTWHILE_StmtCoCo) illegalExpression);
    splCoCoChecker.checkAll(ast.get());

    final Integer errorsFound = countErrorsByPrefix(IllegalExpression.ERROR_CODE, getFindings());
    getFindings().forEach(f -> System.out.println("DEBUG: " + f.toString()) );
    // TODO must be 14
    assertEquals(Integer.valueOf(10), errorsFound);
  }

  @Test
  public void testCodeAfterReturn() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "codeAfterReturn.simple");
    Assert.assertTrue(ast.isPresent());

    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    splCoCoChecker.addCoCo(codeAfterReturn);

    splCoCoChecker.checkAll(ast.get());

    final Integer errorsFound = countErrorsByPrefix(CodeAfterReturn.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testFunctionExists() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "funNotDefined.simple");
    Assert.assertTrue(ast.isPresent());
    splScopeCreator.runSymbolTableCreator(ast.get());

    final FunctionDoesntExist functionDoesntExist = new FunctionDoesntExist(
        splScopeCreator.getTypesFactory());
    splCoCoChecker.addCoCo(functionDoesntExist);

    splCoCoChecker.checkAll(ast.get());

    final Integer errorsFound = countErrorsByPrefix(FunctionDoesntExist.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(3), errorsFound);
  }

  // TODO
  //@Test
  public void testCheckMultipleSignsBeforeFactor() throws IOException {
    final Optional<ASTSPLFile> ast = getAstRoot(TEST_MODELS_FOLDER + "multipleSigns.simple");
    Assert.assertTrue(ast.isPresent());

    final CheckMultipleSignsBeforeFactor checkMultipleSignsBeforeFactor = new CheckMultipleSignsBeforeFactor();
    splCoCoChecker.addCoCo((SPLASTBlockCoCo) checkMultipleSignsBeforeFactor);
    splCoCoChecker.addCoCo((SPLASTExprCoCo) checkMultipleSignsBeforeFactor);

    splCoCoChecker.checkAll(ast.get());

    final Integer errorsFound = countErrorsByPrefix(
        CheckMultipleSignsBeforeFactor.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(4), errorsFound);
  }

}
