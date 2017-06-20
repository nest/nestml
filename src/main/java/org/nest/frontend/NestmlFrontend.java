/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.frontend;

import com.google.common.base.Joiner;
import de.se_rwth.commons.logging.Log;
import org.apache.commons.cli.*;
import org.nest.codegeneration.NestCodeGenerator;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.utils.FilesHelper;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Handles available options set at the tool invocation. Makes minimal checks of the infrastructure:
 * python, sympy.
 *
 * @author plotnikov
 */
public class NestmlFrontend {
  private final static String LOG_NAME = NestmlFrontend.class.getName();

  private static final String PYTHON_VERSION_TEST_OUTPUT = "pythonVersion.tmp";
  private static final String PYTHON_CHECK_SCRIPT = "pythonChecker.py";
  private static final String PYTHON_CHECK_SCRIPT_SOURCE = "checks/pythonChecker.py";

  private static final String SYMPY_VERSION_TEST_OUTPUT = "sympyVersion.tmp";
  private static final String SYMPY_CHECK_SCRIPT = "sympyChecker.py";
  private static final String SYMPY_CHECK_SCRIPT_SOURCE = "checks/sympyChecker.py";
  private static final String PYTHON_INTERPRETER = "python ";

  // Options
  private static final String HELP_ARGUMENT = "help";
  private static final String ENABLE_TRACING = "enable_tracing";
  private static final String TARGET_OPTION = "target";
  private static final String DRY_RUN_OPTION = "dry-run";
  private static final String JSON_OPTION = "json_log";
  private static final String MODULE_OPTION = "module_name";



  private final Options options = new Options();
  private final HelpFormatter formatter = new HelpFormatter();

  private final static Reporter reporter = Reporter.get();

  public NestmlFrontend() {
    Log.enableFailQuick(false); // otherwise error terminates the java vm

    options.addOption(Option.builder(HELP_ARGUMENT.substring(0, 1))
        .desc("Prints this message.")
        .longOpt(HELP_ARGUMENT)
        .build());

    final String TRACING_DESCRIPTION = "Enables tracing of templates which were used to generate C++ code. " +
                                       "It can be used for debugging purporses.";
    options.addOption(Option.builder(ENABLE_TRACING.substring(0, 1))
        .longOpt(ENABLE_TRACING)
        .desc(TRACING_DESCRIPTION)
        .build());

    final String TARGET_DESCRIPTION = "Defines the path where generated artifacts are stored. The only argument " +
                                      "determines the folder where the generated code is stored. E.g. --" +
                                      TARGET_OPTION + " ~/my_path";
    options.addOption(Option.builder(TARGET_OPTION.substring(0, 1))
        .longOpt(TARGET_OPTION)
        .hasArgs()
        .numberOfArgs(1)
        .desc(TARGET_DESCRIPTION)
        .build());


    options.addOption(Option.builder(DRY_RUN_OPTION.substring(0, 1))
        .longOpt(DRY_RUN_OPTION)
        .desc("Use this option to execute the model analysis only.")
        .build());

    final String JSON_DESCRIPTION = "Defines the name of the file where the model log will be stored in JSON format.";
    options.addOption(Option.builder(JSON_OPTION.substring(0, 1))
        .longOpt(JSON_OPTION)
        .hasArgs()
        .numberOfArgs(1)
        .desc(JSON_DESCRIPTION)
        .build());

    final String MODULE_DESCRIPTION = "Defines the name of nest module which is generated with neuron models. Under this" +
                                      "name the module can be installed in SLI/PyNEST.";
    options.addOption(Option.builder(MODULE_OPTION.substring(0, 1))
        .longOpt(MODULE_OPTION)
        .hasArgs()
        .numberOfArgs(1)
        .desc(MODULE_DESCRIPTION)
        .build());
  }

  public static void main(final String[] args) {
    new NestmlFrontend().start(args);
  }

