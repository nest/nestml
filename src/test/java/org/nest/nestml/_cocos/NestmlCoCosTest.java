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
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml._symboltable.predefined.PredefinedTypes;
import org.nest.nestml._symboltable.symbols.TypeSymbol;

import java.io.IOException;
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
public class NestmlCoCosTest extends ModelbasedTest {

  private static final String TEST_MODELS_FOLDER = "src/test/resources/org/nest/nestml/_cocos/";
  private static final String TEST_VALID_MODELS_FOLDER = "src/test/resources/org/nest/nestml/_cocos/valid";
  private static final String TEST_INVALID_MODELS_FOLDER = "src/test/resources/org/nest/nestml/_cocos/invalid";
  protected final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator();

  private NESTMLCoCoChecker nestmlCoCoChecker;

  @Before
  public void setup() {
    nestmlCoCoChecker = new NESTMLCoCoChecker();
  }


  @Test
  public void testVarDefinedMultipleTimes() throws IOException {
    final BlockVariableDefinedMultipleTimes BlockVariableDefinedMultipleTimes = new BlockVariableDefinedMultipleTimes();
    nestmlCoCoChecker.addCoCo(BlockVariableDefinedMultipleTimes);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "varDefinedMultipleTimes.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(BlockVariableDefinedMultipleTimes)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "varDefinedMultipleTimes.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(BlockVariableDefinedMultipleTimes),
        12 * 2); // TODO must be 6! Some declrations are checked multiple times Checks take place 2 times
  }

  @Test
  public void testVariableIsNotDefinedBeforeUse() throws IOException {
    final VariableNotDefinedBeforeUse variableNotDefinedBeforeUse = new VariableNotDefinedBeforeUse();

    nestmlCoCoChecker.addCoCo((NESTMLASTAssignmentCoCo) variableNotDefinedBeforeUse);
    nestmlCoCoChecker.addCoCo((NESTMLASTDeclarationCoCo) variableNotDefinedBeforeUse);
    nestmlCoCoChecker.addCoCo((NESTMLASTFOR_StmtCoCo) variableNotDefinedBeforeUse);
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCallCoCo) variableNotDefinedBeforeUse);
    nestmlCoCoChecker.addCoCo((NESTMLASTWHILE_StmtCoCo) variableNotDefinedBeforeUse);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "varNotDefinedBeforeUse.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(variableNotDefinedBeforeUse)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "varNotDefinedBeforeUse.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(variableNotDefinedBeforeUse),
        10);
  }

  @Test
  public void testIllegalVarInFor() throws IOException {

    final IllegalExpression illegalVarInFor = new IllegalExpression();
    nestmlCoCoChecker.addCoCo((NESTMLASTFOR_StmtCoCo) illegalVarInFor);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "illegalVarInFor.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(illegalVarInFor)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "illegalVarInFor.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(illegalVarInFor),
        3);
  }

  @Test
  public void testIllegalExpression() throws IOException {
    final IllegalExpression illegalExpression = new IllegalExpression();
    nestmlCoCoChecker.addCoCo((NESTMLASTAssignmentCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTDeclarationCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTELIF_ClauseCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTFOR_StmtCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTIF_ClauseCoCo) illegalExpression);
    nestmlCoCoChecker.addCoCo((NESTMLASTWHILE_StmtCoCo) illegalExpression);

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "illegalNumberExpressions.nestml"),
        nestmlCoCoChecker,
        "SPL_",
        9);
  }

  @Test
  public void testCodeAfterReturn() throws IOException {
    final CodeAfterReturn codeAfterReturn = new CodeAfterReturn();
    nestmlCoCoChecker.addCoCo(codeAfterReturn);

    checkModelAndAssertNoErrors(
        Paths.get(TEST_VALID_MODELS_FOLDER, "codeAfterReturn.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(codeAfterReturn)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "codeAfterReturn.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(codeAfterReturn),
        1);
  }

  @Test
  public void testFunctionExists() throws IOException {
    final FunctionWithSignatureDoesNotExist functionWithSignatureDoesNotExist = new FunctionWithSignatureDoesNotExist();
    nestmlCoCoChecker.addCoCo(functionWithSignatureDoesNotExist);

    checkModelAndAssertNoErrors(
        Paths.get("models", "hh_psc_alpha.nestml"),//Paths.get(TEST_VALID_MODELS_FOLDER, "funNotDefined.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(functionWithSignatureDoesNotExist)
    );

    checkModelAndAssertWithErrors(
        Paths.get(TEST_INVALID_MODELS_FOLDER, "funNotDefined.nestml"),
        nestmlCoCoChecker,
        SplErrorStrings.code(functionWithSignatureDoesNotExist),
        2 * 2); // ERRORs are reported as part of the symbol table and in course of the coco check
  }

  @Test
  public void testResolvingOfPredefinedTypes() {
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(
        Paths.get(TEST_MODELS_FOLDER, "valid/resolvePredefinedTypes.nestml").toString());
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
        TEST_MODELS_FOLDER + "restrictUseOfShapes/valid.nestml");
    assertTrue(validRoot.isPresent());
    scopeCreator.runSymbolTableCreator(validRoot.get());
    final RestrictUseOfShapes restrictUseOfShapes = new RestrictUseOfShapes();

    nestmlCoCoChecker.addCoCo(restrictUseOfShapes);
    nestmlCoCoChecker.checkAll(validRoot.get());

    Integer errorsFound = countErrorsByPrefix(NestmlErrorStrings.code(restrictUseOfShapes), getFindings());
    assertEquals(Integer.valueOf(0), errorsFound);

    Log.getFindings().clear();

    final Optional<ASTNESTMLCompilationUnit> invalidRoot = getAstRoot(
        TEST_MODELS_FOLDER + "restrictUseOfShapes/invalid.nestml");
    assertTrue(invalidRoot.isPresent());
    scopeCreator.runSymbolTableCreator(invalidRoot.get());

    nestmlCoCoChecker.checkAll(invalidRoot.get());
    errorsFound = countErrorsByPrefix(NestmlErrorStrings.code(restrictUseOfShapes), getFindings());
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
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCoCo) invalidTypesInDeclaration);
    nestmlCoCoChecker.addCoCo((NESTMLASTDeclarationCoCo) invalidTypesInDeclaration);

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

    //TODO parse
    /*
    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/memberVariableDefinedMultipleTimes.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(new MemberVariableDefinedMultipleTimes()),
        5); // some of the errors is reported twice
        */
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
    nestmlCoCoChecker.addCoCo(functionDefinedMultipleTimes);

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
        12); // this coco is checked twice. during the symboltabe construction and in the test
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
    nestmlCoCoChecker.addCoCo(typeIsDeclaredMultipleTimes);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "typeIsDeclaredMultipleTimes/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(typeIsDeclaredMultipleTimes));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "typeIsDeclaredMultipleTimes/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(typeIsDeclaredMultipleTimes),
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
        2*2); // this error is checked twice: as a part of the symboltable construction and in the coco
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
  public void testUndefinedVariablesInEquations() {
    final UsageOfAmbiguousName usageOfAmbiguousName = new UsageOfAmbiguousName();
    nestmlCoCoChecker.addCoCo((NESTMLASTOdeDeclarationCoCo) usageOfAmbiguousName);
    nestmlCoCoChecker.addCoCo((NESTMLASTCompound_StmtCoCo) usageOfAmbiguousName);
    nestmlCoCoChecker.addCoCo((NESTMLASTAssignmentCoCo) usageOfAmbiguousName);
    nestmlCoCoChecker.addCoCo((NESTMLASTDeclarationCoCo) usageOfAmbiguousName);
    nestmlCoCoChecker.addCoCo((NESTMLASTFunctionCallCoCo) usageOfAmbiguousName);
    nestmlCoCoChecker.addCoCo((NESTMLASTReturnStmtCoCo) usageOfAmbiguousName);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/variableDoesNotExist.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(usageOfAmbiguousName));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/variableDoesNotExist.nestml");
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToInvalidModel.toString());
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());
    Integer errorsFound = countErrorsByPrefix(NestmlErrorStrings.code(usageOfAmbiguousName), getFindings());
    assertEquals(Integer.valueOf(11), errorsFound);
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

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/equationsOnlyForStateVariables.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(equationsOnlyForStateVariables));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/equationsOnlyForStateVariables.nestml");

    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToInvalidModel.toString());
    scopeCreator.runSymbolTableCreator(ast.get());

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

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "valid/derivativeOrderAtLeastOne.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(derivativeOrderAtLeastOne));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/derivativeOrderAtLeastOne.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(derivativeOrderAtLeastOne),
        1);

  }
  
  @Test
  public void testConvolveHasCorrectParameter() {
    final ConvolveHasCorrectParameter convolveHasCorrectParameter = new ConvolveHasCorrectParameter();
    nestmlCoCoChecker.addCoCo(convolveHasCorrectParameter);

    final Path pathToValidModel = Paths.get(TEST_MODELS_FOLDER, "ConvolveHasCorrectParameter/valid.nestml");
    checkModelAndAssertNoErrors(
        pathToValidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(convolveHasCorrectParameter));

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "ConvolveHasCorrectParameter/invalid.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(convolveHasCorrectParameter),
        3);

  }

  @Test
  public void testIllegalAssignment(){
    final IllegalAssignment illegalAssignment = new IllegalAssignment();
    nestmlCoCoChecker.addCoCo(illegalAssignment);

    final Path pathToInvalidModel = Paths.get(TEST_MODELS_FOLDER, "invalid/illegalAssignments.nestml");
    checkModelAndAssertWithErrors(
        pathToInvalidModel,
        nestmlCoCoChecker,
        NestmlErrorStrings.code(illegalAssignment),
        4);
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
    final Optional<ASTNESTMLCompilationUnit> ast = getAstRoot(pathToModel.toString());
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());
    NESTMLPrettyPrinter p = NESTMLPrettyPrinter.Builder.build();
    ast.get().accept(p);

    nestmlCoCoChecker.checkAll(ast.get());

    Integer errorsFound = countErrorsByPrefix(expectedErrorCode, getFindings());
    assertEquals(expectedNumberCount, errorsFound);

  }

}