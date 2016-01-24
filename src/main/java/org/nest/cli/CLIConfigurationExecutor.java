/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.cli;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.utils.LogHelper;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
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

  public CLIConfigurationExecutor() {
    Log.enableFailQuick(false);
  }

  public boolean execute(final NESTMLToolConfiguration nestmlToolConfiguration) {
    List<String> nestmlModelFilenames = collectNestmlModelFilenames(nestmlToolConfiguration.getInputBasePath());
    handleCollectedModels(nestmlModelFilenames, nestmlToolConfiguration);

    return true;
  }

  private List<String> collectNestmlModelFilenames(final String inputPath) {
    List<String> filenames = Lists.newArrayList();
    try {
      Files.list(new File(inputPath).toPath())
          .filter(file -> !Files.isDirectory(file))
          .forEach(file -> filenames.add(file.getFileName().toString()));
    }
    catch (IOException e) {
      final String msg = "There is a problem to process NESTML models in the folder:  " + inputPath;
      Log.error(msg, e);
      throw new RuntimeException(msg, e);
    }
    Log.info("NESTML models found: #" + filenames.size(), LOG_NAME);
    return filenames;
  }

  private void handleCollectedModels(
      final List<String> nestmlModelFilenames,
      final NESTMLToolConfiguration nestmlToolConfiguration) {
    for (final String modelName:nestmlModelFilenames) {
      handleSingleModel(modelName, nestmlToolConfiguration);
    }

  }

  private void handleSingleModel(final String modelName, final NESTMLToolConfiguration nestmlToolConfiguration) {
    parseWithOptionalCocosCheck(modelName, nestmlToolConfiguration);
    Log.info("Processed model: " + modelName, LOG_NAME);
  }

  private boolean parseWithOptionalCocosCheck(final String modelName, final NESTMLToolConfiguration nestmlToolConfiguration) {
    final NESTMLParser parser = new NESTMLParser(
        Paths.get(nestmlToolConfiguration.getInputBasePath()));
    try {
      final Optional<ASTNESTMLCompilationUnit> root = parser.parse(
          Paths.get(nestmlToolConfiguration.getInputBasePath(), modelName).toString());

      if (root.isPresent()) {
        if (nestmlToolConfiguration.isCheckCoCos()) {
          final List<Finding> error = checkCocosForModel(modelName, nestmlToolConfiguration, root);
          return error.isEmpty();

        } else {
          return true;
        }

      }
      else {
        Log.error("There is a problem with the model: " + modelName + ". It will be skipped.");
        return false;
      }

    }
    catch (IOException e) {
      Log.error("Skips the procession of the model: " + modelName, e);
      return false;
    }

  }

  private List<Finding> checkCocosForModel(
      final String modelName,
      final NESTMLToolConfiguration toolConfiguration,
      final Optional<ASTNESTMLCompilationUnit> root) {
    final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(
        toolConfiguration.getInputBasePath());

    scopeCreator.runSymbolTableCreator(root.get());

    final NESTMLCoCosManager nestmlCoCosManager = new NESTMLCoCosManager();

    final NESTMLCoCoChecker cocosChecker = nestmlCoCosManager.createDefaultChecker();

    checkNESTMLCocos(root, cocosChecker);
    final List<Finding> errors = Lists.newArrayList();
    errors.addAll(LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings()));
    errors.addAll(LogHelper.getErrorsByPrefix("SPL_", Log.getFindings()));

    evaluateCocosLog(modelName, LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings()));
    evaluateCocosLog(modelName, LogHelper.getErrorsByPrefix("SPL_", Log.getFindings()));
    return errors;
  }

  private void checkNESTMLCocos(Optional<ASTNESTMLCompilationUnit> root, NESTMLCoCoChecker cocosChecker) {
    Log.getFindings().clear();
    cocosChecker.checkAll(root.get());
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
