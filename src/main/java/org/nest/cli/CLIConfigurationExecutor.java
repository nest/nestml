/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.cli;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.NESTGenerator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLLanguage;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.utils.FileHelper;
import org.nest.utils.LogHelper;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.nio.file.PathMatcher;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static java.nio.file.FileSystems.*;

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

  public void execute(
      final NESTGenerator generator,
      final Configuration config) {

    final List<Path> modelFilenames = collectNESTMLModelFilenames(config.getInputBase());
    final NESTMLParser parser =  new NESTMLParser(config.getInputBase());
    final List<ASTNESTMLCompilationUnit> modelRoots = parseModels(modelFilenames, parser);
    final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(config.getInputBase());

    processNestmlModels(modelRoots, config, scopeCreator, generator);
  }

  private List<ASTNESTMLCompilationUnit> parseModels(
      final List<Path> nestmlModelFiles,
      final NESTMLParser parser) {
    final List<ASTNESTMLCompilationUnit> modelRoots = Lists.newArrayList();
    for (final Path modelFile:nestmlModelFiles) {
      try {
        final Optional<ASTNESTMLCompilationUnit> root = parser.parse(modelFile.toString());
        if (root.isPresent()) {
          modelRoots.add(root.get());
        }
        else {
          Log.warn("Cannot parse the model " + modelFile.toString() + " due to parser errors.");
        }

      }
      catch (IOException e) {
        Log.warn("Cannot parse the model: " + modelFile.toString(), e);
      }

    }

    return modelRoots;
  }

  public List<Path> collectNESTMLModelFilenames(final Path path) {
    final PathMatcher matcher = getDefault().getPathMatcher("glob:*." + NESTMLLanguage.FILE_ENDING);
    return FileHelper.collectModelFilenames(path, modelFile -> matcher.matches(modelFile.getFileName()));
  }

  private void processNestmlModels(
      final List<ASTNESTMLCompilationUnit> modelRoots,
      final Configuration config,
      final NESTMLScopeCreator scopeCreator,
      final NESTGenerator generator) {

    modelRoots.forEach(scopeCreator::runSymbolTableCreator);

    if (config.isCheckCoCos()) {
      Log.info("Checks context conditions.", LOG_NAME);
      modelRoots.forEach(this::checkCocosForModel);
    }

    for (final ASTNESTMLCompilationUnit root:modelRoots) {
      Log.info("Begins codegeneration for the model: " + root.getFullName(), LOG_NAME);
      generator.analyseAndGenerate(root, config.getTargetPath());
    }

    final String modelName = config.getInputBase().getFileName().toString();
    generator.generateNESTModuleCode(modelRoots, modelName, config.getTargetPath());

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
