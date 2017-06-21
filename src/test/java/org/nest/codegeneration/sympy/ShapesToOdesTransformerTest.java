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
import org.nest.nestml._symboltable.symbols.NeuronSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;

import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Checks that the model transformation adds psc initial values and derivative variables
 *
 * @author plotnikov
 */
public class ShapesToOdesTransformerTest extends ModelbasedTest {
  private static final String TARGET_TMP_MODEL_PATH = "target/tmp.nestml";

  private static final String NEURON_NAME = "iaf_cond_alpha_neuron";
  private static final String MODEL_FILE_PATH = "models/iaf_cond_alpha.nestml";

  @Test
  public void testExactSolutionTransformation() {
    final ShapesToOdesTransformer shapesToOdesTransformer = new ShapesToOdesTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNestmlModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);
    shapesToOdesTransformer.transformShapesToOdeForm(new SolverOutput(), modelRoot.getNeurons().get(0));

    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNestmlModel(TARGET_TMP_MODEL_PATH);
    testant.setArtifactName("iaf_cond_alpha");
    final NESTMLScopeCreator scopeCreator2 = new NESTMLScopeCreator();
    final Scope scope = scopeCreator2.runSymbolTableCreator(testant);

    Optional<NeuronSymbol> neuronSymbol = scope.resolve(NEURON_NAME, NeuronSymbol.KIND);
    assertTrue(neuronSymbol.isPresent());
    final Optional<VariableSymbol> pscInitialValue1 = neuronSymbol.get().getVariableByName("g_in__D_PSCInitialValue");
    assertTrue(pscInitialValue1.isPresent());
    assertTrue(pscInitialValue1.get().getBlockType().equals(VariableSymbol.BlockType.INTERNALS));

    final Optional<VariableSymbol> pscInitialValue2 = neuronSymbol.get().getVariableByName("g_ex__D_PSCInitialValue");
    assertTrue(pscInitialValue2.isPresent());
    assertTrue(pscInitialValue2.get().getBlockType().equals(VariableSymbol.BlockType.INTERNALS));

    final Optional<VariableSymbol> shapeAsState = neuronSymbol.get().getVariableByName("g_ex");
    assertTrue(shapeAsState.isPresent());
    assertTrue(shapeAsState.get().getBlockType().equals(VariableSymbol.BlockType.STATE));

    final Optional<VariableSymbol> derivedStateVariable = neuronSymbol.get().getVariableByName("g_ex'");
    assertTrue(derivedStateVariable.isPresent());
    assertTrue(derivedStateVariable.get().getBlockType().equals(VariableSymbol.BlockType.STATE));

  }

}