/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.cli;

import com.google.common.base.Joiner;
import de.se_rwth.commons.logging.Log;
import org.apache.commons.cli.*;
import org.nest.codegeneration.NESTCodeGenerator;
import org.nest.nestml._symboltable.NESTMLScopeCreator;

import java.nio.file.Paths;
import java.util.Optional;

/**
 * Handles available options set by the tool invocation
 *
 * @author plotnikov
 */
public class NESTMLFrontend {
  private final static String LOGGER_NAME = NESTMLFrontend.class.getName();

  public static final String RUNNING_MODE = "runningMode";
  public static final String HELP_ARGUMENT = "help";
  public static final String TARGET_PATH = "target";

  private final Options options = new Options();
  private final HelpFormatter formatter = new HelpFormatter();

  public NESTMLFrontend() {
    Log.enableFailQuick(false);
    createOptions();
  }

  private void createOptions() {
    //"mode", true, "Chose the working mode. Possible options are: parse, check, generate");
    options.addOption(Option.builder(RUNNING_MODE)
        .longOpt(RUNNING_MODE)
        .hasArgs()
        .numberOfArgs(1)
        .desc("With the 'parseAndCheck' context conditions for NESTML are activated.")
        .build());

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
    final NESTMLToolConfiguration nestmlToolConfiguration = createCLIConfiguration(args);
    final CLIConfigurationExecutor executor = new CLIConfigurationExecutor();

    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(
        nestmlToolConfiguration.getInputBase());
    final NESTCodeGenerator nestCodeGenerator = new NESTCodeGenerator(nestmlScopeCreator);

    executor.execute(nestCodeGenerator, nestmlToolConfiguration);

  }

  public NESTMLToolConfiguration createCLIConfiguration(String[] args) {
    final CommandLine commandLineParameters = parseCLIArguments(args);
    interpretHelpArgument(commandLineParameters);

    boolean isCheckCocos = interpretRunningModeArgument(commandLineParameters);
    final String targetPath = interpretTargetPathArgument(commandLineParameters);

    final NESTMLToolConfiguration nestmlToolConfiguration = new NESTMLToolConfiguration
        .Builder()
        .withCoCos(isCheckCocos)
        .withInputBasePath(args[0])
        .withTargetPath(targetPath)
        .build();

    return nestmlToolConfiguration;
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

  public boolean interpretRunningModeArgument(final CommandLine cmd) {
    boolean isCheckCocos = false;
    if (cmd.hasOption(RUNNING_MODE)) {
      Log.info("'" + RUNNING_MODE + "' option is set to: " + cmd.getOptionValue(RUNNING_MODE),
          LOGGER_NAME);
      if (cmd.getOptionValue(RUNNING_MODE).equals("parseAndCheck")) {
        Log.info("NESTML models will be parsed and checked.", LOGGER_NAME);
        isCheckCocos = true;
      }

    }
    else {
      Log.info("'" + RUNNING_MODE + "' is set to 'parse' only configuration", LOGGER_NAME);
    }
    return isCheckCocos;
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
