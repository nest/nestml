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
import groovyjarjarantlr.collections.AST;
import org.nest.codegeneration.NestCodeGenerator;
import org.nest.codegeneration.sympy.TransformerBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._ast.ASTNESTMLCompilationUnitTOP;
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
        reporter.reportProgress(modelRoot.getArtifactName() + ": Successfully built the symboltable.");
      } else {
        reporter.reportProgress(modelRoot.getArtifactName() + ": Cannot built the symboltable.");
      }
      final Collection<Finding> symbolTableWarnings = LogHelper.getWarningsByPrefix("NESTML_", Log.getFindings());

      symbolTableWarnings.addAll(LogHelper.getWarningsByPrefix("SPL_", Log.getFindings()));

      for (Finding warning:symbolTableWarnings) {
        if (!warning.getSourcePosition().isPresent()) {
          System.out.printf("");
        }

      }
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
    }
    else {
      reporter.reportProgress("Cannot generate module code, since there is no parsable neuron in " + config.getModelPath());
    }

  }

  private void generateNeuronCode(List<ASTNESTMLCompilationUnit> modelRoots, CliConfiguration config, NestCodeGenerator generator) {
    for (final ASTNESTMLCompilationUnit root:modelRoots) {
      reporter.reportProgress("Generate NEST code from the artifact: " + root.getFullName());
      generator.analyseAndGenerate(root, config.getTargetPath());
      checkGeneratedCode(root, config.getTargetPath());
    }

  }

  private void checkGeneratedCode(final ASTNESTMLCompilationUnit root, final Path targetPath) {
    for (final ASTNeuron astNeuron:root.getNeurons()) {
      if (Files.exists(Paths.get(targetPath.toString(), astNeuron.getName() + "." + TransformerBase.SOLVER_TYPE))) {

        final String msg = "NEST code for the neuron: " + astNeuron.getName() + " from file: " + root.getFullName() +
                           " was generated.";
        reporter.reportProgress(root.getArtifactName() + ": " + msg);

      } else {
        final String msg = "NEST code for the neuron: " + astNeuron.getName() + " in " + root.getFullName() +
                           " wasn't generated.";
        reporter.reportProgress(root.getArtifactName() + ":" + msg);

      }

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
