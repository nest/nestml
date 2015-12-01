/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.symboltable.Scope;
import org.junit.Test;
import org.nest.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;
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

    final Optional<NESTMLNeuronSymbol> neuronSymbol = scope.resolve(
        NEURON_NAME,
        NESTMLNeuronSymbol.KIND);

    final Optional<NESTMLVariableSymbol> y0 = neuronSymbol.get().getVariableByName("y0");
    assertTrue(y0.isPresent());
    assertTrue(y0.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));

    final Optional<NESTMLVariableSymbol> y1 = neuronSymbol.get().getVariableByName("y1");
    assertTrue(y1.isPresent());
    assertTrue(y1.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));
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