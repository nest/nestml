/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.base;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.base.ModelTestBase;
import org.nest.codegeneration.NESTCodeGenerator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLScopeCreator;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.Optional;

import static org.junit.Assert.assertTrue;
import static org.nest.utils.LogHelper.getErrorsByPrefix;

/**
 * Base class for the NEST generator tests. Provides the methods to generate header, cpp
 * implementation and boostraping.
 *
 * @author plotnikov
 */
public abstract class GenerationTestBase extends ModelTestBase {
  final NESTMLParser p = new NESTMLParser();
  protected final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH);
  protected final NESTCodeGenerator generator = new NESTCodeGenerator(scopeCreator);

  protected void invokeCodeGenerator(final String pathToModel) {

    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(pathToModel);
      assertTrue(root.isPresent());
      scopeCreator.runSymbolTableCreator(root.get());

      generator.analyseAndGenerate(root.get(), Paths.get(OUTPUT_FOLDER));
    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

  protected void generateNESTMLImplementation(final String pathToModel) {
    try {
      final Optional<ASTNESTMLCompilationUnit> root = p.parse(pathToModel);
      assertTrue(root.isPresent());
      scopeCreator.runSymbolTableCreator(root.get());
      generator.analyseAndGenerate(root.get(), Paths.get(OUTPUT_FOLDER));
    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

  public void checkCocos(final String pathToModel) {
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(pathToModel);
      assertTrue(root.isPresent());

      scopeCreator.runSymbolTableCreator(root.get());
      final NESTMLCoCoChecker checker = new NESTMLCoCosManager().createNESTMLCheckerWithSPLCocos();
      checker.checkAll(root.get());

      Collection<Finding> errorFindings = getErrorsByPrefix("NESTML_", Log.getFindings());
      errorFindings.addAll(getErrorsByPrefix("SPL_", Log.getFindings()));

      assertTrue("Models contain unexpected errors: " + errorFindings.size(),
          errorFindings.isEmpty());

    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

}
