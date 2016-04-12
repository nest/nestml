/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.codegeneration.sympy.ODEProcessor;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.symboltable.symbols.NeuronSymbol;
import org.nest.symboltable.symbols.VariableSymbol;
import org.nest.utils.FileHelper;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static de.se_rwth.commons.Names.getQualifiedName;
import static org.junit.Assert.assertTrue;

/**
 * Tests if the overall transformation solveODE works
 *
 * @author plotnikov
 */
public class ODEProcessorTest extends ModelbasedTest {
  private static final String COND_MODEL_FILE
      = "src/test/resources/codegeneration/iaf_cond_alpha.nestml";
  private static final String PSC_MODEL_FILE
      = "src/test/resources/codegeneration/iaf_neuron.nestml";
  private static final String NEURON_NAME = "iaf_neuron_nestml";

  private final ODEProcessor testant = new ODEProcessor();

  @Test
  public void testPscModel() throws Exception {
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
    final String modelFolder = modelRoot.getFullName();

    final Path outputBase = Paths.get(OUTPUT_FOLDER.toString(), Names.getPathFromQualifiedName(modelFolder));
    FileHelper.deleteFilesInFolder(outputBase);

    testant.solveODE(modelRoot.getNeurons().get(0), outputBase);

    return scopeCreator.runSymbolTableCreator(modelRoot);
  }

}