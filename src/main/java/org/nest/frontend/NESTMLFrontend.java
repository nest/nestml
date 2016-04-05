/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.frontend;

import com.google.common.base.Joiner;
import de.se_rwth.commons.logging.Log;
import org.apache.commons.cli.*;
import org.apache.commons.io.IOUtils;
import org.nest.codegeneration.NESTGenerator;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.utils.FileHelper;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static de.se_rwth.commons.logging.Log.info;

/**
 * Handles available options set by the tool invocation
 *
 * @author plotnikov
 */
public class NESTMLFrontend {

  private static final String PYTHON_VERSION_TEST_OUTPUT = "pythonVersion.tmp";
  private static final String PYTHON_CHECK_SCRIPT = "pythonChecker.py";
  private final static String LOG_NAME = NESTMLFrontend.class.getName();
  private static final String HELP_ARGUMENT = "help";
  private static final String TARGET_PATH = "target";

  private final Options options = new Options();
  private final HelpFormatter formatter = new HelpFormatter();

  public NESTMLFrontend() {
    Log.enableFailQuick(false); // otherwise error terminates the java vm
    createOptions();
  }

  private void createOptions() {
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
    final NESTMLFrontend nestmlFrontend = new NESTMLFrontend();
    nestmlFrontend.start(args);
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
    if (!checkPython(cliConfiguration.getTargetPath())) {
      Log.error("Install Python in minimal version 2.7");
      isError = true;
    }
    else {
      Log.trace("Python is installed", LOG_NAME);
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

  private static boolean checkPython(final Path targetPath) {
    executeCommand(PythonCheckPrograms.PYTHON_CHECK, targetPath);
    final Path file = Paths.get(targetPath.toString(), PYTHON_VERSION_TEST_OUTPUT);
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

  private static void executeCommand(final String command, final Path outputFolder) {
    info("Start long running SymPy script evaluation...", LOG_NAME);
    try {
      ClassLoader classloader = NESTMLFrontend.class.getClassLoader();
      final InputStream is = classloader.getResourceAsStream("checks/pythonCheck.py");
      byte[] buffer = new byte[is.available()];
      is.read(buffer);

      OutputStream outStream = new FileOutputStream(Paths.get(outputFolder.toString(), PYTHON_CHECK_SCRIPT).toString());
      outStream.write(buffer);

      long start = System.nanoTime();
      final Process res;
      res = Runtime.getRuntime().exec(
          "python2.7 " + PYTHON_CHECK_SCRIPT,
          new String[0],
          outputFolder.toFile());
      res.waitFor();
      long end = System.nanoTime();
      long elapsedTime = end - start;
      final String msg = "Successfully evaluated the SymPy script. Elapsed time: "
          + (double)elapsedTime / 1000000000.0 +  " [s]";
      info(msg, LOG_NAME);

      getListFromStream(res.getErrorStream()).forEach(Log::error);
      getListFromStream(res.getInputStream()).forEach(entry -> Log.info(entry, LOG_NAME));

    }
    catch (IOException|InterruptedException e) {
      throw new RuntimeException(e);
    }

  }

  private static List<String> getListFromStream(final InputStream inputStream) throws IOException {
    final BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
    return in.lines().collect(Collectors.toList());
  }

  private void handleConsoleArguments(final CLIConfiguration CLIConfiguration) {
    final CLIConfigurationExecutor executor = new CLIConfigurationExecutor();

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(CLIConfiguration.getInputBase());
    final NESTGenerator nestGenerator = new NESTGenerator(nestmlScopeCreator);

    executor.execute(nestGenerator, CLIConfiguration);
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
