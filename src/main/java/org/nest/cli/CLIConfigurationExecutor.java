package org.nest.cli;

import com.google.common.collect.Lists;
import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;
import org.nest.utils.LogHelper;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

public class CLIConfigurationExecutor {

  private static final String LOG_NAME = CLIConfigurationExecutor.class.getName();

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  public CLIConfigurationExecutor() {
    Log.enableFailQuick(false);
  }

  public boolean execute(final NESTMLToolConfiguration nestmlToolConfiguration) {
    List<String> nestmlModelFilenames = collectNestmlModelFilenames(nestmlToolConfiguration.getInputBasePath());
    handleCollectedModels(nestmlModelFilenames, nestmlToolConfiguration);

    return true;
  }

  private List<String> collectNestmlModelFilenames(final String inputPath) {
    List<String> filenames = Lists.newArrayList();
    try {
      Files.list(new File(inputPath).toPath())
          .forEach(file -> filenames.add(file.getFileName().toString()));
    }
    catch (IOException e) {
      final String msg = "There is a problem to process NESTML models in the folder:  " + inputPath;
      Log.error(msg, e);
      throw new RuntimeException(msg, e);
    }
    Log.info("NESTML models found: #" + filenames.size(), LOG_NAME);
    return filenames;
  }

  private void handleCollectedModels(
      final List<String> nestmlModelFilenames,
      final NESTMLToolConfiguration nestmlToolConfiguration) {
    for (final String modelName:nestmlModelFilenames) {
      handleSingleModel(modelName, nestmlToolConfiguration);
    }

  }

  private void handleSingleModel(final String modelName, final NESTMLToolConfiguration nestmlToolConfiguration) {
    parseWithOptionalCocosCheck(modelName, nestmlToolConfiguration);
    Log.info("Processed model: " + modelName, LOG_NAME);
  }

  private void parseWithOptionalCocosCheck(final String modelName, final NESTMLToolConfiguration nestmlToolConfiguration) {
    final NESTMLCompilationUnitMCParser nestmlParser = NESTMLParserFactory
        .createNESTMLCompilationUnitMCParser();
    try {
      final Optional<ASTNESTMLCompilationUnit> root = nestmlParser.parse(nestmlToolConfiguration.getInputBasePath() +
              File.separator + modelName);
      if (root.isPresent()) {
        if (nestmlToolConfiguration.isCheckCoCos()) {
          checkCocosForModel(modelName, nestmlToolConfiguration, root);

        }

      }
      else {
        Log.error("There is a problem with the model: " + modelName + ". It will be skipped.");
      }

    }
    catch (IOException e) {
      Log.error("Skips the procession of the model: " + modelName, e);
    }

  }

  private void checkCocosForModel(
      final String modelName,
      final NESTMLToolConfiguration toolConfiguration,
      final Optional<ASTNESTMLCompilationUnit> root) {
    final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(
        toolConfiguration.getModelPath(), typesFactory);

    scopeCreator.runSymbolTableCreator(root.get());

    final NESTMLCoCosManager nestmlCoCosManager
        = new NESTMLCoCosManager(
        root.get(),
        scopeCreator.getTypesFactory());

    final NESTMLCoCoChecker cocosChecker = nestmlCoCosManager.createDefaultChecker();

    checkNESTMLCocos(root, cocosChecker);
    evaluateCocosLog(modelName, LogHelper.getErrorsByPrefix("NESTML_", Log.getFindings()));
  }

  private void checkNESTMLCocos(Optional<ASTNESTMLCompilationUnit> root, NESTMLCoCoChecker cocosChecker) {
    Log.getFindings().clear();
    cocosChecker.checkAll(root.get());
  }

  private void evaluateCocosLog(String modelName, Collection<Finding> nestmlErrorFindings) {
    if (nestmlErrorFindings.isEmpty()) {
      Log.info(modelName + " contains no errors", LOG_NAME);
    }
    else {
      Log.error(modelName + " contains the following errors: ");
      nestmlErrorFindings.forEach(finding -> Log.warn(finding.toString()));
    }
  }

}
