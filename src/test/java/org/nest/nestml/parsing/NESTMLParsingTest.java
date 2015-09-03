/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.parsing;

import de.se_rwth.commons.logging.Log;
import org.junit.Test;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;

import java.io.File;
import java.io.IOException;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**e
 * Tests whether the nestml model can be parsed
 */
public class NESTMLParsingTest {

  private final static  String PARSABLE_MODELS_FOLDER = "src/test/resources/org/nest/nestml/parsing";
  private final static  String COCOS_MODELS_FOLDER = "src/test/resources/org/nest/nestml/cocos";
  private final static  String LOG_NAME = NESTMLParsingTest.class.getName();
  private final NESTMLCompilationUnitMCParser parser;

  public NESTMLParsingTest() {
    parser = NESTMLParserFactory.createNESTMLCompilationUnitMCParser();
  }

  @Test
  public void testParsableModels() throws IOException {

    for (File file: new File(PARSABLE_MODELS_FOLDER).listFiles()) {
      Log.trace(String.format("Processes the following file: %s", file.getAbsolutePath()), LOG_NAME);

      Optional<ASTNESTMLCompilationUnit> ast = parser.parse(file.getAbsolutePath());
      assertTrue(ast.isPresent());
    }

  }

  @Test
  public void testModelsForCocos() throws IOException {
    for (File file : new File(COCOS_MODELS_FOLDER).listFiles()) {
      if (!file.isDirectory()) {
        Log.trace(String.format("Processes the following file: %s", file.getAbsolutePath()), LOG_NAME);

        Optional<ASTNESTMLCompilationUnit> ast = parser.parse(file.getAbsolutePath());
        assertTrue(ast.isPresent());

      }
    }

  }

  @Test
  public void testModelWithODE() throws IOException {
    Optional<ASTNESTMLCompilationUnit> ast = parser.parse("src/test/resources/codegeneration/iaf_neuron_ode_module.nestml");
    assertTrue(ast.isPresent());
  }

}
