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
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests how the Python output is transformed into the NESTML AST that can be appended to the
 * NESTML model.
 *
 * @author plonikov
 */
public class ExactSolutionTransformerTest extends ModelbasedTest {

  private static final String TARGET_TMP_MODEL_PATH = "target/tmp.nestml";

  private final static String P30_FILE
      = "src/test/resources/codegeneration/sympy/psc/" + SymPyScriptEvaluator.P30_FILE;
  private final static String CONSTANT_FACTORS_FILE
      = "src/test/resources/codegeneration/sympy/psc/" + SymPyScriptEvaluator.CONSTANT_TERM;
  private final static String PSC_INITIAL_VALUE_FILE
      = "src/test/resources/codegeneration/sympy/psc/" + SymPyScriptEvaluator.PSC_INITIAL_VALUE_FILE;
  private final static String STATE_VECTOR_FILE
      = "src/test/resources/codegeneration/sympy/psc/" + SymPyScriptEvaluator.STATE_VECTOR_UPDATE_FILE;
  private final static String STATE_VARIABLES_FILE
      = "src/test/resources/codegeneration/sympy/psc/" + SymPyScriptEvaluator.STATE_VARIABLES_FILE;
  private final static String UPDATE_STEP_FILE
      = "src/test/resources/codegeneration/sympy/psc/" + SymPyScriptEvaluator.UPDATE_STEP_FILE;
  private static final String MODEL_FILE_PATH
      = "src/test/resources/codegeneration/iaf_psc_alpha.nestml";

  private static final String NEURON_NAME = "iaf_psc_alpha_nestml";

  @Test
  public void testExactSolutionTransformation() {
    final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);
    final ASTNeuron transformedModel = exactSolutionTransformer
        .addExactSolution(
            modelRoot.getNeurons().get(0),
            Paths.get(P30_FILE),
            Paths.get(PSC_INITIAL_VALUE_FILE),
            Paths.get(STATE_VARIABLES_FILE),
            Paths.get(STATE_VECTOR_FILE),
            Paths.get(UPDATE_STEP_FILE));

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


    final Optional<VariableSymbol> y1 = neuronSymbol.get().getVariableByName("y2_I_shape_in");
    assertTrue(y1.isPresent());
    assertTrue(y1.get().getBlockType().equals(VariableSymbol.BlockType.STATE));
  }

  @Test
  public void testAddingP00Value() {
    final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();
    // false abstraction level
    ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    exactSolutionTransformer.addP30(modelRoot.getNeurons().get(0), Paths.get(P30_FILE));

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
    final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();
    // false abstraction level
    ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    exactSolutionTransformer.replaceODEPropagationStep(
        modelRoot.getNeurons().get(0),
        Paths.get(UPDATE_STEP_FILE));
    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    parseNESTMLModel(TARGET_TMP_MODEL_PATH);
  }

  @Test
  public void testAddingPSCInitialValue() {
    final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();
    // false abstraction level
    ASTNESTMLCompilationUnit modelRoot = parseAndBuildSymboltable(MODEL_FILE_PATH);
    exactSolutionTransformer.addPSCInitialValueAndHToInternalBlock(
        modelRoot.getNeurons().get(0),
        Paths.get(PSC_INITIAL_VALUE_FILE));
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
    final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);

    exactSolutionTransformer.addStateVariablesAndUpdateStatements(
        modelRoot.getNeurons().get(0),
        Paths.get(PSC_INITIAL_VALUE_FILE),
        Paths.get(STATE_VARIABLES_FILE),
        Paths.get(STATE_VECTOR_FILE));
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
