/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import com.google.common.collect.Lists;
import de.monticore.symboltable.Scope;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml._symboltable.symbols.NeuronSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests how the Python output is transformed into the NESTML AST that can be appended to the
 * NESTML model.
 *
 * @author plonikov
 */
public class LinearSolutionTransformerTest extends ModelbasedTest {
  private static final String NEURON_NAME = "iaf_psc_alpha_neuron";
  private static final String MODEL_FILE_PATH = "models/iaf_psc_alpha.nestml";
  private static final String TARGET_TMP_MODEL_PATH = "target/tmp.nestml";



  @Test
  public void testExactSolutionTransformation() {
    final LinearSolutionTransformer linearSolutionTransformer = new LinearSolutionTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNestmlModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);
    linearSolutionTransformer.addExactSolution(
        modelRoot.getNeurons().get(0),
        new SolverOutput());

    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNestmlModel(TARGET_TMP_MODEL_PATH);

    final NESTMLScopeCreator scopeCreator2 = new NESTMLScopeCreator();
    final Scope scope = scopeCreator2.runSymbolTableCreator(testant);

    Optional<NeuronSymbol> neuronSymbol = scope.resolve(NEURON_NAME, NeuronSymbol.KIND);

    final Optional<VariableSymbol> p30Symbol = neuronSymbol.get().getVariableByName("P30");
    assertTrue(p30Symbol.isPresent());
    assertTrue(p30Symbol.get().getBlockType().equals(VariableSymbol.BlockType.INTERNALS));

    final Optional<VariableSymbol> pscInitialValue = neuronSymbol.get().getVariableByName("y1_I_shape_inPSCInitialValue");
    assertTrue(pscInitialValue.isPresent());
    assertTrue(pscInitialValue.get().getBlockType().equals(VariableSymbol.BlockType.INTERNALS));


    final Optional<VariableSymbol> y2 = neuronSymbol.get().getVariableByName("y2_I_shape_in");
    assertTrue(y2.isPresent());
    assertTrue(y2.get().getBlockType().equals(VariableSymbol.BlockType.STATE));

    assertTrue(neuronSymbol.get().getUpdateBlock().getSpannedScope().resolve("y2_I_shape_in_tmp", VariableSymbol.KIND).isPresent());
  }

  @Test
  public void testReplaceODEThroughMatrixMultiplication() {
    final LinearSolutionTransformer linearSolutionTransformer = new LinearSolutionTransformer();
    // false abstraction level
    ASTNESTMLCompilationUnit modelRoot = parseNestmlModel(MODEL_FILE_PATH);
    linearSolutionTransformer.replaceIntegrateCallThroughPropagation(
        modelRoot.getNeurons().get(0),
        Lists.newArrayList());
    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    parseNestmlModel(TARGET_TMP_MODEL_PATH);
  }


}
