/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.frontend;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.codegeneration.NESTCodeGenerator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.utils.FilesHelper;
import org.nest.utils.LogHelper;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import static de.se_rwth.commons.logging.Log.info;
import static org.nest.utils.FilesHelper.collectNESTMLModelFilenames;

/**
 * Interprets the provided configuration by collecting models and executing parsing, context
 * conditions checks, and code generation.
 *
 * @author plotnikov
 */
public class CLIConfigurationExecutor {

  private static final String LOG_NAME = CLIConfigurationExecutor.class.getName();
  private final NESTMLCoCosManager checker = new NESTMLCoCosManager();

  public CLIConfigurationExecutor() {
    Log.enableFailQuick(false); // otherwise the processing is stopped after encountering first error
  }

  void execute(final NESTCodeGenerator generator, final CLIConfiguration config) {
    final NESTMLParser parser =  new NESTMLParser(config.getInputBase());
    final List<Path> modelFilenames = collectNESTMLModelFilenames(config.getInputBase());
    final List<ASTNESTMLCompilationUnit> modelRoots = parseModels(modelFilenames, parser);
    final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(config.getInputBase());

    cleanUpWorkingFolder(config.getTargetPath());
    processNestmlModels(modelRoots, config, scopeCreator, generator);
    formatGeneratedCode(config.getTargetPath());
  }

  private void cleanUpWorkingFolder(final Path targetPath) {
    FilesHelper.deleteFilesInFolder(targetPath, file -> file.endsWith(".tmp"));
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
    final Collection<Finding> symbolTableFindings = LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings());

    if (symbolTableFindings.isEmpty() && checkModels(modelRoots, config)) {
      generateNeuronCode(modelRoots, config, generator);
      generateModuleCode(modelRoots, config, generator);
    }
    else {
      Log.error(LOG_NAME + ": Models contain semantic errors, therefore, no codegeneration is possible");
    }

  }

  private void generateModuleCode(List<ASTNESTMLCompilationUnit> modelRoots, CLIConfiguration config, NESTCodeGenerator generator) {
    if (modelRoots.size() > 0) {
      final String modelName;
      if (Files.isRegularFile(config.getInputBase())) {
        modelName = config.getInputBase().getName(config.getInputBase().getNameCount() - 2 ).toString();
      }
      else {
        modelName = config.getInputBase().getFileName().toString();
      }
      generator.generateNESTModuleCode(modelRoots, modelName, config.getTargetPath());
    }
    else {
      Log.warn("Cannot generate module code, since there is no parsable neuron in " + config.getInputBase());
    }
  }

  private void generateNeuronCode(List<ASTNESTMLCompilationUnit> modelRoots, CLIConfiguration config, NESTCodeGenerator generator) {
    for (final ASTNESTMLCompilationUnit root:modelRoots) {
      Log.info("Begins codegeneration for the model: " + root.getFullName(), LOG_NAME);
      generator.analyseAndGenerate(root, config.getTargetPath());
    }
  }

  private boolean checkModels(List<ASTNESTMLCompilationUnit> modelRoots, CLIConfiguration config) {
    boolean anyError = false;
    if (config.isCheckCoCos()) {
      final Map<String, List<Finding>> findingsToModel = Maps.newHashMap();

      Log.info("Checks context conditions.", LOG_NAME);
      for (ASTNESTMLCompilationUnit root:modelRoots) {
        findingsToModel.put(root.getFullName(), checker.analyzeModel(root));
        if (findingsToModel.get(root.getFullName()).stream().filter(Finding::isError).findAny().isPresent()) {
          anyError = true;
        }

      }

    }
    return !anyError;
  }

  private List<String> getListFromStream(final InputStream inputStream) throws IOException {
    final BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
    return in.lines().collect(Collectors.toList());
  }

  private void formatGeneratedCode(final Path targetPath) {
    // "/bin/sh", "-c" is necessary because of the wild cards in the clang-format command.
    // otherwise, the command is not evaluated correctly
    final List<String> formatCommand = Lists.newArrayList("/bin/sh", "-c", "clang-format -style=\"{Standard: Cpp03}\"  -i *.cpp *.h");

    try {

      final ProcessBuilder processBuilder = new ProcessBuilder(formatCommand).directory(targetPath.toFile());

      final Process res = processBuilder.start();
      res.waitFor();
      getListFromStream(res.getInputStream()).forEach(m -> Log.trace("Log: " + m, LOG_NAME));
      getListFromStream(res.getErrorStream()).forEach(m -> Log.warn("Error: " + m));
      info("Formatted generates sources in: " + targetPath.toString(), LOG_NAME);
    } catch (IOException | InterruptedException e) {
      Log.warn("Cannot format generated sources in: " + targetPath.toString(), e);
    }

  }

}
