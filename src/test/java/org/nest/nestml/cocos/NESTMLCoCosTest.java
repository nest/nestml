/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import de.monticore.cocos.CoCoLog;
import de.se_rwth.commons.Names;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.nestml.cocos.spl.BufferNotAssignable;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.*;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.spl.cocos.VarHasTypeName;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl.symboltable.SPLCoCosManager;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.utils.LogHelper;

import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.nestml._symboltable.NESTMLRootCreator.getAstRoot;
import static org.nest.utils.LogHelper.countOccurrences;

/**
 * Test every context context conditions. For each implemented context condition there is one model that contains exactly one tested error.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLCoCosTest {

  public static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final String TEST_MODELS_FOLDER = "src/test/resources/org/nest/nestml/cocos/";

  private NESTMLCoCoChecker nestmlCoCoChecker;

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  private NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH, typesFactory);

  @BeforeClass
  public static void initLog() {
    CoCoLog.setDelegateToLog(false);
  }

  @Before
  public void setup() {
    CoCoLog.getFindings().clear();
    nestmlCoCoChecker = new NESTMLCoCoChecker();

  }

  @After
  public void printErrorMessage() {
    CoCoLog.getFindings().forEach(e -> System.out.println("Error found: " + e));
  }

  @Test
  public void testResolvingOfPredefinedTypes() {
    // just take an arbitrary nestml model with an import: nestml*
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "functionWithOutReturn.nestml");
    assertTrue(ast.isPresent());

    scopeCreator.getTypesFactory().getTypes().forEach(type -> {
      Optional<NESTMLTypeSymbol> predefinedType = scopeCreator.getGlobalScope()
          .resolve(Names.getSimpleName(type.getName()), NESTMLTypeSymbol.KIND);
      assertTrue("Cannot resolve the predefined type: " + type.getFullName(),
          predefinedType.isPresent());
    });
  }

  @Test
  public void testAliasHasNoSetter() {
    final Optional<ASTNESTMLCompilationUnit> root = getAstRoot(TEST_MODELS_FOLDER + "aliasSetter.nestml");
    assertTrue(root.isPresent());

    scopeCreator.runSymbolTableCreator(root.get());

    final AliasHasNoSetter aliasHasNoSetter = new AliasHasNoSetter(root.get());
    nestmlCoCoChecker.addCoCo(aliasHasNoSetter);
    nestmlCoCoChecker.checkAll(root.get());

    Integer errorsFound = countOccurrences(AliasHasNoSetter.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(2), errorsFound);
  }

  @Test
  public void testAliasHasOneVar() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "aliasMultipleVars.nestml");
    assertTrue(ast.isPresent());

    final AliasHasOneVar aliasHasOneVar = new AliasHasOneVar();
    nestmlCoCoChecker.addCoCo(aliasHasOneVar);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(AliasHasOneVar.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testAliasInNonAliasDecl() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "useAliasInNonAliasDecl.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final AliasInNonAliasDecl aliasInNonAliasDecl = new AliasInNonAliasDecl();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) aliasInNonAliasDecl);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) aliasInNonAliasDecl);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(AliasInNonAliasDecl.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testComponentHasNoDynamics() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "componentWithDynamics.nestml");
    assertTrue(ast.isPresent());

    final ComponentHasNoDynamics componentHasNoDynamics = new ComponentHasNoDynamics();
    nestmlCoCoChecker.addCoCo(componentHasNoDynamics);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(ComponentHasNoDynamics.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testComponentNoInput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "componentWithInput.nestml");
    assertTrue(ast.isPresent());

    final ComponentNoInput componentNoInput = new ComponentNoInput();
    nestmlCoCoChecker.addCoCo(componentNoInput);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(ComponentNoInput.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testComponentNoOutput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "componentWithOutput.nestml");
    assertTrue(ast.isPresent());

    final ComponentNoOutput componentNoOutput = new ComponentNoOutput();
    nestmlCoCoChecker.addCoCo(componentNoOutput);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(ComponentNoOutput.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testCorrectReturnValues() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER
        + "functionsWithWrongReturns.nestml");
    assertTrue(ast.isPresent());

    scopeCreator.runSymbolTableCreator(ast.get());

    final CorrectReturnValues correctReturnValues
        = new CorrectReturnValues(scopeCreator.getTypesFactory());
    nestmlCoCoChecker.addCoCo(correctReturnValues);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(CorrectReturnValues.ERROR_CODE, CoCoLog.getFindings());
    CoCoLog.getFindings().forEach(f -> System.out.println(f.getCode() + ":" + f.getMsg()));
    // TODO check if this does make sense?
    assertEquals(Integer.valueOf(10), errorsFound);
  }

  @Test
  public void testCurrentInputIsNotInhExc() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "inputTypeForCurrent.nestml");
    assertTrue(ast.isPresent());

    final CurrentInputIsNotInhExc currentInputIsNotInhExc = new CurrentInputIsNotInhExc();
    nestmlCoCoChecker.addCoCo(currentInputIsNotInhExc);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(CurrentInputIsNotInhExc.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(3), errorsFound);
  }

  @Test
  public void testDynamicsTimeStepParameter() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "timestepDynamics.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final DynamicsTimeStepParameter dynamicsTimeStepParameter = new DynamicsTimeStepParameter();
    nestmlCoCoChecker.addCoCo(dynamicsTimeStepParameter);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(DynamicsTimeStepParameter.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(3), errorsFound);
  }

  @Test
  public void testFunctionHasReturnStatement() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "functionWithOutReturn.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final FunctionHasReturnStatement functionHasReturnStatement = new FunctionHasReturnStatement(
        scopeCreator.getTypesFactory());
    nestmlCoCoChecker.addCoCo(functionHasReturnStatement);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(FunctionHasReturnStatement.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testInvalidTypesInDeclaration() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "invalidTypeInDecl.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final InvalidTypesInDeclaration invalidTypesInDeclaration = new InvalidTypesInDeclaration();

    nestmlCoCoChecker.addCoCo((NESTMLASTUSE_StmtCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((SPLASTDeclarationCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(InvalidTypesInDeclaration.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(6), errorsFound);
  }

  @Test
  public void testMemberVariableDefinedMultipleTimes() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "varDefinedMultipleTimes.nestml");
    assertTrue(ast.isPresent());

    final MemberVariableDefinedMultipleTimes memberVariableDefinedMultipleTimes = new MemberVariableDefinedMultipleTimes();

    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) memberVariableDefinedMultipleTimes);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) memberVariableDefinedMultipleTimes);

    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(MemberVariableDefinedMultipleTimes.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testMemberVariablesInitialisedInCorrectOrder() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "memberVarDefinedInWrongOrder.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());
    final MemberVariablesInitialisedInCorrectOrder memberVariablesInitialisedInCorrectOrder
            = new MemberVariablesInitialisedInCorrectOrder();

    nestmlCoCoChecker.addCoCo(memberVariablesInitialisedInCorrectOrder);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(MemberVariablesInitialisedInCorrectOrder.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(3), errorsFound);
  }

  @Test
  public void testMultipleFunctionsDeclarations() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "multipleFunctionDeclarations.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final MultipleFunctionDeclarations multipleFunctionDeclarations
            = new MultipleFunctionDeclarations();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) multipleFunctionDeclarations);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) multipleFunctionDeclarations);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(MultipleFunctionDeclarations.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(6), errorsFound);
  }

  @Test
  public void testMultipleInhExcInput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "multipleInhExcInInput.nestml");
    assertTrue(ast.isPresent());

    final MultipleInhExcInput multipleInhExcInput = new MultipleInhExcInput();
    nestmlCoCoChecker.addCoCo(multipleInhExcInput);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(MultipleInhExcInput.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(4), errorsFound);
  }

  @Test
  public void testMultipleOutputs() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "multipleOutputs.nestml");
    assertTrue(ast.isPresent());

    final MultipleOutputs multipleOutputs = new MultipleOutputs();
    nestmlCoCoChecker.addCoCo(multipleOutputs);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(MultipleOutputs.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testFunctionNameChecker() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "nestFunName.nestml");
    assertTrue(ast.isPresent());

    final NESTFunctionNameChecker functionNameChecker = new NESTFunctionNameChecker();
    nestmlCoCoChecker.addCoCo(functionNameChecker);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(NESTFunctionNameChecker.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(9), errorsFound);
  }

  @Test
  public void testNESTGetterSetterFunctionNames() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "getterSetter.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final NESTGetterSetterFunctionNames nestGetterSetterFunctionNames = new NESTGetterSetterFunctionNames();
    nestmlCoCoChecker.addCoCo(nestGetterSetterFunctionNames);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(NESTGetterSetterFunctionNames.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(4), errorsFound);
  }

  @Test
  public void testNeuronNeedsDynamicsWithNoDynamics() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "emptyNeuron.nestml");
    assertTrue(ast.isPresent());

    final NeuronNeedsDynamics neuronNeedsDynamics = new NeuronNeedsDynamics();
    nestmlCoCoChecker.addCoCo(neuronNeedsDynamics);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(NeuronNeedsDynamics.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testNeuronNeedsDynamicsWithMultipleDynamics() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "multipleDynamicsNeuron.nestml");
    assertTrue(ast.isPresent());

    final NeuronNeedsDynamics neuronNeedsDynamics = new NeuronNeedsDynamics();
    nestmlCoCoChecker.addCoCo(neuronNeedsDynamics);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(NeuronNeedsDynamics.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testNeuronWithoutInput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "emptyNeuron.nestml");
    assertTrue(ast.isPresent());

    final NeuronWithoutInput neuronNeedsDynamics = new NeuronWithoutInput();
    nestmlCoCoChecker.addCoCo(neuronNeedsDynamics);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(NeuronWithoutInput.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testNeuronWithoutOutput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "emptyNeuron.nestml");
    assertTrue(ast.isPresent());

    final NeuronWithoutOutput neuronWithoutOutput = new NeuronWithoutOutput();
    nestmlCoCoChecker.addCoCo(neuronWithoutOutput);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(NeuronWithoutOutput.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testTypesDeclaredMultipleTimes() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "multipleTypesDeclared.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final TypeIsDeclaredMultipleTimes typeIsDeclaredMultipleTimes = new TypeIsDeclaredMultipleTimes();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) typeIsDeclaredMultipleTimes);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) typeIsDeclaredMultipleTimes);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(TypeIsDeclaredMultipleTimes.ERROR_CODE,
        CoCoLog.getFindings());
    assertEquals(Integer.valueOf(2), errorsFound);
  }

  @Test
  public void testUsesOnlyComponents() {

    final UsesOnlyComponents usesOnlyComponents = new UsesOnlyComponents();
    nestmlCoCoChecker.addCoCo(usesOnlyComponents);

    String pathToValidModel = TEST_MODELS_FOLDER + "useComponents/validUsage.nestml";
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        "NESTML_");

    String pathToInvalidModel = TEST_MODELS_FOLDER + "useComponents/invalidUsage.nestml";
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        "NESTML_",
        2);
  }

  @Test
  public void testBufferNotAssignable() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "reassignBuffer.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final BufferNotAssignable bufferNotAssignable = new BufferNotAssignable();
    // TODO: rewrite: Must be possible: wait for the visitor that visits super types
    nestmlCoCoChecker.addCoCo(bufferNotAssignable);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(BufferNotAssignable.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testSplCocosInNestml() {
    final NESTMLCoCoChecker nestmlCoCoCheckerWithSPLCocos = new NESTMLCoCoChecker();
    final SPLCoCosManager splCoCosManager  = new SPLCoCosManager(scopeCreator.getTypesFactory());
    splCoCosManager.addSPLCocosToNESTMLChecker(nestmlCoCoCheckerWithSPLCocos);

    String pathToValidModel = TEST_MODELS_FOLDER + "splInFunctions/validMethod.nestml";
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoCheckerWithSPLCocos,
        "SPL_");

    String pathToInvalidModel = TEST_MODELS_FOLDER + "splInFunctions/invalidMethod.nestml";
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoCheckerWithSPLCocos,
        "SPL_",
        18);
  }

  @Test
  public void testVarHasTypeName() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(TEST_MODELS_FOLDER + "varWithTypeName.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    nestmlCoCoChecker.addCoCo(varHasTypeName);

    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countOccurrences(VarHasTypeName.ERROR_CODE, CoCoLog.getFindings());
    assertEquals(Integer.valueOf(2), errorsFound);
  }

  @Test
  public void testUsageIncorrectOrder() {
    String pathToValidModel = TEST_MODELS_FOLDER + "undefinedVariables/validModelUndefinedValues.nestml";
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        MemberVariablesInitialisedInCorrectOrder.ERROR_CODE);

    final MemberVariablesInitialisedInCorrectOrder memberVariablesInitialisedInCorrectOrder
        = new MemberVariablesInitialisedInCorrectOrder();
    nestmlCoCoChecker.addCoCo(memberVariablesInitialisedInCorrectOrder);

    String pathToInvalidModel = TEST_MODELS_FOLDER + "undefinedVariables/invalidModelUndefinedValues.nestml";
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        MemberVariablesInitialisedInCorrectOrder.ERROR_CODE,
        3);

  }

  @Test
  public void testSplInFunctions() {
    final NESTMLCoCoChecker nestmlCoCoCheckerWithSPLCocos = new NESTMLCoCoChecker();
    final SPLCoCosManager splCoCosManager  = new SPLCoCosManager(scopeCreator.getTypesFactory());
    splCoCosManager.addSPLCocosToNESTMLChecker(nestmlCoCoCheckerWithSPLCocos);

    String pathToValidModel = TEST_MODELS_FOLDER + "splInFunctions/validMethod.nestml";
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoCheckerWithSPLCocos,
        "SPL_");

    String pathToInvalidModel = TEST_MODELS_FOLDER + "splInFunctions/invalidMethod.nestml";
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoCheckerWithSPLCocos,
        "SPL_",
        18);

  }

  @Test
  public void testInvalidInvariantExpressionType() {
    final BooleanInvariantExpressions booleanInvariantExpressions
        = new BooleanInvariantExpressions(scopeCreator.getTypesFactory());
    nestmlCoCoChecker.addCoCo(booleanInvariantExpressions);

    String pathToValidModel = TEST_MODELS_FOLDER + "invariants/validInvariantType.nestml";
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        BooleanInvariantExpressions.ERROR_CODE);

    String pathToInvalidModel = TEST_MODELS_FOLDER + "invariants/invalidInvariantType.nestml";
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        BooleanInvariantExpressions.ERROR_CODE,
        2);

  }

  private void checkModelAndAssertNoErrors(
      final String pathToModel,
      final NESTMLCoCoChecker nestmlCoCoChecker,
      final String expectedErrorCode) {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToModel);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    nestmlCoCoChecker.checkAll(ast.get());

    int errorsFound = LogHelper.countOccurrencesByPrefix(expectedErrorCode, CoCoLog.getFindings());
    assertEquals(0, errorsFound);

  }

  private void checkModelAndAssertWithErrors(
      final String pathToModel,
      final NESTMLCoCoChecker nestmlCoCoChecker,
      final String expectedErrorCode,
      final Integer expectedNumberCount) {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToModel);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = LogHelper.countOccurrencesByPrefix(expectedErrorCode,
        CoCoLog.getFindings());
    assertEquals(expectedNumberCount, errorsFound);

  }

}
