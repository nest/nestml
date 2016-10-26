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

import static com.google.common.base.Preconditions.checkArgument;

/**
 * Handles available options set at the tool invocation. Makes minimal checks of the infrastructure:
 * python, sympy.
 *
 * @author plotnikov
 */
public class NestmlFrontend {
  private static final String PYTHON_VERSION_TEST_OUTPUT = "pythonVersion.tmp";
  private static final String PYTHON_CHECK_SCRIPT = "pythonChecker.py";
  private static final String PYTHON_CHECK_SCRIPT_SOURCE = "checks/pythonChecker.py";

  private static final String SYMPY_VERSION_TEST_OUTPUT = "sympyVersion.tmp";
  private static final String SYMPY_CHECK_SCRIPT = "sympyChecker.py";
  private static final String SYMPY_CHECK_SCRIPT_SOURCE = "checks/sympyChecker.py";

  private final static String LOG_NAME = NestmlFrontend.class.getName();
  private static final String HELP_ARGUMENT = "help";
  private static final String TARGET_PATH = "target";
  private static final String PYTHON_INTERPRETER = "python ";

  private final Options options = new Options();
  private final HelpFormatter formatter = new HelpFormatter();

  private final static Reporter reporter = Reporter.get();

  public NestmlFrontend() {
    Log.enableFailQuick(false); // otherwise error terminates the java vm

    options.addOption(Option.builder(TARGET_PATH)
        .longOpt(TARGET_PATH)
        .hasArgs()
        .numberOfArgs(1)
        .desc("Defines the path where generated artifacts are stored. E.g. --" + TARGET_PATH + " ./")
        .build());

    options.addOption(Option.builder(HELP_ARGUMENT)
        .longOpt(HELP_ARGUMENT)
        .build());
  }

  public static void main(final String[] args) {
    new NestmlFrontend().start(args);
  }

  public void start(final String[] args) {
    if (args.length > 0) {
      final CliConfiguration cliConfiguration = createCLIConfiguration(args);

      if (checkEnvironment(cliConfiguration)) {
        executeConfiguration(cliConfiguration);

      }
      else {
        final String msg = "The execution environment is not installed properly. Execution will be terminated.";
        reporter.addSystemInfo(msg, Reporter.Level.ERROR);
      }

    }
    else {
      reporter.addSystemInfo("The tool must get one argument with the path to the model folder", Reporter.Level.ERROR);
      formatter.printHelp("NESTML frontend: ", options);
    }

  }

  public CliConfiguration createCLIConfiguration(String[] args) {
    checkArgument(args.length > 0);
    final CommandLine commandLineParameters = parseCLIArguments(args);
    interpretHelpArgument(commandLineParameters);

    final String targetPath = interpretTargetPathArgument(commandLineParameters);

    final String inputPathMsg = "The input modelpath: " + Paths.get(args[0]).toAbsolutePath().toString();
    reporter.addSystemInfo(inputPathMsg, Reporter.Level.INFO);
    final String outputPathMsg = "The base output path: " + Paths.get(targetPath).toAbsolutePath().toString();
    reporter.addSystemInfo(outputPathMsg, Reporter.Level.INFO);

    return new CliConfiguration
        .Builder()
        .withCoCos(true)
        .withInputBasePath(args[0])
        .withTargetPath(targetPath)
        .build();
  }

  public static boolean checkEnvironment(final CliConfiguration cliConfiguration) {
    try {
      FilesHelper.createFolders(cliConfiguration.getTargetPath());
    }

    catch (final Exception e) {
      final String msg = "Cannot create output folder. If you are running from docker, check if the folder provided " +
                         "exists and/or the corresponding user. Execution will be terminated.";
      reporter.addSystemInfo(msg, Reporter.Level.ERROR);
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
      reporter.addSystemInfo(msg, Reporter.Level.ERROR);
      isError = true;
    }
    else {
      final String msg = "Correct python version is installed";
      reporter.addSystemInfo(msg, Reporter.Level.INFO);
    }

    if (!evaluateCheckScript(
        SYMPY_CHECK_SCRIPT_SOURCE,
        SYMPY_CHECK_SCRIPT,
        SYMPY_VERSION_TEST_OUTPUT,
        cliConfiguration.getTargetPath())) {
      final String msg = "Install SymPy in minimal version 1.0.1.dev, e.g. from github";
      reporter.addSystemInfo(msg, Reporter.Level.ERROR);
      isError = true;
    }
    else {
      final String msg = "Correct SymPy is installed.";
      reporter.addSystemInfo(msg, Reporter.Level.INFO);
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
          file -> file.endsWith(".tmp"));

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
      reporter.addSystemInfo(msg, Reporter.Level.ERROR);
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

  private void executeConfiguration(final CliConfiguration CliConfiguration) {
    final CliConfigurationExecutor executor = new CliConfigurationExecutor();

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(CliConfiguration.getInputBase());
    final NestCodeGenerator nestCodeGenerator = new NestCodeGenerator(nestmlScopeCreator);

    executor.execute(nestCodeGenerator, CliConfiguration);
  }

  CommandLine parseCLIArguments(String[] args) {
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

  private void interpretHelpArgument(CommandLine cmd) {
    if (cmd.hasOption(HELP_ARGUMENT)) {
      formatter.printHelp("NESTML frontend", options);
    }

  }

  String interpretTargetPathArgument(final CommandLine cmd) {
    return interpretPathArgument(cmd, TARGET_PATH).orElse("build");
  }

  private Optional<String> interpretPathArgument(CommandLine cmd, String argumentName) {
    if (cmd.hasOption(argumentName)) {
      Log.trace("'" + argumentName + "' option is set to: " + cmd.getOptionValue(argumentName), LOG_NAME);
      return  Optional.of(cmd.getOptionValue(argumentName));
    }
    else {
      return Optional.empty();
    }

  }

}
