/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.frontend;

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
import java.nio.file.Path;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static org.nest.utils.FileHelper.collectNESTMLModelFilenames;

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
    Log.enableFailQuick(false); // otherwise the processing is stopped after encountering first error
  }

  public void execute(final NESTCodeGenerator generator, final CLIConfiguration config) {
    final NESTMLParser parser =  new NESTMLParser(config.getInputBase());
    final List<Path> modelFilenames = collectNESTMLModelFilenames(config.getInputBase());
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

  private void processNestmlModels(
      final List<ASTNESTMLCompilationUnit> modelRoots,
      final CLIConfiguration config,
      final NESTMLScopeCreator scopeCreator,
      final NESTCodeGenerator generator) {

    modelRoots.forEach(scopeCreator::runSymbolTableCreator);

    if (config.isCheckCoCos()) {
      Log.info("Checks context conditions.", LOG_NAME);
      modelRoots.forEach(this::checkCocosForModel);
    }

    for (final ASTNESTMLCompilationUnit root:modelRoots) {
      Log.info("Begins codegeneration for the model: " + root.getFullName(), LOG_NAME);
      generator.analyseAndGenerate(root, config.getTargetPath());
    }

    if (modelRoots.size() > 0) {
      final String modelName = config.getInputBase().getFileName().toString();
      generator.generateNESTModuleCode(modelRoots, modelName, config.getTargetPath());
    }
    else {
      Log.warn("Cannot generate module code, since there is no parsable neuron in " + config.getInputBase());
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
        "NESTML",
        LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings()));
    evaluateCocosLog(
        root.getFullName(),
        "SPL",
        LogHelper.getErrorsByPrefix("SPL_", Log.getFindings()));
    return errors;
  }

  private void checkNESTMLCocos(ASTNESTMLCompilationUnit root, NESTMLCoCoChecker cocosChecker) {
    Log.getFindings().clear();
    cocosChecker.checkAll(root);
  }

  private void evaluateCocosLog(
      final String modelName,
      final String errorClass,
      final Collection<Finding> nestmlErrorFindings) {
    if (nestmlErrorFindings.isEmpty()) {
      Log.info(modelName + " contains no '" +  errorClass + "' errors", LOG_NAME);
    } else {
      Log.error(modelName + " contains the following errors: ");
      nestmlErrorFindings.forEach(finding -> Log.warn(finding.toString()));
    }
  }

}
