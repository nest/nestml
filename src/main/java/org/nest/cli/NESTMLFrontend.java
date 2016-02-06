/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.cli;

import com.google.common.base.Joiner;
import de.se_rwth.commons.logging.Log;
import org.apache.commons.cli.*;
import org.nest.codegeneration.NESTGenerator;
import org.nest.nestml._symboltable.NESTMLScopeCreator;

import java.util.Optional;

/**
 * Handles available options set by the tool invocation
 *
 * @author plotnikov
 */
public class NESTMLFrontend {
  private final static String LOGGER_NAME = NESTMLFrontend.class.getName();

  public static final String HELP_ARGUMENT = "help";
  public static final String TARGET_PATH = "target";

  private final Options options = new Options();
  private final HelpFormatter formatter = new HelpFormatter();

  public NESTMLFrontend() {
    Log.enableFailQuick(false);
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

  public static void main(String[] args) {
    final NESTMLFrontend nestmlFrontend = new NESTMLFrontend();
    nestmlFrontend.handleConsoleArguments(args);
  }

  public void handleConsoleArguments(String[] args) {
    final Configuration configuration = createCLIConfiguration(args);
    final CLIConfigurationExecutor executor = new CLIConfigurationExecutor();

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        configuration.getInputBase());
    final NESTGenerator nestGenerator = new NESTGenerator(nestmlScopeCreator);

    executor.execute(nestGenerator, configuration);

  }

  public Configuration createCLIConfiguration(String[] args) {
    final CommandLine commandLineParameters = parseCLIArguments(args);
    interpretHelpArgument(commandLineParameters);

    final String targetPath = interpretTargetPathArgument(commandLineParameters);

    return new Configuration
        .Builder()
        .withCoCos(true)
        .withInputBasePath(args[0])
        .withTargetPath(targetPath)
        .build();
  }

  public CommandLine parseCLIArguments(String[] args) {
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

  public void interpretHelpArgument(CommandLine cmd) {
    if (cmd.hasOption(HELP_ARGUMENT)) {
      formatter.printHelp("NESTML frontend", options);
    }
  }

  public String interpretTargetPathArgument(final CommandLine cmd) {
    return interpretPathArgument(cmd, TARGET_PATH).orElse("build");
  }

  private Optional<String> interpretPathArgument(CommandLine cmd, String argumentName) {
    if (cmd.hasOption(argumentName)) {
      Log.info("'" + argumentName + "' option is set to: " + cmd.getOptionValue(argumentName), LOGGER_NAME);
      return  Optional.of(cmd.getOptionValue(argumentName));

    }
    else {
      return Optional.empty();
    }

  }

}
