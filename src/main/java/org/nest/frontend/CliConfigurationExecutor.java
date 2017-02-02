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
import org.apache.commons.io.FilenameUtils;
import org.nest.codegeneration.NestCodeGenerator;
import org.nest.codegeneration.sympy.TransformerBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml._symboltable.NestmlCoCosManager;
import org.nest.utils.FilesHelper;
import org.nest.utils.LogHelper;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;
import static org.nest.utils.FilesHelper.collectNESTMLModelFilenames;

/**
 * Interprets the provided configuration by collecting models and executing parsing, context
 * conditions checks, and code generation.
 *
 * @author plotnikov
 */
public class CliConfigurationExecutor {

  private static final String LOG_NAME = CliConfigurationExecutor.class.getName();
  private final NestmlCoCosManager checker = new NestmlCoCosManager();
  private final Reporter reporter = Reporter.get();

  public CliConfigurationExecutor() {
    Log.enableFailQuick(false); // otherwise the processing is stopped after encountering first error
  }

  void execute(final NestCodeGenerator generator, final CliConfiguration config) {
    final NESTMLParser parser =  new NESTMLParser(config.getModelPath());
    final List<Path> modelFilenames = collectNESTMLModelFilenames(config.getModelPath());
    final List<ASTNESTMLCompilationUnit> modelRoots = parseModels(modelFilenames, parser);

    if (!modelRoots.isEmpty()) {
      final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(config.getModelPath());
      reporter.reportProgress("Finished parsing nestml mdoels...");
      reporter.reportProgress("Remove temporary files...");
      cleanUpWorkingFolder(config.getTargetPath());

      processNestmlModels(modelRoots, config, scopeCreator, generator);

      reporter.reportProgress("Format generated code...");
      formatGeneratedCode(config.getTargetPath());

    }

    reporter.printReports(System.out, System.out);
  }

  private List<ASTNESTMLCompilationUnit> parseModels(
      final List<Path> nestmlModelFiles,
      final NESTMLParser parser) {
    final List<ASTNESTMLCompilationUnit> modelRoots = Lists.newArrayList();
    boolean isError = false;
    for (final Path modelFile:nestmlModelFiles) {
      try {
        final Optional<ASTNESTMLCompilationUnit> root = parser.parse(modelFile.toString());

        if (root.isPresent()) {
          modelRoots.add(root.get());
          reporter.addArtifactInfo(
              FilenameUtils.removeExtension(modelFile.getFileName().toString()),
              "The artifact was parsed successfully.",
              Reporter.Level.INFO);
        }
        else {
          final String errorMsg = Log.getFindings()
              .stream()
              .map(error -> "<" + error.getSourcePosition() + ">: " + error.getMsg()).collect(joining(";"));
          reporter.addArtifactInfo(
              FilenameUtils.removeExtension(modelFile.getFileName().toString()),
              "The artifact is unparsable: " + errorMsg,
              Reporter.Level.ERROR);
          Log.getFindings().clear();
          isError = true;
        }

      }
      catch (IOException e) {
        final String errorMsg = Log.getFindings()
            .stream()
            .map(error -> "<" + error.getSourcePosition() + ">: " + error.getMsg()).collect(joining(";"));
        reporter.addArtifactInfo(
            FilenameUtils.removeExtension(modelFile.getFileName().toString()),
            "The artifact is unparsable: " + errorMsg,
            Reporter.Level.ERROR);
        isError = true;
      }

    }
    if (!isError) {
      return modelRoots;
    }
    else {
      return Lists.newArrayList();
    }

  }

  private void cleanUpWorkingFolder(final Path targetPath) {
    FilesHelper.deleteFilesInFolder(targetPath, file -> file.endsWith(".tmp") || file.endsWith(".nestml"));
  }

