/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._parser;

import de.se_rwth.commons.logging.Log;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLLanguage;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertTrue;
import static org.nest.utils.FilesHelper.collectFiles;

/**
 * Tests whether the nestml model can be parsed
 */
public class NESTMLParserModelCoverage extends ModelbasedTest {
  private final static  String LOG_NAME = NESTMLParserModelCoverage.class.getName();


  @Test
  public void testParsableModels() throws IOException {
    final List<Path> filenames = collectFiles(
        TEST_MODEL_PATH,
        model -> model.getFileName().toString().endsWith(NESTMLLanguage.FILE_ENDING));

    filenames.addAll(collectFiles(
        Paths.get("src/test/resources"),
        model -> model.getFileName().toString().endsWith(NESTMLLanguage.FILE_ENDING) && !model.toString().contains("unparsable")));

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
