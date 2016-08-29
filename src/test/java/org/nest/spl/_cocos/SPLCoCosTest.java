/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl._cocos;

import de.se_rwth.commons.logging.Log;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.ode._cocos.ODEASTOdeDeclarationCoCo;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._parser.SPLParser;
import org.nest.spl.symboltable.SPLScopeCreator;
import org.nest.units._visitor.UnitsSIVisitor;

import java.io.IOException;
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

  public static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String TEST_MODELS_FOLDER = "src/test/resources/org/nest/spl/_cocos/";

  final SPLScopeCreator splScopeCreator = new SPLScopeCreator(TEST_MODEL_PATH);

  private SPLCoCoChecker splCoCoChecker;
  /**
   * Parses the model and returns ast.
   * @throws java.io.IOException
   */
  private ASTSPLFile getAstRoot(String modelPath) throws IOException {
    final SPLParser p = new SPLParser();
    final Optional<ASTSPLFile> ast = p.parse(modelPath);
    assertTrue(ast.isPresent());
    return ast.get();
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
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "varNotDefined.simple");
    splScopeCreator.runSymbolTableCreator(ast);

    final VariableDoesNotExist variableExists = new VariableDoesNotExist();
    splCoCoChecker.addCoCo((SPLASTCompound_StmtCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableExists);
    splCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo) variableExists);
    splCoCoChecker.addCoCo((SPLASTReturnStmtCoCo) variableExists);


    splCoCoChecker.checkAll(ast);

    Integer errorsFound = countErrorsByPrefix(
        VariableDoesNotExist.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(5), errorsFound);
  }


  @Test
  public void testVarDefinedMultipleTimes() throws IOException {
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "varDefinedMultipleTimes.simple");

    final VariableDefinedMultipleTimes variableDefinedMultipleTimes = new VariableDefinedMultipleTimes();
    splCoCoChecker.addCoCo(variableDefinedMultipleTimes);

    splCoCoChecker.checkAll(ast);

    Integer errorsFound = countErrorsByPrefix(VariableDefinedMultipleTimes.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testVarHasTypeName() throws IOException {
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "varWithTypeName.simple");
    UnitsSIVisitor.convertSiUnitsToSignature(ast);
    splScopeCreator.runSymbolTableCreator(ast);

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    splCoCoChecker.addCoCo(varHasTypeName);

    splCoCoChecker.checkAll(ast);

    Integer errorsFound = countErrorsByPrefix(VarHasTypeName.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(0), errorsFound); //TODO clear resovling issues in spl modules
  }

  @Test
  public void testVariableIsNotDefinedBeforeUse() throws IOException {
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "varNotDefinedBeforeUse.simple");
    splScopeCreator.runSymbolTableCreator(ast);

    final VariableNotDefinedBeforeUse variableNotDefinedBeforeUse = new VariableNotDefinedBeforeUse();

    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) variableNotDefinedBeforeUse);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) variableNotDefinedBeforeUse);

    splCoCoChecker.checkAll(ast);

    Integer errorsFound = countErrorsByPrefix(VariableNotDefinedBeforeUse.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(5), errorsFound);
  }

  @Test
  public void testIllegalVarInFor() throws IOException {
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "illegalVarInFor.simple");
    splScopeCreator.runSymbolTableCreator(ast);

    final IllegalVarInFor illegalVarInFor = new IllegalVarInFor();
    splCoCoChecker.addCoCo(illegalVarInFor);

    splCoCoChecker.checkAll(ast);

    Integer errorsFound = countErrorsByPrefix(IllegalVarInFor.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testIllegalExpression() throws IOException {
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "illegalNumberExpressions.simple");
    splScopeCreator.runSymbolTableCreator(ast);

    final IllegalExpression illegalExpression = new IllegalExpression();
    splCoCoChecker.addCoCo((SPLASTAssignmentCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTDeclarationCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTELIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTFOR_StmtCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTIF_ClauseCoCo) illegalExpression);
    splCoCoChecker.addCoCo((SPLASTWHILE_StmtCoCo) illegalExpression);
    splCoCoChecker.checkAll(ast);

    final Integer errorsFound = countErrorsByPrefix(IllegalExpression.ERROR_CODE, getFindings());
    getFindings().forEach(f -> System.out.println("DEBUG: " + f.toString()) );
    // TODO must be 14
    assertEquals(Integer.valueOf(10), errorsFound);
  }

  @Test
  public void testCodeAfterReturn() throws IOException {
    final ASTSPLFile ast = getAstRoot(TEST_MODELS_FOLDER + "codeAfterReturn.simple");

    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    splCoCoChecker.addCoCo(codeAfterReturn);

    splCoCoChecker.checkAll(ast);

    final Integer errorsFound = countErrorsByPrefix(CodeAfterReturn.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
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

}
