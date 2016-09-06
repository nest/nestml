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

import static org.junit.Assert.*;

/**
 * Checks that the model transformation adds psc initial values and derivative variables
 *
 * @author plotnikov
 */
public class ImplicitFormTransformerTest extends ModelbasedTest {
  private static final String TARGET_TMP_MODEL_PATH = "target/tmp.nestml";

  private final static Path PSC_INITIAL_VALUE_FILE = Paths.get(
      "src/test/resources/codegeneration/sympy/cond/",
      ImplicitFormTransformer.PSC_INITIAL_VALUE_FILE);

  private final static Path IMPLICTI_EQUATIONS = Paths.get(
      "src/test/resources/codegeneration/sympy/cond/",
      ImplicitFormTransformer.EQUATIONS_FILE);

  private static final String NEURON_NAME = "iaf_cond_alpha_neuron";
  private static final String MODEL_FILE_PATH = "models/iaf_cond_alpha.nestml";

  @Test
  public void testExactSolutionTransformation() {
    final ImplicitFormTransformer implicitFormTransformer = new ImplicitFormTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);
    implicitFormTransformer.transformToImplicitForm(
        modelRoot.getNeurons().get(0),
        PSC_INITIAL_VALUE_FILE,
        IMPLICTI_EQUATIONS);

    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNESTMLModel(TARGET_TMP_MODEL_PATH);
    testant.setPackageName("codegeneration");
    testant.setArtifactName("iaf_cond_alpha");
    final NESTMLScopeCreator scopeCreator2 = new NESTMLScopeCreator(TEST_MODEL_PATH);
    final Scope scope = scopeCreator2.runSymbolTableCreator(testant);

    Optional<NeuronSymbol> neuronSymbol = scope.resolve(NEURON_NAME, NeuronSymbol.KIND);
    assertTrue(neuronSymbol.isPresent());
    final Optional<VariableSymbol> pscInitialValue = neuronSymbol.get().getVariableByName("g_in__DPSCInitialValue");
    assertTrue(pscInitialValue.isPresent());
    assertTrue(pscInitialValue.get().getBlockType().equals(VariableSymbol.BlockType.INTERNAL));

  }
  
}