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
import org.nest.codegeneration.NestCodeGenerator;
import org.nest.codegeneration.sympy.TransformerBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.nestml._symboltable.NestmlCoCosManager;
import org.nest.reporting.Reporter;
import org.nest.utils.FilesHelper;
import org.nest.utils.LogHelper;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static java.util.stream.Collectors.toList;
import static org.nest.utils.FilesHelper.collectNESTMLModelFilenames;

/**
 * Interprets the provided configuration by collecting models and executing parsing, context
 * conditions checks, and code generation.
 *
 * @author plotnikov
 */
class CliConfigurationExecutor {

  private static final String LOG_NAME = CliConfigurationExecutor.class.getName();
  private final NestmlCoCosManager checker = new NestmlCoCosManager();
  private final Reporter reporter = Reporter.get();

  public CliConfigurationExecutor() {
    Log.enableFailQuick(false); // otherwise the processing is stopped after encountering first error
  }

  void execute(final NestCodeGenerator generator, final CliConfiguration config) {
    final NESTMLParser parser =  new NESTMLParser();
    final List<Path> modelFilenames = collectNESTMLModelFilenames(config.getInputPath());
    final List<ASTNESTMLCompilationUnit> modelRoots = parseModels(modelFilenames, parser);

    reporter.reportProgress("Finished parsing nestml mdoels...");

    if (!modelRoots.isEmpty()) {
      final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator();
      if (!Files.exists(config.getTargetPath())) {
        try {
          Files.createDirectories(config.getTargetPath());
        }
        catch (IOException e) {
          Log.error("Cannot create the output foder: " + config.getTargetPath().toString(), e);
        }
      }

      cleanUpWorkingFolder(config.getTargetPath());

      processNestmlModels(modelRoots, config, scopeCreator, generator);

      reporter.reportProgress("Format generated code...");
      formatGeneratedCode(config.getTargetPath());

    }

    reporter.printReports(System.out, System.out);
    if (!config.getJsonLogFile().isEmpty()) {
      final Path logFile = Paths.get(config.getTargetPath().toString(), config.getJsonLogFile());
      try (BufferedWriter writer = Files.newBufferedWriter(logFile)) {
        writer.write(reporter.printFindingsAsJsonString());
      }
      catch (IOException e) {
        Log.error("Cannot write JSON log", e);
      }

    }

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
          reporter.reportProgress("The NESTML file was parsed successfully: " + modelFile.getFileName().toString());
        }
        else {
          final Optional<Finding> parserError = Log.getFindings()
              .stream()
              .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
              .findAny();

          reportParserError(modelFile, parserError);
          Log.getFindings().clear();
          isError = true;
        }

      }
      catch (IOException e) {
        final Optional<Finding> parserError = Log.getFindings()
            .stream()
            .filter(finding -> finding.getType().equals(Finding.Type.ERROR))
            .findAny();

        reportParserError(modelFile, parserError);
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

  private void reportParserError(Path modelFile, Optional<Finding> parserError) {
    reporter.addNeuronReport(
        modelFile.getFileName().toString(), // TODO: is it a good idea?
        "",
        Reporter.Level.ERROR,
        "NESTML_PARSER",
        parserError.map(finding -> finding.getSourcePosition().get().getLine()).orElse(0),
        parserError.map(finding -> finding.getSourcePosition().get().getColumn()).orElse(0),
        parserError.map(Finding::getMsg).orElse("Cannot parse the NESTML-file"));
  }

  private void cleanUpWorkingFolder(final Path targetPath) {
    FilesHelper.deleteFilesInFolder(targetPath, file -> file.toString().endsWith(".tmp"));
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

      symbolTableFindings.forEach(warning -> reporter.addNeuronReport(
          modelRoot.getFilename(),
          modelRoot.getNeuronNameAtLine(warning.getSourcePosition()),
          warning));

      if (symbolTableFindings.isEmpty()) {
        reporter.reportProgress(modelRoot.getArtifactName() + ": Successfully built the symboltable.");
      } else {
        reporter.reportProgress(modelRoot.getArtifactName() + ": Cannot built the symboltable.", Reporter.Level.ERROR);
      }
      final Collection<Finding> symbolTableWarnings = LogHelper.getWarningsByPrefix("NESTML_", Log.getFindings());

      symbolTableWarnings.forEach(warning -> reporter.addNeuronReport(
          modelRoot.getFilename(),
          modelRoot.getNeuronNameAtLine(warning.getSourcePosition().get().getLine()),
          warning));
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
        reporter.reportProgress(msg);
      }
    }
    else {
      final String msg = " Models contain semantic error(s), therefore, no codegeneration is possible";
      reporter.reportProgress(msg);
    }

  }


  private void generateModuleCode(List<ASTNESTMLCompilationUnit> modelRoots, CliConfiguration config, NestCodeGenerator generator) {
    if (modelRoots.size() > 0) {
      generator.generateNESTModuleCode(modelRoots, config.getModuleName(), config.getTargetPath());
      reporter.reportProgress(String.format("Generated NEST module: %s", config.getModuleName()));
    }
    else {
      reporter.reportProgress("Cannot generate module code, since there is no parsable neuron in " + config.getInputPath());
    }

  }

  private void generateNeuronCode(List<ASTNESTMLCompilationUnit> modelRoots, CliConfiguration config, NestCodeGenerator generator) {
    for (final ASTNESTMLCompilationUnit root:modelRoots) {
      reporter.reportProgress("Generate NEST code from the artifact: " + root.getArtifactName());
      generator.analyseAndGenerate(root, config.getTargetPath());
    }

  }

  /**
   *
   * @param modelRoots List with root nodes of NESTML files from the model path
   * @return true iff. there is no errors in neurons
   */
  private boolean checkModels(List<ASTNESTMLCompilationUnit> modelRoots) {
    boolean anyError = false;
    final Map<String, List<Finding>> findingsToModel = Maps.newHashMap();

    reporter.reportProgress("Check context conditions...");

    for (final ASTNESTMLCompilationUnit root:modelRoots) {
      for (ASTNeuron neuron:root.getNeurons()) {
        Log.getFindings().clear(); // clear it to determine which errors are produced through the current model

        final List<Finding> modelFindings = checker.analyzeModel(root);
        findingsToModel.put(root.getArtifactName(), modelFindings);

        if (findingsToModel.get(root.getArtifactName()).stream().anyMatch(Finding::isError)) {
          anyError = true;
        }
        reporter.addNeuronReports(root.getFilename(), neuron.getName(), modelFindings);

      }

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
      getListFromStream(res.getErrorStream()).forEach(m -> Log.trace("Error: " + m, LOG_NAME));
      reporter.reportProgress("Formatted generates sources in: " + targetPath.toString());
    }
    catch (IOException | InterruptedException e) {
      reporter.reportProgress("Cannot format source files located in: " + targetPath.toString());
      e.printStackTrace();
    }

  }

}
