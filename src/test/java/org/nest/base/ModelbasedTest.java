/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.base;

import de.se_rwth.commons.logging.Log;
import org.apache.commons.io.FileUtils;
import org.junit.Before;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Disables exit on error and provides base services for parsing and symbol table.
 *
 * @author plotnikov
 */
public class ModelbasedTest {
  protected static final Path OUTPUT_FOLDER = Paths.get("target");
  protected static final Path TEST_MODEL_PATH = Paths.get("models");
  protected final NESTMLParser parser = new NESTMLParser();
  protected final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator();


  @Before
  public void clearLog() {
    Log.enableFailQuick(false);
    Log.getFindings().clear();
  }

  protected ASTNESTMLCompilationUnit parseNestmlModel(final String pathToModel)  {

    try {
      return parser.parse(pathToModel).get();
    }
    catch (final IOException e) {
      throw new RuntimeException("Cannot parse the NESTML model: " + pathToModel, e);
    }

  }

  protected ASTNESTMLCompilationUnit parseAndBuildSymboltable(final String pathToModel) {
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = parser.parse(pathToModel);
      assertTrue(root.isPresent());
      scopeCreator.runSymbolTableCreator(root.get());
      return root.get();
    }
    catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected void printModelToFile(
      final ASTNESTMLCompilationUnit root,
      final String outputModelFile) {

    final File prettyPrintedModelFile = new File(outputModelFile);
    try {
      FileUtils.write(prettyPrintedModelFile, NESTMLPrettyPrinter.print(root));
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot write the prettyprinted model to the file: " + outputModelFile, e);
    }
  }
  
}
