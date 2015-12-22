package org.nest.cli;

import com.google.common.base.Joiner;
import de.se_rwth.commons.logging.Log;
import org.apache.commons.cli.*;
import org.nest.codegeneration.NESTML2NESTCodeGenerator;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.IOException;
import java.nio.file.Paths;

/**
 *
 */
public class NESTMLFrontend {

  public static final PredefinedTypesFactory TYPES_FACTORY = new PredefinedTypesFactory();

  private final static String LOGGER_NAME = NESTMLFrontend.class.getName();

  public static final String RUNNING_MODE = "runningMode";

  public static final String HELP_ARGUMENT = "help";

  public static final String INPUT_MODELS = "input";

  public static final String MODEL_PATH = "modelPath";

  public static final String TARGET_PATH = "target";

  private final Options options = new Options();
  private final HelpFormatter formatter = new HelpFormatter();

  protected NESTMLFrontend() {
    //"mode", true, "Chose the working mode. Possible options are: parse, check, generate");
    options.addOption(Option.builder(RUNNING_MODE)
        .longOpt(RUNNING_MODE)
        .hasArgs()
        .numberOfArgs(1)
        .desc("With the 'parseAndCheck' context conditions for NESTML are activated.")
        .build());

    options.addOption(Option.builder(INPUT_MODELS)
        .longOpt(INPUT_MODELS)
        .hasArgs()
        .numberOfArgs(1)
        .desc("Defines the path to input models. E.g. --" + INPUT_MODELS + " ./")
        .build());

    options.addOption(Option.builder(MODEL_PATH)
        .longOpt(MODEL_PATH)
        .hasArgs()
        .numberOfArgs(1)
        .desc("Defines the path to input models. E.g. --" + MODEL_PATH + " ./")
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
    nestmlFrontend.handleCLIArguments(args);

  }

  public void handleCLIArguments(String[] args) {
    Log.enableFailQuick(false);
    final NESTMLToolConfiguration nestmlToolConfiguration = createCLIConfiguration(args);
    final NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator("", TYPES_FACTORY);
    final NESTML2NESTCodeGenerator nestml2NESTCodeGenerator = new NESTML2NESTCodeGenerator(TYPES_FACTORY, nestmlScopeCreator);
    final NESTMLParser parser =  new NESTMLParser();

    try {
      final ASTNESTMLCompilationUnit root = parser.parse(args[0]).get();
      nestmlScopeCreator.runSymbolTableCreator(root);
      NESTMLCoCosManager nestmlCoCosManager = new NESTMLCoCosManager(root, TYPES_FACTORY);
      NESTMLCoCoChecker checker = nestmlCoCosManager.createNESTMLCheckerWithSPLCocos();
      checker.checkAll(root);

      nestml2NESTCodeGenerator.analyseAndGenerate(root, Paths.get(nestmlToolConfiguration.getTargetPath()));
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot parse the model due to parser errors", e);
    }
  }

  public NESTMLToolConfiguration createCLIConfiguration(String[] args) {
    final CommandLine commandLineParameters = parseCLIArguments(args);

    interpretHelpArgument(commandLineParameters);

    boolean isCheckCocos = interpretRunningModeArgument(commandLineParameters);
    final String inputModelPath = interpretInputModelsPathArgument(commandLineParameters);
    final String modelPath = interpretModelPathArgument(commandLineParameters);
    final String targetPath = interpretTargetPathArgument(commandLineParameters);

    final NESTMLToolConfiguration nestmlToolConfiguration = new NESTMLToolConfiguration
        .Builder()
        .withCoCos(isCheckCocos)
        .withInputBasePath(inputModelPath)
        .withModelPath(modelPath)
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
      formatter.printHelp("NESTML frontend", options );
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

  public String interpretInputModelsPathArgument(final CommandLine cmd) {
    return interpretPathArgument(cmd, INPUT_MODELS);
  }

  public String interpretModelPathArgument(final CommandLine cmd) {
    return interpretPathArgument(cmd, MODEL_PATH);
  }

  public String interpretTargetPathArgument(final CommandLine cmd) {
    return interpretPathArgument(cmd, TARGET_PATH);
  }

  private String interpretPathArgument(CommandLine cmd, String argumentName) {
    if (cmd.hasOption(argumentName)) {

      Log.info("'" + argumentName + "' option is set to: " + cmd.getOptionValue(argumentName), LOGGER_NAME);
      return  cmd.getOptionValue(argumentName);

    }
    else {
      Log.info("Uses current folder as " +  argumentName + " value",  LOGGER_NAME);
      return "./";
    }

  }

}
