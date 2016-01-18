/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import de.monticore.symboltable.Scope;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.base.ModelTestBase;
import org.nest.codegeneration.sympy.ODEProcessor;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.ASTNodes;

import java.nio.file.Paths;
import java.util.Optional;

import static de.se_rwth.commons.Names.getQualifiedName;
import static org.junit.Assert.assertTrue;

/**
 * Tests if the overall transformation process works
 *
 * @author plotnikov
 */
@Ignore
public class ODEProcessorTest extends ModelTestBase {
  private static final String COND_MODEL_FILE
      = "src/test/resources/codegeneration/iaf_cond_alpha_module.nestml";
  private static final String PSC_MODEL_FILE
      = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";
  public static final String NEURON_NAME = "iaf_neuron_ode";

  final ODEProcessor testant = new ODEProcessor();

  @Test
  public void testProcess() throws Exception {
    final Scope scope = processModel(PSC_MODEL_FILE);

    final Optional<NeuronSymbol> neuronSymbol = scope.resolve(
        NEURON_NAME,
        NeuronSymbol.KIND);

    final Optional<VariableSymbol> y1 = neuronSymbol.get().getVariableByName("y1");
    assertTrue(y1.isPresent());
    assertTrue(y1.get().getBlockType().equals(VariableSymbol.BlockType.STATE));
  }

  @Test
  public void testCondModel() throws Exception {
    processModel(COND_MODEL_FILE);

  }

  private Scope processModel(final String pathToModel) {
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(pathToModel);
    scopeCreator.runSymbolTableCreator(modelRoot);
    final String modelFolder = ASTNodes.toString(modelRoot.getPackageName());

    final ASTNESTMLCompilationUnit explicitSolution = testant
        .process(modelRoot, Paths.get(OUTPUT_FOLDER, modelFolder));

    return scopeCreator.runSymbolTableCreator(explicitSolution);
  }

}