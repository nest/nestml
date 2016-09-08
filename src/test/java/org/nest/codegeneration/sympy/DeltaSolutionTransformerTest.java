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
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.VariableSymbol;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.*;

/**
 * Tests that the transformer processes input artifacts as expected and altered the corresponding model.
 * @author plotnikov
 */
public class DeltaSolutionTransformerTest extends ModelbasedTest {
  private static final String TARGET_TMP_MODEL_PATH = "target/tmp.nestml";

  private final static Path P30_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      DeltaSolutionTransformer.P30_FILE);

  private final static Path PROPAGATPR_STEP_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/psc/",
      LinearSolutionTransformer.PROPAGATOR_STEP_FILE);
  private static final String NEURON_NAME = "iaf_psc_delta_neuron";
  private static final String MODEL_FILE_PATH = "models/iaf_psc_delta.nestml";

  @Test
  public void testAddingSolution() {
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);

    final DeltaSolutionTransformer deltaSolutionTransformer = new DeltaSolutionTransformer();

    deltaSolutionTransformer.addExactSolution(modelRoot.getNeurons().get(0), P30_FILE, PROPAGATPR_STEP_FILE);

    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);
    final ASTNeuron astNeuron = testant.getNeurons().get(0);
    final Scope scope = scopeCreator.runSymbolTableCreator(testant);
    final Optional<NeuronSymbol> neuronSymbol = scope.resolve(NEURON_NAME, NeuronSymbol.KIND);
    assertTrue(neuronSymbol.isPresent());

    final Optional<VariableSymbol> p30Variable = neuronSymbol.get().getVariableByName("P30");
    assertTrue(p30Variable.isPresent());
    final Optional<VariableSymbol> p33Variable = neuronSymbol.get().getVariableByName("__P33__");
    assertTrue(p33Variable.isPresent());
  }

}