/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.symboltable.Scope;
import org.apache.commons.io.FileUtils;
import org.junit.Test;
import org.nest.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.io.File;
import java.io.IOException;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests how the Python output is transformed into the NESTML AST that can be appended to the
 * NESTML model.
 *
 * @author plonikov
 */
public class SymPySolutionTransformerTest extends ModelTestBase {

  public static final String TARGET_TMP_MODEL_PATH = "target/tmp.nestml";
  private final static String P30_FILE
      = "src/test/resources/codegeneration/sympy/" + SymPyScriptEvaluator.P30_FILE;
  private final static String PSC_INITIAL_VALUE_FILE
      = "src/test/resources/codegeneration/sympy/" + SymPyScriptEvaluator.PSC_INITIAL_VALUE_FILE;
  private final static String STATE_VECTOR_FILE
      = "src/test/resources/codegeneration/sympy/" + SymPyScriptEvaluator.STATE_VECTOR_FILE;
  private final static String UPDATE_STEP_FILE
      = "src/test/resources/codegeneration/sympy/" + SymPyScriptEvaluator.UPDATE_STEP_FILE;

  private static final String MODEL_FILE_PATH = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";


  @Test
  public void testExactSolutionTransformation() {
    final SymPySolutionTransformer symPySolutionTransformer = new SymPySolutionTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);
    final ASTNESTMLCompilationUnit transformedModel = symPySolutionTransformer
        .replaceODEWithSymPySolution(
            modelRoot,
            P30_FILE,
            PSC_INITIAL_VALUE_FILE,
            STATE_VECTOR_FILE,
            UPDATE_STEP_FILE);

    printModelToFile(transformedModel, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);

    final NESTMLScopeCreator scopeCreator2 = new NESTMLScopeCreator(TEST_MODEL_PATH, typesFactory);
    final Scope scope = scopeCreator2.runSymbolTableCreator(testant);
    Optional<NESTMLNeuronSymbol> neuronSymbol = scope.resolve("iaf_neuron_ode_neuron", NESTMLNeuronSymbol.KIND);

    final Optional<NESTMLVariableSymbol> p30Symbol = neuronSymbol.get().getVariableByName("P30");
    assertTrue(p30Symbol.isPresent());
    assertTrue(p30Symbol.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.INTERNAL));

    final Optional<NESTMLVariableSymbol> pscInitialValue = neuronSymbol.get().getVariableByName("PSCInitialValue");
    assertTrue(pscInitialValue.isPresent());
    assertTrue(pscInitialValue.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.INTERNAL));

    final Optional<NESTMLVariableSymbol> y0 = neuronSymbol.get().getVariableByName("y0");
    assertTrue(y0.isPresent());
    assertTrue(y0.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));

    final Optional<NESTMLVariableSymbol> y1 = neuronSymbol.get().getVariableByName("y1");
    assertTrue(y1.isPresent());
    assertTrue(y1.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));
  }

  @Test
  public void testAddingP00Value() {
    final SymPySolutionTransformer symPySolutionTransformer = new SymPySolutionTransformer();
    // false abstraction level
    final ASTNESTMLCompilationUnit transformedModel = symPySolutionTransformer.addP30(
        parseNESTMLModel(MODEL_FILE_PATH),
        P30_FILE);
    printModelToFile(transformedModel, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);

    final Scope scope = scopeCreator.runSymbolTableCreator(testant);
    Optional<NESTMLNeuronSymbol> symbol = scope.resolve("iaf_neuron_ode_neuron", NESTMLNeuronSymbol.KIND);

    final Optional<NESTMLVariableSymbol> p00Symbol = symbol.get().getVariableByName("P30");

    assertTrue(p00Symbol.isPresent());
    assertTrue(p00Symbol.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.INTERNAL));
  }

  @Test
  public void testReplaceODEThroughMatrixMultiplication() {
    final SymPySolutionTransformer symPySolutionTransformer = new SymPySolutionTransformer();
    // false abstraction level
    final ASTNESTMLCompilationUnit transformedModel = symPySolutionTransformer.replaceODE(
        parseNESTMLModel(MODEL_FILE_PATH),
        UPDATE_STEP_FILE);
    printModelToFile(transformedModel, TARGET_TMP_MODEL_PATH);

    parseNESTMLModel(TARGET_TMP_MODEL_PATH);
  }

  @Test
  public void testAddingPSCInitialValue() {
    final SymPySolutionTransformer symPySolutionTransformer = new SymPySolutionTransformer();
    // false abstraction level
    final ASTNESTMLCompilationUnit transformedModel = symPySolutionTransformer.addPSCInitialValue(
        parseNESTMLModel(MODEL_FILE_PATH),
        PSC_INITIAL_VALUE_FILE);
    printModelToFile(transformedModel, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);

    final Scope scope = scopeCreator.runSymbolTableCreator(testant);

    Optional<NESTMLNeuronSymbol> symbol = scope.resolve("iaf_neuron_ode_neuron", NESTMLNeuronSymbol.KIND);

    final Optional<NESTMLVariableSymbol> pscInitialValue = symbol.get().getVariableByName("PSCInitialValue");

    assertTrue(pscInitialValue.isPresent());
    assertTrue(pscInitialValue.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.INTERNAL));
  }

  @Test
  public void testAddingStateVariables() {
    final SymPySolutionTransformer symPySolutionTransformer = new SymPySolutionTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);

    final ASTNESTMLCompilationUnit transformedModel = symPySolutionTransformer
        .addStateVariablesAndUpdateStatements(modelRoot, STATE_VECTOR_FILE);
    printModelToFile(transformedModel, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);

    // TODO: why do I need new instance?
    NESTMLScopeCreator scopeCreator2 = new NESTMLScopeCreator(TEST_MODEL_PATH, typesFactory);
    final Scope scope = scopeCreator2.runSymbolTableCreator(testant);

    Optional<NESTMLNeuronSymbol> neuronSymbol = scope.resolve("iaf_neuron_ode_neuron", NESTMLNeuronSymbol.KIND);

    final Optional<NESTMLVariableSymbol> y0 = neuronSymbol.get().getVariableByName("y0");
    assertTrue(y0.isPresent());
    assertTrue(y0.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));

    final Optional<NESTMLVariableSymbol> y1 = neuronSymbol.get().getVariableByName("y1");
    assertTrue(y1.isPresent());
    assertTrue(y1.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));
  }



  // TODO: replace it with return root call
  private void printModelToFile(
      final ASTNESTMLCompilationUnit root,
      final String outputModelFile) {
    final NESTMLPrettyPrinter prettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    root.accept(prettyPrinter);

    final File prettyPrintedModelFile = new File(outputModelFile);
    try {
      FileUtils.write(prettyPrintedModelFile, prettyPrinter.getResult());
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot write the prettyprinted model to the file: " + outputModelFile, e);
    }
  }

}
