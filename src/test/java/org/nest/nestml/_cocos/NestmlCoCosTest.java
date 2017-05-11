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
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.ode._cocos.DerivativeOrderAtLeastOne;
import org.nest.ode._cocos.EquationsOnlyForStateVariables;
import org.nest.ode._cocos.SumHasCorrectParameter;
import org.nest.ode._cocos.VariableDoesNotExist;
import org.nest.spl._cocos.SPLASTDeclarationCoCo;
import org.nest.spl._cocos.SplErrorStrings;
import org.nest.spl._cocos.VariableHasTypeName;
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
  public void testRestrictUseOfShapes(){
    final Optional<ASTNESTMLCompilationUnit> validRoot = getAstRoot(
        TEST_MODELS_FOLDER + "restrictUseOfShapes/valid.nestml", Paths.get(TEST_MODELS_FOLDER));
    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());
    final RestrictUseOfShapes restrictUseOfShapes = new RestrictUseOfShapes();

    nestmlCoCoChecker.addCoCo(restrictUseOfShapes);
    nestmlCoCoChecker.checkAll(validRoot.get());

    Integer errorsFound = countErrorsByPrefix(RestrictUseOfShapes.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(0), errorsFound);

    Log.getFindings().clear();

    final Optional<ASTNESTMLCompilationUnit> invalidRoot = getAstRoot(
        TEST_MODELS_FOLDER + "restrictUseOfShapes/invalid.nestml", Paths.get(TEST_MODELS_FOLDER));
    assertTrue(invalidRoot.isPresent());
    scopeCreator.runSymbolTableCreator(invalidRoot.get());

    nestmlCoCoChecker.checkAll(invalidRoot.get());
    errorsFound = countErrorsByPrefix(RestrictUseOfShapes.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(5), errorsFound);
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
    final FunctionReturnsIncorrectValue functionReturnsIncorrectValue = new FunctionReturnsIncorrectValue();
    nestmlCoCoChecker.addCoCo(functionReturnsIncorrectValue);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/functionReturnsIncorrectValue.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(functionReturnsIncorrectValue));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/functionReturnsIncorrectValue.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(functionReturnsIncorrectValue),
        9);
  }

  @Test
  public void testCurrentInputIsNotInhExc() {
    final CurrentPortIsInhOrExc currentPortIsInhOrExc = new CurrentPortIsInhOrExc();
    nestmlCoCoChecker.addCoCo(currentPortIsInhOrExc);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/currentPortIsInhOrExc.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(currentPortIsInhOrExc));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/currentPortIsInhOrExc.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(currentPortIsInhOrExc),
        3);
  }

  @Test
  public void testMissingReturnStatementInFunction() {
    final MissingReturnStatementInFunction missingReturnStatementInFunction = new MissingReturnStatementInFunction();
    nestmlCoCoChecker.addCoCo(missingReturnStatementInFunction);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/missingReturnStatementInFunction.nestml") ;
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(missingReturnStatementInFunction));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/missingReturnStatementInFunction.nestml") ;
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(missingReturnStatementInFunction),
        2);
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
        NestmlErrorStrings.code(invalidTypesInDeclaration));
    //TODO: Rewrite or drop invalid model
    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalidTypesInDeclaration/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(invalidTypesInDeclaration),
        0);
  }

  @Test
  public void testMemberVariableDefinedMultipleTimes() {

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/memberVariableDefinedMultipleTimes.nestml") ;
    // errors are reported during the construction of the symbol table
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(new MemberVariableDefinedMultipleTimes()));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/memberVariableDefinedMultipleTimes.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(new MemberVariableDefinedMultipleTimes()),
        5); // some of the errors is reported twice
  }

  @Test
  public void testMemberVariablesInitialisedInCorrectOrder() {
    final MemberVariablesInitialisedInCorrectOrder memberVariablesInitialisedInCorrectOrder
            = new MemberVariablesInitialisedInCorrectOrder();

    nestmlCoCoChecker.addCoCo(memberVariablesInitialisedInCorrectOrder);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/memberVariablesInitialisedInCorrectOrder.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(memberVariablesInitialisedInCorrectOrder));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/memberVariablesInitialisedInCorrectOrder.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(memberVariablesInitialisedInCorrectOrder),
        4);
  }

  @Test
  public void testMultipleFunctionsDeclarations() {
    final FunctionDefinedMultipleTimes functionDefinedMultipleTimes
            = new FunctionDefinedMultipleTimes();
    nestmlCoCoChecker.addCoCo((NESTMLASTComponentCoCo) functionDefinedMultipleTimes);
    nestmlCoCoChecker.addCoCo((NESTMLASTNeuronCoCo) functionDefinedMultipleTimes);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/functionDefinedMultipleTimes.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(functionDefinedMultipleTimes));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/functionDefinedMultipleTimes.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(functionDefinedMultipleTimes),
        6);
  }

  @Test
  public void testMultipleInhExcModifiers() {
    final MultipleInhExcModifiers multipleInhExcModifiers = new MultipleInhExcModifiers();
    nestmlCoCoChecker.addCoCo(multipleInhExcModifiers);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/multipleInhExcModifiers.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(multipleInhExcModifiers));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/multipleInhExcModifiers.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(multipleInhExcModifiers),
        4);
  }

  @Test
  public void testNeuronWithMultipleOrNoOutput() {
    final NeuronWithMultipleOrNoOutput neuronWithMultipleOrNoOutput = new NeuronWithMultipleOrNoOutput();
    nestmlCoCoChecker.addCoCo(neuronWithMultipleOrNoOutput);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/neuronWithMultipleOrNoOutput.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(neuronWithMultipleOrNoOutput));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/neuronWithMultipleOrNoOutput.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(neuronWithMultipleOrNoOutput),
        2);
  }

  @Test
  public void testNestFunctionCollision() {
    final NestFunctionCollision nestFunctionCollision = new NestFunctionCollision();
    nestmlCoCoChecker.addCoCo(nestFunctionCollision);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/nestFunctionCollision.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(nestFunctionCollision));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/nestFunctionCollision.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(nestFunctionCollision),
        8);
  }

  @Test
  public void testFunctionParameterHasTypeName() {
    final FunctionParameterHasTypeName functionParameterHasTypeName = new FunctionParameterHasTypeName();
    nestmlCoCoChecker.addCoCo(functionParameterHasTypeName);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/functionParameterHasTypeName.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(functionParameterHasTypeName));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/functionParameterHasTypeName.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(functionParameterHasTypeName),
        2);
  }



  @Test
  public void testNESTGetterSetterFunctionNames() {
    final GetterSetterFunctionNames getterSetterFunctionNames = new GetterSetterFunctionNames();
    nestmlCoCoChecker.addCoCo(getterSetterFunctionNames);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "getterSetterFunctionNames/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(getterSetterFunctionNames));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "getterSetterFunctionNames/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(getterSetterFunctionNames),
        4);
  }


  @Test
  public void testNeuronWithMultipleOrNoUpdate() {
    final NeuronWithMultipleOrNoUpdate neuronWithMultipleOrNoUpdate = new NeuronWithMultipleOrNoUpdate();
    nestmlCoCoChecker.addCoCo(neuronWithMultipleOrNoUpdate);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/neuronWithMultipleOrNoUpdate.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(neuronWithMultipleOrNoUpdate));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/neuronWithMultipleOrNoUpdate.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(neuronWithMultipleOrNoUpdate),
        2);
  }

  @Test
  public void testNeuronWithMultipleOrNoInput() {
    final NeuronWithMultipleOrNoInput neuronWithMultipleOrNoInput = new NeuronWithMultipleOrNoInput();
    nestmlCoCoChecker.addCoCo(neuronWithMultipleOrNoInput);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/neuronWithMultipleOrNoInput.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(neuronWithMultipleOrNoInput));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/neuronWithMultipleOrNoInput.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(neuronWithMultipleOrNoInput),
        3);
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
        NestmlErrorStrings.code(bufferNotAssignable));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "bufferNotAssignable/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(bufferNotAssignable),
        1);
  }

  @Test
  public void testVarHasTypeName() {
    final VariableHasTypeName variableHasTypeName = new VariableHasTypeName();
    nestmlCoCoChecker.addCoCo(variableHasTypeName);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/varHasTypeName.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        SplErrorStrings.code(variableHasTypeName));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/varHasTypeName.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        SplErrorStrings.code(variableHasTypeName),
        2);
  }

  @Test
  public void testVariableBlockDefinedMultipleTimes() {
    final VariableBlockDefinedMultipleTimes variableBlockDefinedMultipleTimes = new VariableBlockDefinedMultipleTimes();
    nestmlCoCoChecker.addCoCo(variableBlockDefinedMultipleTimes);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/variableBlockDefinedMultipleTimes.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(variableBlockDefinedMultipleTimes));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/variableBlockDefinedMultipleTimes.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(variableBlockDefinedMultipleTimes),
        3);
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
        16);

  }

  @Test
  public void testUndefinedVariablesInEquations() {
    final VariableDoesNotExist variableDoesNotExist = new VariableDoesNotExist();
    nestmlCoCoChecker.addCoCo(variableDoesNotExist);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "equations/validEquations.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        VariableDoesNotExist.ERROR_CODE);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "equations/invalidEquations.nestml");
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToInvalidModel.toString(), Paths.get(TEST_MODELS_FOLDER));
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());
    Integer errorsFound = countErrorsByPrefix(VariableDoesNotExist.ERROR_CODE, getFindings());
    assertEquals(Integer.valueOf(3), errorsFound);

  }

  @Test
  public void testInvalidInvariantExpressionType() {
    final InvalidTypeOfInvariant invalidTypeOfInvariant = new InvalidTypeOfInvariant();
    nestmlCoCoChecker.addCoCo(invalidTypeOfInvariant);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/invalidTypeOfInvariant.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(invalidTypeOfInvariant));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/invalidTypeOfInvariant.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(invalidTypeOfInvariant),
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
        NestmlErrorStrings.code(aliasHasDefiningExpression));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "aliasHasDefiningExpression/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(aliasHasDefiningExpression),
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
        NestmlErrorStrings.code(equationsOnlyForStateVariables));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "equationsOnlyForStateVariables/invalid.nestml");

    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToInvalidModel.toString(), Paths.get(TEST_MODELS_FOLDER));
    scopeCreator.runSymbolTableCreator(ast.get());

    // The errors are issued d
    //Integer errorsFound = countErrorsByPrefix(NestmlErrorStrings.code(equationsOnlyForStateVariables), getFindings());
    //assertEquals(Integer.valueOf(2), errorsFound);

    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(equationsOnlyForStateVariables),
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
    final SumHasCorrectParameter sumHasCorrectParameter = new SumHasCorrectParameter();
    nestmlCoCoChecker.addCoCo(sumHasCorrectParameter);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "i_SumHasCorrectParameter/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(sumHasCorrectParameter));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "i_SumHasCorrectParameter/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(sumHasCorrectParameter),
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
