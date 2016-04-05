/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.frontend;

import com.google.common.base.Joiner;
import de.se_rwth.commons.logging.Log;
import org.apache.commons.cli.*;
import org.nest.codegeneration.NESTCodeGenerator;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.utils.FileHelper;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static de.se_rwth.commons.logging.Log.trace;

/**
 * Handles available options set at the tool invocation. Makes minimal checks of the infrastructure:
 * python, sympy.
 *
 * @author plotnikov
 */
public class NESTMLFrontend {

  private static final String PYTHON_VERSION_TEST_OUTPUT = "pythonVersion.tmp";
  private static final String PYTHON_CHECK_SCRIPT = "pythonChecker.py";
  private static final String PYTHON_CHECK_SCRIPT_SOURCE = "checks/pythonCheck.py";

  private static final String SYMPY_VERSION_TEST_OUTPUT = "sympyVersion.tmp";
  private static final String SYMPY_CHECK_SCRIPT = "sympyChecker.py";
  private static final String SYMPY_CHECK_SCRIPT_SOURCE = "checks/sympyChecker.py";

  private final static String LOG_NAME = NESTMLFrontend.class.getName();
  private static final String HELP_ARGUMENT = "help";
  private static final String TARGET_PATH = "target";

  private final Options options = new Options();
  private final HelpFormatter formatter = new HelpFormatter();

  public NESTMLFrontend() {
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
    new NESTMLFrontend().start(args);
  }

  public void start(final String[] args) {
    final CLIConfiguration cliConfiguration = createCLIConfiguration(args);

    if (checkEnvironment(cliConfiguration)) {
      handleConsoleArguments(cliConfiguration);

    } else {
      Log.error("The execution environment is not installed properly.");

    }
  }

  CLIConfiguration createCLIConfiguration(String[] args) {
    final CommandLine commandLineParameters = parseCLIArguments(args);
    interpretHelpArgument(commandLineParameters);

    final String targetPath = interpretTargetPathArgument(commandLineParameters);

    return new CLIConfiguration
        .Builder()
        .withCoCos(true)
        .withInputBasePath(args[0])
        .withTargetPath(targetPath)
        .build();
  }

  private static boolean checkEnvironment(final CLIConfiguration cliConfiguration) {
    cleanUpTmpFiles(cliConfiguration);

    boolean isError = false;
    if (!evaluateCheckScript(
        PYTHON_CHECK_SCRIPT_SOURCE,
        PYTHON_CHECK_SCRIPT,
        PYTHON_VERSION_TEST_OUTPUT,
        cliConfiguration.getTargetPath())) {
      Log.error("Install Python in minimal version 2.7");
      isError = true;
    }
    else {
      Log.info("Python is installed", LOG_NAME);
    }

    if (!evaluateCheckScript(
        SYMPY_CHECK_SCRIPT_SOURCE,
        SYMPY_CHECK_SCRIPT,
        SYMPY_VERSION_TEST_OUTPUT,
        cliConfiguration.getTargetPath())) {
      Log.error("Install SymPy in minimal version 1.0.0");
      isError = true;
    }
    else {
      Log.info("SymPy is installed.", LOG_NAME);
    }
    return !isError;
  }

  private static void cleanUpTmpFiles(final CLIConfiguration cliConfiguration) {
    if (!Files.exists(cliConfiguration.getTargetPath())) {
      FileHelper.createFolders(cliConfiguration.getTargetPath());
    }
    else {
      final List<Path> tmps = FileHelper.collectFiles(
          cliConfiguration.getTargetPath(),
          file -> file.endsWith(".tmp"));

      tmps.stream().forEach(FileHelper::deleteFile);
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
      Log.error("Cannot read python check file.", e);
      return false;
    }

    return pythonStatus.size() != 0 && pythonStatus.get(0).equals("True");
  }

  private static void executeCommand(
      final String checkScript,
      final String copiedScriptName,
      final Path outputFolder) {
    trace("Evaluate script " + copiedScriptName, LOG_NAME);
    try {
      copyScript(checkScript, copiedScriptName, outputFolder);

      long start = System.nanoTime();
      final Process res;
      res = Runtime.getRuntime().exec(
          "python2.7 " + copiedScriptName,
          new String[0],
          outputFolder.toFile());
      res.waitFor();
      long end = System.nanoTime();
      long elapsedTime = end - start;
      final String msg = "Successfully evaluated script. Elapsed time: "
          + (double)elapsedTime / 1000000000.0 +  " [s]";
      trace(msg, LOG_NAME);

      getListFromStream(res.getErrorStream()).forEach(Log::error);
      getListFromStream(res.getInputStream()).forEach(entry -> Log.info(entry, LOG_NAME));

    }
    catch (IOException|InterruptedException e) {
      throw new RuntimeException(e);
    }

  }

  private static void copyScript(
      final String checkScript,
      final String copiedScriptName,
      final Path outputFolder) throws IOException {
    ClassLoader classloader = NESTMLFrontend.class.getClassLoader();
    final InputStream is = classloader.getResourceAsStream(checkScript);
    byte[] buffer = new byte[is.available()];
    if (is.read(buffer) < 0) {
      Log.error("Cannot copy the script " + checkScript);
    }

    OutputStream outStream = new FileOutputStream(
        Paths.get(outputFolder.toString(), copiedScriptName).toString());
    outStream.write(buffer);
  }

  private static List<String> getListFromStream(final InputStream inputStream) throws IOException {
    final BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
    return in.lines().collect(Collectors.toList());
  }

  private void handleConsoleArguments(final CLIConfiguration CLIConfiguration) {
    final CLIConfigurationExecutor executor = new CLIConfigurationExecutor();

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(CLIConfiguration.getInputBase());
    final NESTCodeGenerator nestCodeGenerator = new NESTCodeGenerator(nestmlScopeCreator);

    executor.execute(nestCodeGenerator, CLIConfiguration);
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
      Log.info("'" + argumentName + "' option is set to: " + cmd.getOptionValue(argumentName),
          LOG_NAME);
      return  Optional.of(cmd.getOptionValue(argumentName));
    }
    else {
      return Optional.empty();
    }

  }

}
