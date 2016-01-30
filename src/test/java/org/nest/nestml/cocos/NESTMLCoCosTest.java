/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.cocos;

import de.se_rwth.commons.Names;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.nest.base.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.*;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl.cocos.VarHasTypeName;
import org.nest.spl.symboltable.SPLCoCosManager;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;

import java.nio.file.Paths;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.getFindings;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.nestml._symboltable.NESTMLRootCreator.getAstRoot;
import static org.nest.utils.LogHelper.countErrorsByPrefix;

/**
 * Test every context context conditions. For each implemented context condition there is one model that contains exactly one tested error.
 *
 * @author plotnikov
 */
public class NESTMLCoCosTest extends ModelTestBase {

  private static final String TEST_MODELS_FOLDER = "src/test/resources/org/nest/nestml/cocos/";

  private NESTMLCoCoChecker nestmlCoCoChecker;

  @Before
  public void setup() {
    nestmlCoCoChecker = new NESTMLCoCoChecker();
  }

  @After
  public void printErrorMessage() {
    getFindings().forEach(e -> System.out.println("Error found: " + e));
  }

  @Test
  public void testResolvingOfPredefinedTypes() {
    // just take an arbitrary nestml model with an import: nestml*
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        Paths.get(TEST_MODELS_FOLDER, "functionWithOutReturn.nestml").toString(),
        TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    PredefinedTypes.getTypes().forEach(type -> {
      Optional<TypeSymbol> predefinedType = scopeCreator.getGlobalScope()
          .resolve(Names.getSimpleName(type.getName()), TypeSymbol.KIND);
      assertTrue("Cannot resolve the predefined type: " + type.getFullName(),
          predefinedType.isPresent());
    });
  }

  @Test
  public void testAliasHasNoSetter() {
    final Optional<ASTNESTMLCompilationUnit> root = getAstRoot(
        TEST_MODELS_FOLDER + "aliasSetter.nestml", TEST_MODEL_PATH);
    assertTrue(root.isPresent());

    scopeCreator.runSymbolTableCreator(root.get());

    final AliasHasNoSetter aliasHasNoSetter = new AliasHasNoSetter();
    nestmlCoCoChecker.addCoCo(aliasHasNoSetter);
    nestmlCoCoChecker.checkAll(root.get());

    Integer errorsFound = countErrorsByPrefix(AliasHasNoSetter.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(2), errorsFound);
  }

  @Test
  public void testAliasHasOneVar() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "aliasMultipleVars.nestml",TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final AliasHasOneVar aliasHasOneVar = new AliasHasOneVar();
    nestmlCoCoChecker.addCoCo(aliasHasOneVar);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(AliasHasOneVar.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testAliasInNonAliasDecl() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "useAliasInNonAliasDecl.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final AliasInNonAliasDecl aliasInNonAliasDecl = new AliasInNonAliasDecl();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) aliasInNonAliasDecl);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) aliasInNonAliasDecl);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(AliasInNonAliasDecl.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testComponentHasNoDynamics() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "componentWithDynamics.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final ComponentHasNoDynamics componentHasNoDynamics = new ComponentHasNoDynamics();
    nestmlCoCoChecker.addCoCo(componentHasNoDynamics);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(ComponentHasNoDynamics.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testComponentNoInput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "componentWithInput.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final ComponentNoInput componentNoInput = new ComponentNoInput();
    nestmlCoCoChecker.addCoCo(componentNoInput);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(ComponentNoInput.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testComponentNoOutput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "componentWithOutput.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final ComponentNoOutput componentNoOutput = new ComponentNoOutput();
    nestmlCoCoChecker.addCoCo(componentNoOutput);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(ComponentNoOutput.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testCorrectReturnValues() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "functionsWithWrongReturns.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    scopeCreator.runSymbolTableCreator(ast.get());

    final CorrectReturnValues correctReturnValues = new CorrectReturnValues();
    nestmlCoCoChecker.addCoCo(correctReturnValues);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(CorrectReturnValues.ERROR_CODE, getFindings());
    getFindings().forEach(System.out::println);
    // TODO check if this does make sense?
    assertEquals(Integer.valueOf(8), errorsFound);
  }

  @Test
  public void testCurrentInputIsNotInhExc() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "inputTypeForCurrent.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final CurrentInputIsNotInhExc currentInputIsNotInhExc = new CurrentInputIsNotInhExc();
    nestmlCoCoChecker.addCoCo(currentInputIsNotInhExc);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(CurrentInputIsNotInhExc.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(3), errorsFound);
  }

  @Test
  public void testFunctionHasReturnStatement() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "functionWithOutReturn.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final FunctionHasReturnStatement functionHasReturnStatement = new FunctionHasReturnStatement();
    nestmlCoCoChecker.addCoCo(functionHasReturnStatement);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(FunctionHasReturnStatement.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testInvalidTypesInDeclaration() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "invalidTypeInDecl.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final InvalidTypesInDeclaration invalidTypesInDeclaration = new InvalidTypesInDeclaration();

    nestmlCoCoChecker.addCoCo((NESTMLASTUSE_StmtCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((SPLASTDeclarationCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(InvalidTypesInDeclaration.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(6), errorsFound);
  }

  @Test
  public void testMemberVariableDefinedMultipleTimes() {

    final MemberVariableDefinedMultipleTimes memberVariableDefinedMultipleTimes = new MemberVariableDefinedMultipleTimes();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) memberVariableDefinedMultipleTimes);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) memberVariableDefinedMultipleTimes);

    String pathToValidModel = TEST_MODELS_FOLDER + "multiplyDefinedVars/validModel.nestml";
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        "NESTML_");

    String pathToInvalidModel = TEST_MODELS_FOLDER + "multiplyDefinedVars/varDefinedMultipleTimes.nestml";
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        "NESTML_",
        2);



    Integer errorsFound = countErrorsByPrefix(MemberVariableDefinedMultipleTimes.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(2), errorsFound);
  }

