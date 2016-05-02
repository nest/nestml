/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.parsing;

import de.se_rwth.commons.logging.Log;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLLanguage;

import java.io.IOException;
import java.nio.file.*;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertTrue;
import static org.nest.utils.FilesHelper.collectFiles;

/**
 * Tests whether the nestml model can be parsed
 */
public class NESTMLParserTest extends ModelbasedTest {
  private final static  String LOG_NAME = NESTMLParserTest.class.getName();


  @Test
  public void testParsableModels() throws IOException {
    final List<Path> filenames = collectFiles(
        TEST_MODEL_PATH,
        model -> model.endsWith(NESTMLLanguage.FILE_ENDING));

    filenames.forEach(this::parseAndCheck);
  }

  private void parseAndCheck(Path file) {
    Log.info(String.format("Processes the following file: %s", file.toString()), LOG_NAME);

    Optional<ASTNESTMLCompilationUnit> ast;
    try {
      ast = parser.parse(file.toString());
    }
    catch (IOException e) {
      throw new RuntimeException(e);
    }
    assertTrue(ast.isPresent());
  }

}