  public void start(final String[] args) {
    final Optional<CliConfiguration> cliConfiguration = createCLIConfiguration(args);

    if (cliConfiguration.isPresent()) {
      final String inputPathMsg = "The input modelpath: " + cliConfiguration.get().getModelPath().toAbsolutePath().toString();
      reporter.reportProgress(inputPathMsg);

      final String outputPathMsg = "The base output path: " + cliConfiguration.get().getTargetPath().toAbsolutePath().toString();
      reporter.reportProgress(outputPathMsg);

      if (checkEnvironment(cliConfiguration.get())) {
        executeConfiguration(cliConfiguration.get());

      }
      else {
        final String msg = "The execution environment is not installed properly. Execution will be terminated.";
        reporter.reportProgress(msg);
      }
    }

  }

  public Optional<CliConfiguration> createCLIConfiguration(String[] args) {
    if (args.length == 0) {
      printToolUsageHelp();
      return Optional.empty();
    }

    final CommandLine cliParameters = parseCLIArguments(args);

    if (cliParameters.hasOption(HELP_ARGUMENT)) {
      printToolUsageHelp();
    }

    boolean isTracing = false;
    if (cliParameters.hasOption(ENABLE_TRACING)) {
      isTracing = true;
    }

    boolean isCodegeneration = true;
    if (cliParameters.hasOption(DRY_RUN_OPTION)) {
      isCodegeneration = false;
    }

    final String targetPath = getOptionValue(cliParameters, TARGET_OPTION).orElse("build");

    if (cliParameters.getArgs().length != 1) {
      formatter.printHelp("Provide exactly one path to the model folder.", options);
      printToolUsageHelp();
      return Optional.empty();
    }
    final Path modelPath = Paths.get(cliParameters.getArgs()[0]);

    final String moduleName;
    if (cliParameters.hasOption(MODULE_OPTION)) {
      moduleName = cliParameters.getOptionValue(MODULE_OPTION);
    }
    else { // if the module name is not provided than take the name of its first parent
      if (Files.isRegularFile(modelPath)) {
        moduleName = modelPath.getName(modelPath.getNameCount() - 2 ).toString();
      }
      else {
        moduleName = modelPath.getFileName().toString();
      }

    }

    String jsonLogFile;
    if (cliParameters.hasOption(JSON_OPTION)) {
      jsonLogFile = cliParameters.getOptionValue(JSON_OPTION);
      if (!jsonLogFile.endsWith(".log")) {
        jsonLogFile += ".log";
      }
    }
    else { // if the module name is not provided than take the name of its first parent
      jsonLogFile = "";
    }

    return Optional.of(new CliConfiguration
        .Builder()
        .withCodegeneration(isCodegeneration)
        .withModelPath(modelPath)
        .withModuleName(moduleName)
        .withTargetPath(targetPath)
        .withTracing(isTracing)
        .withJsonLog(jsonLogFile)
        .build());
  }

  private CommandLine parseCLIArguments(String[] args) {
    final CommandLineParser commandLineParser = new DefaultParser();
    final CommandLine commandLineParameters;

    try {
      commandLineParameters = commandLineParser.parse(options, args);
    }
    catch (ParseException e) {
      final String msg = "Cannot parse CLI arguments: " + Joiner.on(" ").join(args) + "\nThe reason: " + e.getMessage();
      formatter.printHelp(msg, options);
      throw new RuntimeException(e);
    }

    return commandLineParameters;
  }

  private void printToolUsageHelp() {
    final String helpMsg = "The NESTML command line tool can be used as " +
                           "'java -jar nestml.jar <options> path_to_models'." +
                           " Valid options are listed below:\n";
    formatter.printHelp(helpMsg, options);
  }


  private Optional<String> getOptionValue(CommandLine cmd, String argumentName) {
    if (cmd.hasOption(argumentName)) {
      return  Optional.of(cmd.getOptionValue(argumentName));
    }
    else {
      return Optional.empty();
    }

  }


