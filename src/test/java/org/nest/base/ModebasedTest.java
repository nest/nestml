/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.base;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Log;
import org.apache.commons.io.FileUtils;
import org.junit.Before;
import org.junit.BeforeClass;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.spl._symboltable.SPLLanguage;

import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.List;

/**
 * Disables exit on error and provides base services for parsing and symbol table.
 *
 * @author plotnikov
 */
public class ModebasedTest {
  protected static final Path OUTPUT_FOLDER = Paths.get("target");
  protected static final Path TEST_MODEL_PATH = Paths.get("src/test/resources/");
  protected final NESTMLParser parser = new NESTMLParser(TEST_MODEL_PATH);
  protected final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH);

  @BeforeClass
  public static void disableFailQuick() {
    Log.enableFailQuick(false);
  }

  @Before
  public void clearLog() {
    Log.getFindings().clear();
  }

  public ASTNESTMLCompilationUnit parseNESTMLModel(final String pathToModel)  {

    try {
      return parser.parse(pathToModel).get();
    }
    catch (final IOException e) {
      throw new RuntimeException("Cannot parse the NESTML model: " + pathToModel, e);
    }

  }

  protected void printModelToFile(
      final ASTNESTMLCompilationUnit root,
      final String outputModelFile) {
    final NESTMLPrettyPrinter prettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    root.accept(prettyPrinter);

    final File prettyPrintedModelFile = new File(outputModelFile);
    try {
      FileUtils.write(prettyPrintedModelFile, prettyPrinter.getResult());
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot write the prettyprinted model to the file: " + outputModelFile, e);
    }
  }

  protected List<Path> getSPLFilesFromFolder(Path testModelPath) throws IOException {
    final List<Path> filenames = Lists.newArrayList();
    Files.walkFileTree(testModelPath, new SimpleFileVisitor<Path>() {
      @Override
      public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
        if (Files.isRegularFile(file) &&
            file.getFileName().toString().endsWith(SPLLanguage.FILE_ENDING)) {

          filenames.add(file);
        }
        return FileVisitResult.CONTINUE;
      }
    });
    return filenames;
  }
}
