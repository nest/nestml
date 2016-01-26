/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.cli;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.NESTCodeGenerator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.utils.LogHelper;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

/**
 * Interprets the provided configuration by collecting models and executing parsing, context
 * conditions checks, and code generation.
 *
 * @author plotnikov
 */
public class CLIConfigurationExecutor {

  private static final String LOG_NAME = CLIConfigurationExecutor.class.getName();
  final NESTMLCoCosManager nestmlCoCosManager = new NESTMLCoCosManager();

  public CLIConfigurationExecutor() {
    Log.enableFailQuick(false);
  }

  public boolean execute(
      final NESTCodeGenerator generator,
      final NESTMLToolConfiguration configuration) {
    final List<Path> nestmlModelFilenames = collectNESTMLModelFilenames(
        Paths.get(configuration.getInputBasePath()));
    final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(configuration.getInputBasePath());
    handleCollectedModels(nestmlModelFilenames, configuration, scopeCreator, generator);

    return true;
  }

  protected List<Path> collectNESTMLModelFilenames(final Path inputPath) {
    final List<Path> filenames = Lists.newArrayList();
    try {
      Files.walkFileTree(inputPath, new SimpleFileVisitor<Path>() {
        @Override
        public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
          if (Files.isRegularFile(file)) {
            filenames.add(file);
          }
          return FileVisitResult.CONTINUE;
        }
      });
    }
    catch (IOException e) {
      final String msg = "There is a problem to process NESTML models in the folder:  " + inputPath;
      Log.error(msg, e);
      throw new RuntimeException(msg, e);
    }
    return filenames;
  }

  private void handleCollectedModels(
      final List<Path> nestmlModelFiles,
      final NESTMLToolConfiguration configuration,
      final NESTMLScopeCreator scopeCreator,
      final NESTCodeGenerator generator) {
    for (final Path modelFile:nestmlModelFiles) {
      handleSingleModel(modelFile, scopeCreator, generator, configuration);
    }

  }

  private void handleSingleModel(
      final Path modelFile,
      final NESTMLScopeCreator nestmlScopeCreator,
      final NESTCodeGenerator nestCodeGenerator,
      final NESTMLToolConfiguration nestmlToolConfiguration) {
    Log.info("Processed model: " + modelFile, LOG_NAME);
    final NESTMLParser parser =  new NESTMLParser(
        Paths.get(nestmlToolConfiguration.getInputBasePath()));

    try {
      final Optional<ASTNESTMLCompilationUnit> root = parser.parse(modelFile.toString());
      if (root.isPresent()) {
        nestmlScopeCreator.runSymbolTableCreator(root.get());
        checkCocosForModel(root.get());
        nestCodeGenerator.analyseAndGenerate(root.get(), Paths.get(nestmlToolConfiguration.getTargetPath()));
      }

    }
    catch (IOException e) {
      throw new RuntimeException("Cannot parse the model due to parser errors", e);
    }
  }

  private List<Finding> checkCocosForModel(final ASTNESTMLCompilationUnit root) {

    final NESTMLCoCoChecker cocosChecker = nestmlCoCosManager.createDefaultChecker();

    checkNESTMLCocos(root, cocosChecker);
    final List<Finding> errors = Lists.newArrayList();
    errors.addAll(LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings()));
    errors.addAll(LogHelper.getErrorsByPrefix("SPL_", Log.getFindings()));

    evaluateCocosLog(
        root.getFullName(),
        LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings()));
    evaluateCocosLog(
        root.getFullName(),
        LogHelper.getErrorsByPrefix("SPL_", Log.getFindings()));
    return errors;
  }

  private void checkNESTMLCocos(ASTNESTMLCompilationUnit root, NESTMLCoCoChecker cocosChecker) {
    Log.getFindings().clear();
    cocosChecker.checkAll(root);
  }

  private void evaluateCocosLog(String modelName, Collection<Finding> nestmlErrorFindings) {
    if (nestmlErrorFindings.isEmpty()) {
      Log.info(modelName + " contains no errors", LOG_NAME);
    } else {
      Log.error(modelName + " contains the following errors: ");
      nestmlErrorFindings.forEach(finding -> Log.warn(finding.toString()));
    }
  }

}