  public static boolean checkEnvironment(final CliConfiguration cliConfiguration) {
    try {
      FilesHelper.createFolders(cliConfiguration.getTargetPath());
    }

    catch (final Exception e) {
      final String msg = "Cannot create output folder. If you are running from docker, check if the folder provided " +
                         "exists and/or the corresponding user. Execution will be terminated.";
      reporter.reportProgress(msg);
      return false;
    }

    cleanUpTmpFiles(cliConfiguration);

    boolean isError = false;
    if (!evaluateCheckScript(
        PYTHON_CHECK_SCRIPT_SOURCE,
        PYTHON_CHECK_SCRIPT,
        PYTHON_VERSION_TEST_OUTPUT,
        cliConfiguration.getTargetPath())) {
      final String msg = "Install Python the in minimal version 2.7. Execution will be terminated.";
      reporter.reportProgress(msg);
      isError = true;
    }
    else {
      final String msg = "Correct python version is installed";
      reporter.reportProgress(msg);
    }

    if (!evaluateCheckScript(
        SYMPY_CHECK_SCRIPT_SOURCE,
        SYMPY_CHECK_SCRIPT,
        SYMPY_VERSION_TEST_OUTPUT,
        cliConfiguration.getTargetPath())) {
      final String msg = "Install SymPy in minimal version 1.0.1.dev, e.g. from github";
      reporter.reportProgress(msg);
      isError = true;
    }
    else {
      final String msg = "Correct SymPy is installed.";
      reporter.reportProgress(msg);
    }

    return !isError;
  }

  private static void cleanUpTmpFiles(final CliConfiguration cliConfiguration) {
    if (!Files.exists(cliConfiguration.getTargetPath())) {
      FilesHelper.createFolders(cliConfiguration.getTargetPath());
    }
    else {
      final List<Path> tmps = FilesHelper.collectFiles(
          cliConfiguration.getTargetPath(),
          file -> file.endsWith(".tmp") || file.endsWith(".log"));

      tmps.forEach(FilesHelper::deleteFile);
    }
  }

  private static boolean evaluateCheckScript(
      final String scriptSource,
      final String scriptName,
      final String scriptOutput,
      final Path targetPath) {
    executeCommand(scriptSource, scriptName, targetPath);

    final Path file = Paths.get(targetPath.toString(), scriptOutput);
    if (!Files.exists(file)) {
      return false;
    }

    List<String> pythonStatus;

    try {
      pythonStatus = Files.readAllLines(file);
    }
    catch (IOException e) {
      final String msg = "Cannot read python check file.";
      reporter.reportProgress(msg);
      return false;
    }

    return pythonStatus.size() != 0 && pythonStatus.get(0).equals("True");
  }

  private static void executeCommand(
      final String checkScript,
      final String copiedScriptName,
      final Path outputFolder) {
    try {
      copyScript(checkScript, copiedScriptName, outputFolder);

      long start = System.nanoTime();
      final Process res;
      res = Runtime.getRuntime().exec(
          PYTHON_INTERPRETER + copiedScriptName,
          new String[0],
          outputFolder.toFile());
      res.waitFor();
      long end = System.nanoTime();
      long elapsedTime = end - start;
      final String msg = "Successfully evaluated script. Elapsed time: "
          + (double) elapsedTime / 1000000000.0 +  " [s]";
      Log.trace(msg, LOG_NAME);

      getListFromStream(res.getErrorStream()).forEach(Log::error);
      getListFromStream(res.getInputStream()).forEach(entry -> Log.info(entry, LOG_NAME));

    }
    catch (IOException|InterruptedException e) {
      throw new RuntimeException(e);
    }

  }

  private static void copyScript(
      final String checkerScript,
      final String copiedScriptName,
      final Path outputFolder) throws IOException {
    final ClassLoader classloader = NestmlFrontend.class.getClassLoader();
    final InputStream is = classloader.getResourceAsStream(checkerScript);
    byte[] buffer = new byte[is.available()];
    if (is.read(buffer) < 0) {
      Log.error("Cannot copy the script " + checkerScript);
    }

    final OutputStream outStream = new FileOutputStream(
        Paths.get(outputFolder.toString(), copiedScriptName).toString());
    outStream.write(buffer);
  }

  private static List<String> getListFromStream(final InputStream inputStream) throws IOException {
    final BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
    return in.lines().collect(Collectors.toList());
  }

  private void executeConfiguration(final CliConfiguration configuration) {
    final CliConfigurationExecutor executor = new CliConfigurationExecutor();

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(configuration.getModelPath());
    final NestCodeGenerator nestCodeGenerator = new NestCodeGenerator(nestmlScopeCreator, configuration.isTracing());

    executor.execute(nestCodeGenerator, configuration);
  }


}
