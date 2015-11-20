/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import de.monticore.symboltable.Scope;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.io.File;
import java.nio.file.Paths;
import java.util.Optional;

import static de.se_rwth.commons.Names.getPathFromPackage;
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


  final ODEProcessor testant = new ODEProcessor();

  @Test
  public void testProcess() throws Exception {
    final Scope scope = processModel(PSC_MODEL_FILE);

    final Optional<NESTMLNeuronSymbol> neuronSymbol = scope.resolve(
        "iaf_neuron_ode_neuron",
        NESTMLNeuronSymbol.KIND);

    final Optional<NESTMLVariableSymbol> y0 = neuronSymbol.get().getVariableByName("y0");
    assertTrue(y0.isPresent());
    assertTrue(y0.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));

    final Optional<NESTMLVariableSymbol> y1 = neuronSymbol.get().getVariableByName("y1");
    assertTrue(y1.isPresent());
    assertTrue(y1.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));
  }

  @Ignore// doesn't work at the moment.
  @Test
  public void testCondModel() throws Exception {
    final Scope scope = processModel(COND_MODEL_FILE);

  }

  private Scope processModel(final String pathToModel) {
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(pathToModel);
    scopeCreator.runSymbolTableCreator(modelRoot);
    String modelFolder = getPathFromPackage(
        getQualifiedName(modelRoot.getPackageName().getParts()));
    final ASTNESTMLCompilationUnit explicitSolution = testant
        .process(modelRoot, new File(Paths.get(OUTPUT_FOLDER, modelFolder).toString()));

    return scopeCreator.runSymbolTableCreator(explicitSolution);
  }

}