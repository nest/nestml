/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.se_rwth.commons.Names;
import de.se_rwth.commons.logging.Log;
import org.junit.Before;
import org.junit.Test;
import org.nest.commons._cocos.CommonsASTFunctionCallCoCo;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.ode._cocos.ODEASTOdeDeclarationCoCo;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl._cocos.SplErrorStrings;
import org.nest.spl._cocos.VarHasTypeName;
import org.nest.spl.symboltable.SPLCoCosManager;
import org.nest.symboltable.predefined.PredefinedTypes;
import org.nest.symboltable.symbols.TypeSymbol;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.getFindings;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.nest.nestml._symboltable.NESTMLRootCreator.getAstRoot;
import static org.nest.utils.LogHelper.countErrorsByPrefix;
import static org.nest.utils.LogHelper.countWarningsByPrefix;

/**
 * Test every context context conditions. For each implemented context condition there is one model that contains exactly one tested error.
 *
 * @author plotnikov
 */
public class NestmlCoCosTest {

  @Before
  public void clearLog() {
    Log.enableFailQuick(false);
    Log.getFindings().clear();
  }

  private static final String TEST_MODELS_FOLDER = "src/test/resources/org/nest/nestml/_cocos/";
  private static final String TEST_VALID_MODELS_FOLDER = "src/test/resources/org/nest/nestml/_cocos/valid";
  private static final String TEST_INVALID_MODELS_FOLDER = "src/test/resources/org/nest/nestml/_cocos/invalid";
  protected final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(Paths.get("src/test/resources"));

  private NESTMLCoCoChecker nestmlCoCoChecker;

  @Before
  public void setup() {
    nestmlCoCoChecker = new NESTMLCoCoChecker();
  }

