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

import java.util.HashMap;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests how the Python output is transformed into the NESTML AST that can be appended to the
 * NESTML model.
 *
 * @author plonikov
 */
public class ExactSolutionTransformerTest extends ModelbasedTest {
  private static final String NEURON_NAME = "iaf_psc_alpha_neuron";
  private static final String MODEL_FILE_PATH = "models/iaf_psc_alpha.nestml";
  private static final String TARGET_TMP_MODEL_PATH = "target/tmp.nestml";

  @Test
  public void testExactSolutionTransformation() {
    final ExactSolutionTransformer exactSolutionTransformer = new ExactSolutionTransformer();
    final ASTNESTMLCompilationUnit modelRoot = parseNestmlModel(MODEL_FILE_PATH);
    scopeCreator.runSymbolTableCreator(modelRoot);
    exactSolutionTransformer.addExactSolution(
        modelRoot.getNeurons().get(0),
        SolverOutput.fromJSON(SolverJsonData.IAF_PSC_ALPHA));

    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    ASTNESTMLCompilationUnit testant = parseNestmlModel(TARGET_TMP_MODEL_PATH);

    final NESTMLScopeCreator scopeCreator2 = new NESTMLScopeCreator();
    final Scope scope = scopeCreator2.runSymbolTableCreator(testant);

    Optional<NeuronSymbol> neuronSymbol = scope.resolve(NEURON_NAME, NeuronSymbol.KIND);

    final Optional<VariableSymbol> p30Symbol = neuronSymbol.get().getVariableByName("__ode_var_factor");
    assertTrue(p30Symbol.isPresent());
    assertTrue(p30Symbol.get().getBlockType().equals(VariableSymbol.BlockType.INTERNALS));

    final Optional<VariableSymbol> pscInitialValue = neuronSymbol.get().getVariableByName("I_shape_in__0");
    assertTrue(pscInitialValue.isPresent());
    assertTrue(pscInitialValue.get().getBlockType().equals(VariableSymbol.BlockType.STATE));

  }

  @Test
  public void testReplaceODEThroughMatrixMultiplication() {
    // false abstraction level
    ASTNESTMLCompilationUnit modelRoot = parseNestmlModel(MODEL_FILE_PATH);
    TransformerBase.replaceIntegrateCallThroughPropagation(
        modelRoot.getNeurons().get(0),
        new HashMap.SimpleEntry<>("__const_input", "2"), Lists.newArrayList());
    printModelToFile(modelRoot, TARGET_TMP_MODEL_PATH);

    parseNestmlModel(TARGET_TMP_MODEL_PATH);
  }


}
