/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.junit.Ignore;
import org.junit.Test;
import org.nest.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.*;
import static org.nest.nestml._parser.NESTMLParserFactory.createNESTMLCompilationUnitMCParser;

/**
 * Test evaluation of the solver script. Depends on successful script generation.
 *
 * @author plonikov
 */
public class SymPyScriptEvaluatorTest extends ModelTestBase {
  private final NESTMLCompilationUnitMCParser p = createNESTMLCompilationUnitMCParser();
  private static final String TEST_MODEL_PATH = "src/test/resources/";
  private static final String PSC_MODEL_FILE
      = "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml";
  private static final String COND_MODEL_FILE
      = "src/test/resources/codegeneration/iaf_cond_alpha_module.nestml";


  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  @Test
  public void generateAndExecuteSympyScriptForPSC() throws IOException {
    generateAndEvaluate(PSC_MODEL_FILE);
  }

  @Test
  public void generateAndExecuteSympyScriptForCOND() throws IOException {
    generateAndEvaluate(COND_MODEL_FILE);
  }

  private void generateAndEvaluate(final String pathToModel) throws IOException {
    final Optional<ASTNESTMLCompilationUnit> root = p.parse(pathToModel);

    assertTrue(root.isPresent());

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(root.get());

    final Optional<Path> generatedScript = SymPyScriptGenerator.generateSympyODEAnalyzer(
        root.get().getNeurons().get(0),
        Paths.get(OUTPUT_FOLDER));

    assertTrue(generatedScript.isPresent());
    final SymPyScriptEvaluator evaluator = new SymPyScriptEvaluator();

    assertTrue(evaluator.execute(generatedScript.get()));
  }

}
