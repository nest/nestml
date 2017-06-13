/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.codegeneration.sympy.OdeProcessor;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.symbols.NeuronSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.nestml._visitor.UnitsSIVisitor;
import org.nest.utils.FilesHelper;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests if the overall transformation solveODE works
 *
 * @author plotnikov
 */
public class OdeProcessorTest extends ModelbasedTest {
  private static final String COND_MODEL_FILE = "models/iaf_cond_alpha.nestml";
  private static final String PSC_MODEL_FILE = "models/iaf_neuron.nestml";
  private static final String PSC_DELTA_MODEL_FILE = "models/iaf_psc_delta.nestml";
  private static final String PSC_NEURON_NAME = "iaf_neuron_nestml";

  private final OdeProcessor testant = new OdeProcessor();

  @Test
  public void testPscModel() throws Exception {
    final Scope scope = processModel(PSC_MODEL_FILE);

    final Optional<NeuronSymbol> neuronSymbol = scope.resolve(
        PSC_NEURON_NAME,
        NeuronSymbol.KIND);

    final Optional<VariableSymbol> y1 = neuronSymbol.get().getVariableByName("y1_G");
    assertTrue(y1.isPresent());
    assertTrue(y1.get().getBlockType().equals(VariableSymbol.BlockType.STATE));
  }

  @Ignore
  @Test
  public void testCondModel() throws Exception {
    processModel(COND_MODEL_FILE);
  }

  @Test
  public void testDeltaModel() throws Exception {
    processModel(PSC_DELTA_MODEL_FILE);
  }

  /**
   * Parses model, builds symboltable, cleanups output folder by deleting tmp file and processes ODEs from model.i
   */
  private Scope processModel(final String pathToModel) {
    final ASTNESTMLCompilationUnit modelRoot = parseNESTMLModel(pathToModel);
    scopeCreator.runSymbolTableCreator(modelRoot);
    final Path outputBase = Paths.get(OUTPUT_FOLDER.toString(), Names.getPathFromQualifiedName(pathToModel));
    FilesHelper.deleteFilesInFolder(outputBase);

    testant.solveODE(modelRoot.getNeurons().get(0), outputBase);

    UnitsSIVisitor.convertSiUnitsToSignature(modelRoot);

    return scopeCreator.runSymbolTableCreator(modelRoot);
  }

}