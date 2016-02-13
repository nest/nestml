/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.parsing;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Log;
import org.junit.Test;
import org.nest.base.ModebasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLLanguage;
import org.nest.utils.FileHelper;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertTrue;
import static org.nest.utils.FileHelper.collectModelFilenames;

/**
 * Tests whether the nestml model can be parsed
 */
public class NESTMLParserTest extends ModebasedTest {
  private final static  String LOG_NAME = NESTMLParserTest.class.getName();


  @Test
  public void testParsableModels() throws IOException {
    final List<Path> filenames = collectModelFilenames(
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
