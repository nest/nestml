/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.symboltable.Scope;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests how the Python output is transformed into the NESTML AST that can be appended to the
 * NESTML model.
 *
 * @author plonikov
 */
public class LinearSolutionTransformerTest extends ModelbasedTest {

  private static final String TARGET_TMP_MODEL_PATH = "target/tmp.nestml";

  private final static Path P30_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      LinearSolutionTransformer.P30_FILE);

  private final static Path PSC_INITIAL_VALUE_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      LinearSolutionTransformer.PSC_INITIAL_VALUE_FILE);

  private final static Path STATE_VARIABLES_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      LinearSolutionTransformer.STATE_VARIABLES_FILE);

  private final static Path PROPAGATPR_MATRIX_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      LinearSolutionTransformer.PROPAGATOR_MATRIX_FILE);

  private final static Path PROPAGATPR_STEP_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      LinearSolutionTransformer.PROPAGATOR_STEP_FILE);

  private final static Path STATE_VECTOR_TMP_DECLARATIONS_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      LinearSolutionTransformer.STATE_VECTOR_TMP_DECLARATIONS_FILE);

  private final static Path STATE_UPDATE_STEPS_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      LinearSolutionTransformer.STATE_VECTOR_UPDATE_STEPS_FILE);

  private final static Path STATE_VECTOR_BACK_ASSIGNMENTS_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      LinearSolutionTransformer.STATE_VECTOR_TMP_BACK_ASSIGNMENTS_FILE);

  private static final String NEURON_NAME = "iaf_psc_alpha_nestml";
  private static final String MODEL_FILE_PATH = "models/iaf_psc_alpha.nestml";

  @Test
  public void testExactSolutionTransformation() {
    final LinearSolutionTransformer linearSolutionTransformer = new LinearSolutionTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);
    linearSolutionTransformer.addExactSolution(
        modelRoot.getNeurons().get(0),
        P30_FILE,
        PSC_INITIAL_VALUE_FILE,
        STATE_VARIABLES_FILE,
        PROPAGATPR_MATRIX_FILE,
        PROPAGATPR_STEP_FILE,
        STATE_VECTOR_TMP_DECLARATIONS_FILE,
        STATE_UPDATE_STEPS_FILE,
        STATE_VECTOR_BACK_ASSIGNMENTS_FILE);

    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);

    final NESTMLScopeCreator scopeCreator2 = new NESTMLScopeCreator(TEST_MODEL_PATH);
    final Scope scope = scopeCreator2.runSymbolTableCreator(testant);

    Optional<NeuronSymbol> neuronSymbol = scope.resolve(NEURON_NAME, NeuronSymbol.KIND);

    final Optional<VariableSymbol> p30Symbol = neuronSymbol.get().getVariableByName("P30");
    assertTrue(p30Symbol.isPresent());
    assertTrue(p30Symbol.get().getBlockType().equals(VariableSymbol.BlockType.INTERNAL));

    final Optional<VariableSymbol> pscInitialValue = neuronSymbol.get().getVariableByName("y1_I_shape_inPSCInitialValue");
    assertTrue(pscInitialValue.isPresent());
    assertTrue(pscInitialValue.get().getBlockType().equals(VariableSymbol.BlockType.INTERNAL));


    final Optional<VariableSymbol> y2 = neuronSymbol.get().getVariableByName("y2_I_shape_in");
    assertTrue(y2.isPresent());
    assertTrue(y2.get().getBlockType().equals(VariableSymbol.BlockType.STATE));

    assertTrue(neuronSymbol.get().getUpdateBlock().getSpannedScope().resolve("y2_I_shape_in_tmp", VariableSymbol.KIND).isPresent());
  }

  @Test
  public void testAddingP00Value() {
    final LinearSolutionTransformer linearSolutionTransformer = new LinearSolutionTransformer();
    // false abstraction level
    ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    linearSolutionTransformer.addAliasToInternals(modelRoot.getNeurons().get(0), P30_FILE);

    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);

    final Scope scope = scopeCreator.runSymbolTableCreator(testant);
    Optional<NeuronSymbol> symbol = scope.resolve(
        NEURON_NAME,
        NeuronSymbol.KIND);

    final Optional<VariableSymbol> p00Symbol = symbol.get().getVariableByName("P30");

    assertTrue(p00Symbol.isPresent());
    assertTrue(p00Symbol.get().getBlockType().equals(VariableSymbol.BlockType.INTERNAL));
  }

  @Test
  public void testReplaceODEThroughMatrixMultiplication() {
    final LinearSolutionTransformer linearSolutionTransformer = new LinearSolutionTransformer();
    // false abstraction level
    ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    linearSolutionTransformer.replaceODEPropagationStep(
        modelRoot.getNeurons().get(0),
        PROPAGATPR_STEP_FILE);
    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    parseNESTMLModel(TARGET_TMP_MODEL_PATH);
  }

  @Test
  public void testAddingPSCInitialValue() {
    final LinearSolutionTransformer linearSolutionTransformer = new LinearSolutionTransformer();
    // false abstraction level
    ASTNESTMLCompilationUnit modelRoot = parseAndBuildSymboltable(MODEL_FILE_PATH);
    linearSolutionTransformer.addDeclarationsToInternals(
        modelRoot.getNeurons().get(0),
        PSC_INITIAL_VALUE_FILE);
    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);

    final Scope scope = scopeCreator.runSymbolTableCreator(testant);

    Optional<NeuronSymbol> symbol = scope.resolve(NEURON_NAME, NeuronSymbol.KIND);

    final Optional<VariableSymbol> pscInitialValue = symbol.get().getVariableByName("y1_I_shape_inPSCInitialValue");

    assertTrue(pscInitialValue.isPresent());
    assertTrue(pscInitialValue.get().getBlockType().equals(VariableSymbol.BlockType.INTERNAL));
  }

  @Test
  public void testAddingStateVariables() {
    final LinearSolutionTransformer linearSolutionTransformer = new LinearSolutionTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);

    linearSolutionTransformer.addStateVariables(STATE_VARIABLES_FILE, modelRoot.getNeurons().get(0));

    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);
    testant.setPackageName("codegeneration");
    testant.setArtifactName("iaf_psc_alpha_neuron");
    final Scope scope = scopeCreator.runSymbolTableCreator(testant);

    Optional<NeuronSymbol> neuronSymbol = scope.resolve(NEURON_NAME, NeuronSymbol.KIND);

    final Optional<VariableSymbol> y1 = neuronSymbol.get().getVariableByName("y1_I_shape_in");
    assertTrue(y1.isPresent());
    assertTrue(y1.get().getBlockType().equals(VariableSymbol.BlockType.STATE));
  }

}
