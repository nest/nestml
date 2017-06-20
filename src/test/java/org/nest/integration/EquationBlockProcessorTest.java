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
import org.nest.codegeneration.sympy.EquationBlockProcessor;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.symbols.NeuronSymbol;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.utils.FilesHelper;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Tests if the overall transformation solveOdeWithShapes works
 *
 * @author plotnikov
 */
public class EquationBlockProcessorTest extends ModelbasedTest {
  private static final String COND_MODEL_FILE = "models/iaf_cond_alpha.nestml";
  private static final String PSC_MODEL_FILE = "models/iaf_neuron.nestml";
  private static final String PSC_DELTA_MODEL_FILE = "models/iaf_psc_delta.nestml";
  private static final String PSC_NEURON_NAME = "iaf_neuron_nestml";

  private final EquationBlockProcessor testant = new EquationBlockProcessor();

  @Test
  public void testPscModel() throws Exception {
    final Scope scope = solveOdesAndShapes(PSC_MODEL_FILE);

    final Optional<NeuronSymbol> neuronSymbol = scope.resolve(PSC_NEURON_NAME, NeuronSymbol.KIND);

    final Optional<VariableSymbol> y1 = neuronSymbol.get().getVariableByName("G__0");
    final Optional<VariableSymbol> y2 = neuronSymbol.get().getVariableByName("G__1");
    assertTrue(y1.isPresent());
    assertTrue(y1.get().getBlockType().equals(VariableSymbol.BlockType.STATE));

    assertTrue(y2.isPresent());
    assertTrue(y2.get().getBlockType().equals(VariableSymbol.BlockType.STATE));
  }

  @Ignore
  @Test
  public void testCondModel() throws Exception {
    solveOdesAndShapes(COND_MODEL_FILE);
  }

  @Ignore
  @Test
  public void testDeltaModel() throws Exception {
    solveOdesAndShapes(PSC_DELTA_MODEL_FILE);
  }

  /**
   * Parses model, builds symboltable, cleanups output folder by deleting tmp file and processes ODEs from model.i
   */
  private Scope solveOdesAndShapes(final String pathToModel) {
    final ASTNESTMLCompilationUnit modelRoot = parseNestmlModel(pathToModel);
    scopeCreator.runSymbolTableCreator(modelRoot);
    final Path outputBase = Paths.get(OUTPUT_FOLDER.toString(), Names.getPathFromQualifiedName(pathToModel));
    FilesHelper.deleteFilesInFolder(outputBase);

    testant.solveOdeWithShapes(modelRoot.getNeurons().get(0), outputBase);

    return scopeCreator.runSymbolTableCreator(modelRoot);
  }

}