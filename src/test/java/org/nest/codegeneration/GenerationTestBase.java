/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.ModelTestBase;
import org.nest.codegeneration.converters.NESTReferenceConverter;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;

import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.Optional;

import static org.junit.Assert.assertTrue;
import static org.nest.utils.LogHelper.getErrorsByPrefix;

/**
 * Base class for the NEST generator tests.
 * Provides the methods to generate header, cpp implementation and boostraping.
 *
 * @author plotnikov
 */
public abstract class GenerationTestBase extends ModelTestBase {

  protected void generateHeader(final String modelPath) {
    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory
        .createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(modelPath);
      assertTrue(root.isPresent());
      scopeCreator.runSymbolTableCreator(root.get());
      final File outputFolder = new File(OUTPUT_FOLDER);

      NESTML2NESTCodeGenerator.generateHeader(glex, root.get(),
          scopeCreator.getTypesFactory(), outputFolder);
    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

  protected void generateClassImplementation(final String MODEL_FILE_PATH) {
    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory.createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(MODEL_FILE_PATH);

      assertTrue(root.isPresent());

      scopeCreator.runSymbolTableCreator(root.get());

      final File outputFolder = new File(OUTPUT_FOLDER);

      NESTML2NESTCodeGenerator.generateClassImplementation(glex,
          scopeCreator.getTypesFactory(), root.get(), outputFolder);
    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

  protected void generateCodeForModelIntegrationInNest(final String modelFile) {
    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory.createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(modelFile);
      assertTrue(root.isPresent());

      scopeCreator.runSymbolTableCreator(root.get());

      final File outputFolder = new File(OUTPUT_FOLDER);

      NESTML2NESTCodeGenerator.generateCodeForModelIntegrationInNest(glex, root.get(), outputFolder);
    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

  protected void generateCodeForNESTMLWithODE(final String modelFilePath) {
    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory.createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(modelFilePath);

      assertTrue(root.isPresent());

      scopeCreator.runSymbolTableCreator(root.get());

      final File outputFolder = new File(OUTPUT_FOLDER);
      final ASTNESTMLCompilationUnit explicitSolutionRoot =
          NESTML2NESTCodeGenerator.transformOdeToSolution(
              root.get(),
              scopeCreator,
              outputFolder);
      NESTML2NESTCodeGenerator.generateClassImplementation(
          glex,
          scopeCreator.getTypesFactory(),
          explicitSolutionRoot,
          outputFolder);
      NESTML2NESTCodeGenerator.generateHeader(
          glex,
          explicitSolutionRoot,
          scopeCreator.getTypesFactory(),
          outputFolder);
      NESTML2NESTCodeGenerator.generateClassImplementation(
          glex,
          scopeCreator.getTypesFactory(),
          explicitSolutionRoot,
          outputFolder);
    }
    catch (IOException e) { // lambda functions doesn't support checked exceptions
      throw new RuntimeException(e);
    }

  }

  public void checkCocos(String modelFilePath) {
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory.createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(modelFilePath);
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

  protected GlobalExtensionManagement createGLEXConfiguration() {
    final GlobalExtensionManagement glex = new GlobalExtensionManagement();

    final NESTReferenceConverter converter = new NESTReferenceConverter(typesFactory);

    // TODO resolve this circular dependency
    final ExpressionsPrettyPrinter expressionsPrinter = new ExpressionsPrettyPrinter(converter);

    glex.setGlobalValue("expressionsPrinter", expressionsPrinter);
    glex.setGlobalValue("functionCallConverter", converter); // TODO better name
    return glex;
  }
}
