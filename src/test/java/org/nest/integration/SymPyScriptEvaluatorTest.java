/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import org.junit.Ignore;
import org.junit.Test;
import org.nest.base.ModelTestBase;
import org.nest.codegeneration.sympy.SymPyScriptEvaluator;
import org.nest.codegeneration.sympy.SymPyScriptGenerator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Test evaluation of the solver script. Depends on successful script generation.
 *
 * @author plonikov
 */
@Ignore
public class SymPyScriptEvaluatorTest extends ModelTestBase {
  private static final String TEST_MODEL_PATH = "src/test/resources/";
  private static final String PSC_MODEL_FILE
      = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";
  private static final String COND_MODEL_FILE
      = "src/test/resources/codegeneration/iaf_cond_alpha_module.nestml";
  private final NESTMLParser parser = new NESTMLParser(Paths.get(TEST_MODEL_PATH));


  @Test
  public void generateAndExecuteSympyScriptForPSC() throws IOException {
    generateAndEvaluate(PSC_MODEL_FILE);
  }

  @Test
  public void generateAndExecuteSympyScriptForCOND() throws IOException {
    generateAndEvaluate(COND_MODEL_FILE);
  }

  private void generateAndEvaluate(final String pathToModel) throws IOException {
    final Optional<ASTNESTMLCompilationUnit> root = parser.parse(pathToModel);

    assertTrue(root.isPresent());

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    final Optional<Path> generatedScript = SymPyScriptGenerator.generateSympyODEAnalyzer(
        root.get().getNeurons().get(0),
        Paths.get(OUTPUT_FOLDER));

    assertTrue(generatedScript.isPresent());
    final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();

    assertTrue(evaluator.execute(generatedScript.get()));
  }

}
