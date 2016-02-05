/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.parsing;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Log;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.base.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLLanguage;

import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * Tests whether the nestml model can be parsed
 */
public class NESTMLParsingTest extends ModelTestBase {
  private final static  String LOG_NAME = NESTMLParsingTest.class.getName();

  private final static  String TEST_RESOURCES_PATH = "src/test/resources";

  @Test
  public void testParsableModels() throws IOException {
    final List<Path> filenames = Lists.newArrayList();
    Files.walkFileTree(Paths.get(TEST_RESOURCES_PATH), new SimpleFileVisitor<Path>() {
      @Override
      public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
        if (Files.isRegularFile(file) &&
            file.getFileName().toString().endsWith(NESTMLLanguage.FILE_ENDING)) {

          filenames.add(file);
        }
        return FileVisitResult.CONTINUE;
      }
    });

    filenames.forEach(this::parseAndCheck);
  }

  @Test
  public void testModelWithODE() throws IOException {
    Optional<ASTNESTMLCompilationUnit> ast = parser.parse(
        "src/test/resources/codegeneration/iaf_neuron_ode.nestml");
    assertTrue(ast.isPresent());
  }

  private void parseAndCheck(Path file) {
    Log.info(String.format("Processes the following file: %s", file.toString()), LOG_NAME);

    Optional<ASTNESTMLCompilationUnit> ast = null;
    try {
      ast = parser.parse(file.toString());
    }
    catch (IOException e) {
      throw new RuntimeException(e);
    }
    assertTrue(ast.isPresent());
  }

}