  @Test
  public void testMemberVariablesInitialisedInCorrectOrder() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "memberVarDefinedInWrongOrder.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());
    final MemberVariablesInitialisedInCorrectOrder memberVariablesInitialisedInCorrectOrder
            = new MemberVariablesInitialisedInCorrectOrder();

    nestmlCoCoChecker.addCoCo(memberVariablesInitialisedInCorrectOrder);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(MemberVariablesInitialisedInCorrectOrder.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(3), errorsFound);
  }

  @Test
  public void testMultipleFunctionsDeclarations() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "multipleFunctionDeclarations.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final MultipleFunctionDeclarations multipleFunctionDeclarations
            = new MultipleFunctionDeclarations();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) multipleFunctionDeclarations);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) multipleFunctionDeclarations);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(MultipleFunctionDeclarations.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(6), errorsFound);
  }

  @Test
  public void testMultipleInhExcInput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "multipleInhExcInInput.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final MultipleInhExcInput multipleInhExcInput = new MultipleInhExcInput();
    nestmlCoCoChecker.addCoCo(multipleInhExcInput);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(MultipleInhExcInput.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(4), errorsFound);
  }

  @Test
  public void testMultipleOutputs() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "multipleOutputs.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final MultipleOutputs multipleOutputs = new MultipleOutputs();
    nestmlCoCoChecker.addCoCo(multipleOutputs);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(MultipleOutputs.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testFunctionNameChecker() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "nestFunName.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final NESTFunctionNameChecker functionNameChecker = new NESTFunctionNameChecker();
    nestmlCoCoChecker.addCoCo(functionNameChecker);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(NESTFunctionNameChecker.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(8), errorsFound);
  }

  @Test
  public void testNESTGetterSetterFunctionNames() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "getterSetter.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final GetterSetterFunctionNames getterSetterFunctionNames = new GetterSetterFunctionNames();
    nestmlCoCoChecker.addCoCo(getterSetterFunctionNames);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(GetterSetterFunctionNames.ERROR_CODE,
        getFindings());
    assertEquals(Integer.valueOf(4), errorsFound);
  }

  @Test
  public void testNeuronNeedsDynamicsWithNoDynamics() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "emptyNeuron.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final NeuronNeedsDynamics neuronNeedsDynamics = new NeuronNeedsDynamics();
    nestmlCoCoChecker.addCoCo(neuronNeedsDynamics);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(NeuronNeedsDynamics.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testNeuronNeedsDynamicsWithMultipleDynamics() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "multipleDynamicsNeuron.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final NeuronNeedsDynamics neuronNeedsDynamics = new NeuronNeedsDynamics();
    nestmlCoCoChecker.addCoCo(neuronNeedsDynamics);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(NeuronNeedsDynamics.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testNeuronWithoutInput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "emptyNeuron.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final NeuronWithoutInput neuronNeedsDynamics = new NeuronWithoutInput();
    nestmlCoCoChecker.addCoCo(neuronNeedsDynamics);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(NeuronWithoutInput.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testNeuronWithoutOutput() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "emptyNeuron.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());

    final NeuronWithoutOutput neuronWithoutOutput = new NeuronWithoutOutput();
    nestmlCoCoChecker.addCoCo(neuronWithoutOutput);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(NeuronWithoutOutput.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testTypesDeclaredMultipleTimes() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "multipleTypesDeclared.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final TypeIsDeclaredMultipleTimes typeIsDeclaredMultipleTimes = new TypeIsDeclaredMultipleTimes();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) typeIsDeclaredMultipleTimes);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) typeIsDeclaredMultipleTimes);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(TypeIsDeclaredMultipleTimes.ERROR_CODE,
        getFindings());
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
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "reassignBuffer.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final BufferNotAssignable bufferNotAssignable = new BufferNotAssignable();
    // TODO: rewrite: Must be possible: wait for the visitor that visits super types
    nestmlCoCoChecker.addCoCo(bufferNotAssignable);
    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(BufferNotAssignable.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(1), errorsFound);
  }

  @Test
  public void testVarHasTypeName() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        TEST_MODELS_FOLDER + "varWithTypeName.nestml", TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    nestmlCoCoChecker.addCoCo(varHasTypeName);

    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(VarHasTypeName.ERROR_CODE, getFindings());
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
    final SPLCoCosManager splCoCosManager  = new SPLCoCosManager();
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
        = new BooleanInvariantExpressions();
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
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToModel, TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    nestmlCoCoChecker.checkAll(ast.get());

    int errorsFound = countErrorsByPrefix(expectedErrorCode, getFindings());
    assertEquals(0, errorsFound);

  }

  private void checkModelAndAssertWithErrors(
      final String pathToModel,
      final NESTMLCoCoChecker nestmlCoCoChecker,
      final String expectedErrorCode,
      final Integer expectedNumberCount) {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToModel, TEST_MODEL_PATH);
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(expectedErrorCode, getFindings());
    assertEquals(expectedNumberCount, errorsFound);

  }

}
