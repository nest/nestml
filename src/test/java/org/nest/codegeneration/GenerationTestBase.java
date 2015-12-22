/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.ModelTestBase;
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
  protected final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(
      TEST_MODEL_PATH, typesFactory);
  protected final NESTML2NESTCodeGenerator generator = new NESTML2NESTCodeGenerator(
      typesFactory, scopeCreator);

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

  public void checkCocos(String pathToModel) {
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(pathToModel);
      assertTrue(root.isPresent());

      scopeCreator.runSymbolTableCreator(root.get());
      final NESTMLCoCoChecker checker
          = new NESTMLCoCosManager(root.get(), scopeCreator.getTypesFactory()).
          createNESTMLCheckerWithSPLCocos();
      checker.checkAll(root.get());

      Collection<Finding> errorFindings = getErrorsByPrefix("NESTML_", Log.getFindings());
      errorFindings.addAll(getErrorsByPrefix("SPL_", Log.getFindings()));

      errorFindings.forEach(System.out::println);
      // TODO reactivate me
      assertTrue("Models contain unexpected errors: " + errorFindings.size(),
          errorFindings.isEmpty());

    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

}