  @Test
  public void testResolvingOfPredefinedTypes() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        Paths.get(TEST_MODELS_FOLDER, "resolvePredefinedTypes.nestml").toString(),
        Paths.get(TEST_MODELS_FOLDER));
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    PredefinedTypes.getTypes().forEach(type -> {
      Optional<TypeSymbol> predefinedType = scopeCreator.getGlobalScope()
          .resolve(Names.getSimpleName(type.getName()), TypeSymbol.KIND);
      assertTrue("Cannot resolve the predefined type: " + type.getFullName(),
          predefinedType.isPresent());
    });
  }

  @Test
  public void testAliasHasNoSetter() {
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        TEST_MODELS_FOLDER + "aliasHasNoSetter/valid.nestml", Paths.get(TEST_MODELS_FOLDER));
    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());
    final AliasHasNoSetter aliasHasNoSetter = new AliasHasNoSetter();

    nestmlCoCoChecker.addCoCo(aliasHasNoSetter);
    nestmlCoCoChecker.checkAll(validRoot.get());

    Integer errorsFound = countWarningsByPrefix(AliasHasNoSetter.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(0), errorsFound);

    final Optional<ASTNESTMLCompilationUnit> invalidRoot = getAstRoot(
        TEST_MODELS_FOLDER + "aliasHasNoSetter/invalid.nestml", Paths.get(TEST_MODELS_FOLDER));
        assertTrue(invalidRoot.isPresent());
    scopeCreator.runSymbolTableCreator(invalidRoot.get());

    nestmlCoCoChecker.checkAll(invalidRoot.get());
    // TODO: Extend Log, make the information about infos also persistable

  }

  @Test
  public void testAliasHasOneVar() {
    final AliasHasOneVar aliasHasOneVar = new AliasHasOneVar();
    nestmlCoCoChecker.addCoCo(aliasHasOneVar);

    final Path pathToValidModel = Paths.get(TEST_VALID_MODELS_FOLDER, "aliasHasOneVar.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(aliasHasOneVar));

    final Path pathToInvalidModel = Paths.get(TEST_INVALID_MODELS_FOLDER, "aliasHasOneVar.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(aliasHasOneVar),
        1);
  }

  @Test
  public void testAliasInNonAliasDecl() {
    final VectorVariableInNonVectorDeclaration vectorVariableInNonVectorDeclaration = new VectorVariableInNonVectorDeclaration();
    nestmlCoCoChecker.addCoCo(vectorVariableInNonVectorDeclaration);

    final Path pathToValidModel = Paths.get(TEST_VALID_MODELS_FOLDER, "vectorVariableInNonVectorDeclaration.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(vectorVariableInNonVectorDeclaration));

    final Path pathToInvalidModel = Paths.get(TEST_INVALID_MODELS_FOLDER, "vectorVariableInNonVectorDeclaration.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(vectorVariableInNonVectorDeclaration),
        1);
  }

  @Test
  public void testComponentHasNoDynamics() {
    final ComponentHasNoDynamics componentHasNoDynamics = new ComponentHasNoDynamics();
    nestmlCoCoChecker.addCoCo(componentHasNoDynamics);

    final Path pathToValidModel = Paths.get(TEST_VALID_MODELS_FOLDER, "componentHasNoDynamics.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(componentHasNoDynamics));

    final Path pathToInvalidModel = Paths.get(TEST_INVALID_MODELS_FOLDER, "componentHasNoDynamics.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(componentHasNoDynamics),
        1);
  }

  @Test
  public void testComponentWithoutInput() {
    final ComponentWithoutInput componentWithoutInput = new ComponentWithoutInput();
    nestmlCoCoChecker.addCoCo(componentWithoutInput);

    final Path pathToValidModel = Paths.get(TEST_VALID_MODELS_FOLDER, "componentWithoutInput.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(componentWithoutInput));

    final Path pathToInvalidModel = Paths.get(TEST_INVALID_MODELS_FOLDER, "componentWithoutInput.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(componentWithoutInput),
        1);
  }

  @Test
  public void testComponentWithoutOutput() {
    final ComponentWithoutOutput componentWithoutOutput = new ComponentWithoutOutput();
    nestmlCoCoChecker.addCoCo(componentWithoutOutput);

    final Path pathToValidModel = Paths.get(TEST_VALID_MODELS_FOLDER, "componentWithoutOutput.nestml") ;
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(componentWithoutOutput));

    final Path pathToInvalidModel = Paths.get(TEST_INVALID_MODELS_FOLDER, "componentWithoutOutput.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(componentWithoutOutput),
        1);
  }

  @Test
  public void testCorrectReturnValues() {
    final CorrectReturnValues correctReturnValues = new CorrectReturnValues();
    nestmlCoCoChecker.addCoCo(correctReturnValues);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "correctReturnValues/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        CorrectReturnValues.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "correctReturnValues/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        CorrectReturnValues.ERROR_CODE,
        8);
  }

  @Test
  public void testCurrentInputIsNotInhExc() {
    final CurrentInputIsNotInhExc currentInputIsNotInhExc = new CurrentInputIsNotInhExc();
    nestmlCoCoChecker.addCoCo(currentInputIsNotInhExc);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "currentInputIsNotInhExc/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        CurrentInputIsNotInhExc.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "currentInputIsNotInhExc/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        CurrentInputIsNotInhExc.ERROR_CODE,
        3);
  }

  @Test
  public void testFunctionHasReturnStatement() {
    final FunctionHasReturnStatement functionHasReturnStatement = new FunctionHasReturnStatement();
    nestmlCoCoChecker.addCoCo(functionHasReturnStatement);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "functionHasReturnStatement/valid.nestml") ;
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        FunctionHasReturnStatement.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "functionHasReturnStatement/invalid.nestml") ;
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        FunctionHasReturnStatement.ERROR_CODE,
        1);
  }

  @Test
  public void testInvalidTypesInDeclaration() {
    final InvalidTypesInDeclaration invalidTypesInDeclaration = new InvalidTypesInDeclaration();
    nestmlCoCoChecker.addCoCo((NESTMLASTUSE_StmtCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((SPLASTDeclarationCoCo) invalidTypesInDeclaration);

    // TODO referencing of the neurons must be enabled
    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "invalidTypesInDeclaration/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        InvalidTypesInDeclaration.ERROR_CODE);
    //TODO: Rewrite or drop invalid model
    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalidTypesInDeclaration/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        InvalidTypesInDeclaration.ERROR_CODE,
        0);
  }

  @Test
  public void testMemberVariableDefinedMultipleTimes() {

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/memberVariableDefinedMultipleTimes.nestml") ;
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        MemberVariableDefinedMultipleTimes.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/memberVariableDefinedMultipleTimes.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        MemberVariableDefinedMultipleTimes.ERROR_CODE,
        10); // some of the errors is reported twice
  }

  @Test
  public void testMemberVariablesInitialisedInCorrectOrder() {
    final MemberVariablesInitialisedInCorrectOrder memberVariablesInitialisedInCorrectOrder
            = new MemberVariablesInitialisedInCorrectOrder();

    nestmlCoCoChecker.addCoCo(memberVariablesInitialisedInCorrectOrder);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "memberVariablesInitialisedInCorrectOrder/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        MemberVariablesInitialisedInCorrectOrder.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "memberVariablesInitialisedInCorrectOrder/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        MemberVariablesInitialisedInCorrectOrder.ERROR_CODE,
        4);
  }

  @Test
  public void testMultipleFunctionsDeclarations() {
    final MultipleFunctionDeclarations multipleFunctionDeclarations
            = new MultipleFunctionDeclarations();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) multipleFunctionDeclarations);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) multipleFunctionDeclarations);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "multipleFunctionDeclarations/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        MultipleFunctionDeclarations.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "multipleFunctionDeclarations/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        MultipleFunctionDeclarations.ERROR_CODE,
        6);
  }

  @Test
  public void testMultipleInhExcInput() {
    final MultipleInhExcInput multipleInhExcInput = new MultipleInhExcInput();
    nestmlCoCoChecker.addCoCo(multipleInhExcInput);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "multipleInhExcInput/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        MultipleInhExcInput.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "multipleInhExcInput/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        MultipleInhExcInput.ERROR_CODE,
        4);
  }

  @Test
  public void testMultipleOutputs() {
    final MultipleOutputs multipleOutputs = new MultipleOutputs();
    nestmlCoCoChecker.addCoCo(multipleOutputs);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "multipleOutputs/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        MultipleOutputs.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "multipleOutputs/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        MultipleOutputs.ERROR_CODE,
        1);
  }

  @Test
  public void testFunctionNameChecker() {
    final NESTFunctionNameChecker functionNameChecker = new NESTFunctionNameChecker();
    nestmlCoCoChecker.addCoCo(functionNameChecker);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "functionNameChecker/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NESTFunctionNameChecker.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "functionNameChecker/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NESTFunctionNameChecker.ERROR_CODE,
        8);
  }

  @Test
  public void testNESTGetterSetterFunctionNames() {
    final GetterSetterFunctionNames getterSetterFunctionNames = new GetterSetterFunctionNames();
    nestmlCoCoChecker.addCoCo(getterSetterFunctionNames);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "getterSetterFunctionNames/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        GetterSetterFunctionNames.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "getterSetterFunctionNames/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        GetterSetterFunctionNames.ERROR_CODE,
        4);
  }

  @Test
  public void testNeuronNeedsDynamicsWithNoDynamics() {
    final NeuronNeedsDynamics neuronNeedsDynamics = new NeuronNeedsDynamics();
    nestmlCoCoChecker.addCoCo(neuronNeedsDynamics);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "neuronNeedsDynamics/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NeuronNeedsDynamics.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "neuronNeedsDynamics/invalid_noDynamics.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NeuronNeedsDynamics.ERROR_CODE,
        1);
  }

  @Test
  public void testNeuronNeedsDynamicsWithMultipleDynamics() {
    final NeuronNeedsDynamics neuronNeedsDynamics = new NeuronNeedsDynamics();
    nestmlCoCoChecker.addCoCo(neuronNeedsDynamics);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "neuronNeedsDynamics/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NeuronNeedsDynamics.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "neuronNeedsDynamics/invalid_multipleDynamics.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NeuronNeedsDynamics.ERROR_CODE,
        1);
  }

  @Test
  public void testNeuronWithoutInput() {
    final NeuronWithoutInput neuronWithoutInput = new NeuronWithoutInput();
    nestmlCoCoChecker.addCoCo(neuronWithoutInput);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "neuronWithoutInput/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NeuronWithoutInput.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "neuronWithoutInput/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NeuronWithoutInput.ERROR_CODE,
        1);
  }

  @Test
  public void testNeuronWithoutOutput() {
    final NeuronWithoutOutput neuronWithoutOutput = new NeuronWithoutOutput();
    nestmlCoCoChecker.addCoCo(neuronWithoutOutput);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "neuronWithoutOutput/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NeuronWithoutOutput.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "neuronWithoutOutput/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NeuronWithoutOutput.ERROR_CODE,
        1);
  }

  @Test
  public void testTypesDeclaredMultipleTimes() {
    final TypeIsDeclaredMultipleTimes typeIsDeclaredMultipleTimes = new TypeIsDeclaredMultipleTimes();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) typeIsDeclaredMultipleTimes);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) typeIsDeclaredMultipleTimes);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "typeIsDeclaredMultipleTimes/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        TypeIsDeclaredMultipleTimes.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "typeIsDeclaredMultipleTimes/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        TypeIsDeclaredMultipleTimes.ERROR_CODE,
        2);
  }


  @Test
  public void testUsesOnlyComponents() {
    final UsesOnlyComponents usesOnlyComponents = new UsesOnlyComponents();
    nestmlCoCoChecker.addCoCo(usesOnlyComponents);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "usesOnlyComponents/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        UsesOnlyComponents.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "usesOnlyComponents/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        UsesOnlyComponents.ERROR_CODE,
        2);
  }

  @Test
  public void testBufferNotAssignable() {
    final BufferNotAssignable bufferNotAssignable = new BufferNotAssignable();
    // TODO: rewrite: Must be possible: wait for the visitor that visits super types
    nestmlCoCoChecker.addCoCo(bufferNotAssignable);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "bufferNotAssignable/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        BufferNotAssignable.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "bufferNotAssignable/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        BufferNotAssignable.ERROR_CODE,
        1);
  }

  @Test
  public void testVarHasTypeName() {
    final VarHasTypeName varHasTypeName = new VarHasTypeName();
    nestmlCoCoChecker.addCoCo(varHasTypeName);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "varHasTypeName/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        SplErrorStrings.code(varHasTypeName));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "varHasTypeName/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        SplErrorStrings.code(varHasTypeName),
        2);
  }

  @Test
  public void testSplInFunctions() {
    final NESTMLCoCoChecker nestmlCoCoCheckerWithSPLCocos = new NESTMLCoCoChecker();
    final SPLCoCosManager splCoCosManager  = new SPLCoCosManager();
    splCoCosManager.addSPLCocosToNESTMLChecker(nestmlCoCoCheckerWithSPLCocos);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "splInFunctions/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoCheckerWithSPLCocos,
        "SPL_");

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "splInFunctions/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoCheckerWithSPLCocos,
        "SPL_",
        20);

  }

  @Test
  public void testUndefinedVariablesInEquations() {
    final VariableDoesNotExist variableDoesNotExist = new VariableDoesNotExist();
    nestmlCoCoChecker.addCoCo((ODEASTOdeDeclarationCoCo) variableDoesNotExist);
    nestmlCoCoChecker.addCoCo((CommonsASTFunctionCallCoCo) variableDoesNotExist);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "equations/validEquations.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        "NESTML_");

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "equations/invalidEquations.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        "NESTML_",
        6);
    
  }

  @Test
  public void testInvalidInvariantExpressionType() {
    final BooleanInvariantExpressions booleanInvariantExpressions
        = new BooleanInvariantExpressions();
    nestmlCoCoChecker.addCoCo(booleanInvariantExpressions);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "booleanInvariantExpressions/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        BooleanInvariantExpressions.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "booleanInvariantExpressions/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        BooleanInvariantExpressions.ERROR_CODE,
        2);

  }

  @Test
  public void testAliasHasDefiningExpression() {
    final AliasHasDefiningExpression aliasHasDefiningExpression
        = new AliasHasDefiningExpression();
    nestmlCoCoChecker.addCoCo(aliasHasDefiningExpression);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "aliasHasDefiningExpression/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        AliasHasDefiningExpression.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "aliasHasDefiningExpression/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        AliasHasDefiningExpression.ERROR_CODE,
        1);

  }

  @Test
  public void testOnlyStateVariablesInOde() {
    final EquationsOnlyForStateVariables equationsOnlyForStateVariables
        = new EquationsOnlyForStateVariables();
    nestmlCoCoChecker.addCoCo(equationsOnlyForStateVariables);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "equationsOnlyForStateVariables/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        EquationsOnlyForStateVariables.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "equationsOnlyForStateVariables/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        EquationsOnlyForStateVariables.ERROR_CODE,
        2);

  }

  @Test
  public void tesDerivativeOrderAtLeastOne() {
    final DerivativeOrderAtLeastOne derivativeOrderAtLeastOne = new DerivativeOrderAtLeastOne();
    nestmlCoCoChecker.addCoCo(derivativeOrderAtLeastOne);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "derivativeOrderAtLeastOne/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        DerivativeOrderAtLeastOne.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "derivativeOrderAtLeastOne/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        DerivativeOrderAtLeastOne.ERROR_CODE,
        1);

  }
  
  @Test
  public void testI_SumHasCorrectParameter() {
    final SumHasCorrectParameter _sumHasCorrectParameter = new SumHasCorrectParameter();
    nestmlCoCoChecker.addCoCo(_sumHasCorrectParameter);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "i_SumHasCorrectParameter/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        SumHasCorrectParameter.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "i_SumHasCorrectParameter/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        SumHasCorrectParameter.ERROR_CODE,
        3);

  }

  @Test
  public void testAssignmentToAlias() {
    final AssignmentToAlias assignmentToAlias = new AssignmentToAlias();
    nestmlCoCoChecker.addCoCo(assignmentToAlias);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/assignmentToAlias.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        AssignmentToAlias.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/assignmentToAlias.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        AssignmentToAlias.ERROR_CODE,
        1);

  }

  private void checkModelAndAssertNoErrors(
      final Path pathToModel,
      final NESTMLCoCoChecker nestmlCoCoChecker,
      final String expectedErrorCode) {
    checkModelAndAssertWithErrors(pathToModel, nestmlCoCoChecker, expectedErrorCode, 0);

  }

  private void checkModelAndAssertWithErrors(
      final Path pathToModel,
      final NESTMLCoCoChecker nestmlCoCoChecker,
      final String expectedErrorCode,
      final Integer expectedNumberCount) {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToModel.toString(), Paths.get(TEST_MODELS_FOLDER));
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());

    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(expectedErrorCode, getFindings());
    assertEquals(expectedNumberCount, errorsFound);

  }

}
