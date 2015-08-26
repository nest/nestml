/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.monticore.cocos.CoCoLog;
import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.se_rwth.commons.logging.Log;
import org.junit.Before;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.codegeneration.converters.NESTReferenceConverter;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.utils.LogHelper;

import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Base class for the NEST generator tests.
 * Provides the methods to generate header, cpp implementation and boostraping.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public abstract class GenerationTestBase {

  private static final String OUTPUT_FOLDER = "target";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  private final NESTMLScopeCreator nestmlScopeCreator
      = new NESTMLScopeCreator(getModelPath(), typesFactory); // must be called in order to build the symbol table

  protected abstract String getModelPath();
  @Before
  public void setup() {
    Log.enableFailQuick(false);
    CoCoLog.getFindings().clear();
  }

  protected void generateHeader(final String modelPath) {
    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory
        .createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(modelPath);
      assertTrue(root.isPresent());
      nestmlScopeCreator.runSymbolTableCreator(root.get());
      final File outputFolder = new File(OUTPUT_FOLDER);

      NESTML2NESTCodeGenerator.generateHeader(glex, root.get(),
          nestmlScopeCreator.getTypesFactory(), outputFolder);
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

      nestmlScopeCreator.runSymbolTableCreator(root.get());

      final File outputFolder = new File(OUTPUT_FOLDER);

      NESTML2NESTCodeGenerator.generateClassImplementation(glex,
          nestmlScopeCreator.getTypesFactory(), root.get(), outputFolder);
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

      nestmlScopeCreator.runSymbolTableCreator(root.get());

      final File outputFolder = new File(OUTPUT_FOLDER);

      NESTML2NESTCodeGenerator.generateCodeForModelIntegrationInNest(glex, root.get(), outputFolder);
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

  public void checkCocos(String modelFilePath) {
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory.createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(modelFilePath);
      assertTrue(root.isPresent());

      nestmlScopeCreator.runSymbolTableCreator(root.get());
      final NESTMLCoCoChecker checker
          = new NESTMLCoCosManager(root.get(), nestmlScopeCreator.getTypesFactory()).
          createNESTMLCheckerWithSPLCocos();
      checker.checkAll(root.get());

      Collection<String> errorFindings
          = LogHelper.getFindingsByPrefix("NESTML_", CoCoLog.getFindings());
      errorFindings.addAll(LogHelper.getFindingsByPrefix("SPL_", CoCoLog.getFindings()));
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
