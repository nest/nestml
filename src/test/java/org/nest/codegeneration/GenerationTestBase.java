/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import de.monticore.generating.templateengine.GlobalExtensionManagement;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.apache.commons.io.FileUtils;
import org.nest.ModelTestBase;
import org.nest.codegeneration.converters.NESTReferenceConverter;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinterFactory;
import org.nest.spl.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.symboltable.symbols.NESTMLNeuronSymbol;
import org.nest.symboltable.symbols.NESTMLVariableSymbol;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
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

  protected void generateCodeForNESTMLWithODE(final String modelFilePath) {
    final GlobalExtensionManagement glex = createGLEXConfiguration();
    final NESTMLCompilationUnitMCParser p = NESTMLParserFactory.createNESTMLCompilationUnitMCParser();
    final Optional<ASTNESTMLCompilationUnit> root;
    try {
      root = p.parse(modelFilePath);
      assertTrue(root.isPresent());

      scopeCreator.runSymbolTableCreator(root.get());

      final File outputFolder = new File(OUTPUT_FOLDER);
      ASTNESTMLCompilationUnit explicitSolutionRoot =
          NESTML2NESTCodeGenerator.transformOdeToSolution(
              root.get(),
              scopeCreator,
              outputFolder);
      final Path tmpModelPath = Paths.get(OUTPUT_FOLDER, "tmp.nestml");
      printModelToFile(explicitSolutionRoot, tmpModelPath.toString());
      explicitSolutionRoot = parseNESTMLModel(tmpModelPath.toString());
      final Scope scope = scopeCreator.runSymbolTableCreator(explicitSolutionRoot);

      Optional<NESTMLNeuronSymbol> neuronSymbol = scope.resolve("iaf_neuron_ode_neuron", NESTMLNeuronSymbol.KIND);

      final Optional<NESTMLVariableSymbol> y0 = neuronSymbol.get().getVariableByName("y0");
      assertTrue(y0.isPresent());
      assertTrue(y0.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));

      final Optional<NESTMLVariableSymbol> y1 = neuronSymbol.get().getVariableByName("y1");
      assertTrue(y1.isPresent());
      assertTrue(y1.get().getBlockType().equals(NESTMLVariableSymbol.BlockType.STATE));

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