  private void processNestmlModels(
      final List<ASTNESTMLCompilationUnit> modelRoots,
      final CliConfiguration config,
      final NESTMLScopeCreator scopeCreator,
      final NestCodeGenerator generator) {

    for (ASTNESTMLCompilationUnit modelRoot:modelRoots) {

      scopeCreator.runSymbolTableCreator(modelRoot);
      final Collection<Finding> symbolTableFindings = LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings());
      symbolTableFindings.addAll(LogHelper.getErrorsByPrefix("SPL_", Log.getFindings()));

      if (symbolTableFindings.isEmpty()) {
        reporter.addArtifactInfo(modelRoot.getArtifactName(), "Successfully built the symboltable.", Reporter.Level.INFO);
      } else {
        reporter.addArtifactInfo(modelRoot.getArtifactName(), "Cannot built the symboltable.", Reporter.Level.INFO);
      }
      final Collection<Finding> symbolTableWarnings = LogHelper.getWarningsByPrefix("NESTML_", Log.getFindings());
      symbolTableWarnings.addAll(LogHelper.getWarningsByPrefix("SPL_", Log.getFindings()));
      symbolTableWarnings.forEach(warning -> reporter.addArtifactInfo(modelRoot.getArtifactName(), warning.getMsg(), Reporter.Level.WARNING));
    }

    final Collection<Finding> symbolTableFindings = LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings());
    symbolTableFindings.addAll(LogHelper.getErrorsByPrefix("SPL_", Log.getFindings()));

    if (symbolTableFindings.isEmpty() && checkModels(modelRoots)) {
      if (config.isCodegeneration()) {
        generateNeuronCode(modelRoots, config, generator);
        generateModuleCode(modelRoots, config, generator);
      }
      else {
        final String msg = "Codegeneration was disabled though the '--dry-run option'.";
        reporter.addSystemInfo(msg, Reporter.Level.INFO);
      }
    }
    else {
      final String msg = " Models contain semantic error(s), therefore, no codegeneration is possible";
      reporter.addSystemInfo(msg, Reporter.Level.ERROR);
    }

  }

  private void generateModuleCode(List<ASTNESTMLCompilationUnit> modelRoots, CliConfiguration config, NestCodeGenerator generator) {
    if (modelRoots.size() > 0) {
      generator.generateNESTModuleCode(modelRoots, config.getModuleName(), config.getTargetPath());
    }
    else {
      reporter.reportProgress("Cannot generate module code, since there is no parsable neuron in " + config.getModelPath());
    }

  }

  private void generateNeuronCode(List<ASTNESTMLCompilationUnit> modelRoots, CliConfiguration config, NestCodeGenerator generator) {
    for (final ASTNESTMLCompilationUnit root:modelRoots) {
      reporter.reportProgress("Generate NEST code from the artifact: " + root.getFullName() + "...");
      generator.analyseAndGenerate(root, config.getTargetPath());
      checkGeneratedCode(root, config.getTargetPath());
    }

  }

  private void checkGeneratedCode(final ASTNESTMLCompilationUnit root, final Path targetPath) {
    for (final ASTNeuron astNeuron:root.getNeurons()) {
      if (Files.exists(Paths.get(targetPath.toString(), astNeuron.getName() + "." + TransformerBase.SOLVER_TYPE))) {

        final String msg = "NEST code for the neuron: " + astNeuron.getName() + " in " + root.getFullName() +
                           " was generated.";
        reporter.addArtifactInfo(root.getArtifactName(), msg, Reporter.Level.INFO);
      } else {

        final String msg = "NEST code for the neuron: " + astNeuron.getName() + " in " + root.getFullName() +
                           " wasn't generated.";
        reporter.addArtifactInfo(root.getArtifactName(), msg, Reporter.Level.ERROR);
      }
    }

  }

  private boolean checkModels(List<ASTNESTMLCompilationUnit> modelRoots) {
    boolean anyError = false;
    final Map<String, List<Finding>> findingsToModel = Maps.newHashMap();

    reporter.reportProgress("Check context conditions...");
    for (ASTNESTMLCompilationUnit root:modelRoots) {
      Log.getFindings().clear(); // clear it to determine which errors are produced through the current model

      final List<Finding> modelFindings = checker.analyzeModel(root);
      findingsToModel.put(root.getArtifactName(), modelFindings);

      if (findingsToModel.get(root.getArtifactName()).stream().anyMatch(Finding::isError)) {
        anyError = true;
      }
      reporter.addArtifactFindings(root.getArtifactName(), modelFindings);

    }

    return !anyError;
  }

  private List<String> getListFromStream(final InputStream inputStream) throws IOException {
    final BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
    return in.lines().collect(toList());
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
      reporter.addSystemInfo("Formatted generates sources in: " + targetPath.toString(), Reporter.Level.INFO);
    }
    catch (IOException | InterruptedException e) {
      reporter.addSystemInfo("Formatted generates sources in: " + targetPath.toString(), Reporter.Level.INFO);
    }

  }

}
