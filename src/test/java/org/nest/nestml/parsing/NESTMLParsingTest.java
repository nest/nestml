/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.parsing;

import de.se_rwth.commons.logging.Log;
import org.junit.Test;
import org.nest.base.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.Optional;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**e
 * Tests whether the nestml model can be parsed
 */
public class NESTMLParsingTest extends ModelTestBase {

  private final static  String CODE_GENERATION_FOLDER = "src/test/resources/codegeneration";
  private final static  String PARSABLE_MODELS_FOLDER = "src/test/resources/org/nest/nestml/parsing";
  private final static  String COCOS_MODELS_FOLDER = "src/test/resources/org/nest/nestml/cocos";
  private final static  String LOG_NAME = NESTMLParsingTest.class.getName();
  private final NESTMLParser parser = new NESTMLParser();


  @Test
  public void testParsableModels() throws IOException {
    parseAllModelsInFolder(PARSABLE_MODELS_FOLDER);
  }

  @Test
  public void testModelsForCocos() throws IOException {
    parseAllModelsInFolder(COCOS_MODELS_FOLDER);
  }

  @Test
  public void testModelsForCodegeneration() throws IOException {
    parseAllModelsInFolder(CODE_GENERATION_FOLDER);
  }

  @Test
  public void testModelWithODE() throws IOException {
    Optional<ASTNESTMLCompilationUnit> ast = parser.parse("src/test/resources/codegeneration/iaf_neuron_ode_module.nestml");
    assertTrue(ast.isPresent());
  }

  private void parseAllModelsInFolder(final String pathToFolder) throws IOException {
    final File path = new File(pathToFolder);
    assertNotNull(path);
    Arrays.stream(path.listFiles())
        .filter(file -> !file.isDirectory())
        .forEach(file -> {
          Log.trace(String.format("Processes the following file: %s", file.getAbsolutePath()), LOG_NAME);

          Optional<ASTNESTMLCompilationUnit> ast = null;
          try {
            ast = parser.parse(file.getAbsolutePath());
          }
          catch (IOException e) {
            throw new RuntimeException(e);
          }
          assertTrue(ast.isPresent());
        });

  }

}
