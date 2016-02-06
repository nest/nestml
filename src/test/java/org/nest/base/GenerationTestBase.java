/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.base;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.NESTGenerator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._symboltable.NESTMLCoCosManager;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.Optional;

import static com.google.common.collect.Lists.newArrayList;
import static org.junit.Assert.assertTrue;
import static org.nest.utils.LogHelper.getErrorsByPrefix;

/**
 * Base class for the NEST generator tests. Provides the methods to generate header, cpp
 * implementation and boostraping.
 *
 * @author plotnikov
 */
public abstract class GenerationTestBase extends ModelTestBase {
  protected final NESTGenerator generator = new NESTGenerator(scopeCreator);
  private final Path CODE_GEN_OUTPUT = Paths.get(OUTPUT_FOLDER.toString(), "integration");

  protected void invokeCodeGenerator(final String pathToModel) {
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = parser.parse(pathToModel);
      assertTrue(root.isPresent());
      scopeCreator.runSymbolTableCreator(root.get());

      generator.analyseAndGenerate(root.get(), CODE_GEN_OUTPUT);
      generator.generateNESTModuleCode(newArrayList(root.get()), "integration", CODE_GEN_OUTPUT);
    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

  public void checkCocos(final String pathToModel) {
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = parser.parse(pathToModel);
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
