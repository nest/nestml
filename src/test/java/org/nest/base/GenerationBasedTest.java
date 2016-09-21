/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.base;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.junit.Before;
import org.nest.codegeneration.NestCodeGenerator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.utils.FilesHelper;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * Base class for the NEST generator tests. Provides the methods to generate header, cpp
 * implementation and boostraping.
 *
 * @author plotnikov
 */
public abstract class GenerationBasedTest extends ModelbasedTest {

  protected static final String MODULE_NAME = "integration";
  protected final Path CODE_GEN_OUTPUT = Paths.get(OUTPUT_FOLDER.toString(), MODULE_NAME);
  private final NestCodeGenerator generator = new NestCodeGenerator(scopeCreator);
  private final NESTMLCoCosManager checker = new NESTMLCoCosManager();

  @Before
  public void cleanUpGeneratedFolder() {
    Log.enableFailQuick(false);
    FilesHelper.deleteFilesInFolder(CODE_GEN_OUTPUT);
  }

  protected void invokeCodeGenerator(final String pathToModel) {
    final ASTNESTMLCompilationUnit root = parseAndBuildSymboltable(pathToModel);
    generator.analyseAndGenerate(root, CODE_GEN_OUTPUT);
  }

  protected void generateNESTModuleCode(final List<ASTNESTMLCompilationUnit> modelRoots) {
    generator.generateNESTModuleCode(modelRoots, MODULE_NAME, CODE_GEN_OUTPUT);
  }

  protected void checkCocos(final String pathToModel) {
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = parser.parse(pathToModel);
      assertTrue(root.isPresent());

      scopeCreator.runSymbolTableCreator(root.get());
      List<Finding> findings = checker.analyzeModel(root.get());
      long errorsFound = findings
          .stream()
          .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
          .count();

      assertEquals("Model " + pathToModel + " contain unexpected errors: " + errorsFound, 0, errorsFound);

    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

}
