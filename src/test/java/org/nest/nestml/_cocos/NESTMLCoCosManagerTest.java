/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLScopeCreator;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static org.nest.utils.FilesHelper.collectNESTMLModelFilenames;
import static org.nest.utils.LogHelper.getErrorsByPrefix;


/**
 * Iterates through good models and checks that there is no errors in log.
 *
 * @author plotnikov
 */
public class NESTMLCoCosManagerTest extends ModelbasedTest {


  /**
   * Parses the model and returns ast.
   *
   * @throws java.io.IOException
   */
  private Optional<ASTNESTMLCompilationUnit> getAstRoot(String modelPath) throws IOException {
    final NESTMLParser p = new NESTMLParser(TEST_MODEL_PATH);
    final Optional<ASTNESTMLCompilationUnit> ast = p.parse(modelPath);
    Assert.assertTrue(ast.isPresent());
    return ast;
  }

  @Before
  public void setup() {
    Log.getFindings().clear();
  }


  @Test
  public void testGoodModels() throws IOException {

    final File modelsFolder = Paths.get("src/test/resources/org/nest/nestml/parsing").toFile();

    checkAllModelsInFolder(modelsFolder);
  }

  @Test
  public void testCodegenerationModels() throws IOException {
    final List<Path> models = collectNESTMLModelFilenames(TEST_MODEL_PATH);
    models.stream().forEach(this::checkModel);
  }

  private void checkAllModelsInFolder(File modelsFolder) throws IOException {
    for (final File file : modelsFolder.listFiles()) {
      checkModel(file.toPath());
    }

  }

  private void checkModel(final Path file)  {
    System.out.println("NESTMLCoCosManagerTest.testGoodModels: " + file);

    if (file.toFile().isFile()) {
      final Optional<ASTNESTMLCompilationUnit> root;
      try {
        root = getAstRoot(file.toString());
      }
      catch (IOException e) {
        throw new RuntimeException(e);
      }
      Assert.assertTrue(root.isPresent());

      final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH);
      scopeCreator.runSymbolTableCreator(root.get());

      System.out.println("NESTMLCoCosManagerTest.testGoodModels: " + file.toString());

      checkNESTMLCocosOnly(file.toFile(), root);
      checkNESTMLWithSPLCocos(file.toFile(), root);
      Collection<Finding> nestmlErrorFindings = getErrorsByPrefix("NESTML_", Log.getFindings());
      nestmlErrorFindings.forEach(System.out::println);
      Assert.assertTrue("Models contain unexpected errors: " + nestmlErrorFindings.size(),
          nestmlErrorFindings.isEmpty());
    }
  }

  private void checkNESTMLCocosOnly(File file, Optional<ASTNESTMLCompilationUnit> root) {
    final NESTMLCoCosManager nestmlCoCosManager = new NESTMLCoCosManager();
    final NESTMLCoCoChecker checker = nestmlCoCosManager.createDefaultChecker();
    checker.checkAll(root.get());

    Collection<Finding> nestmlErrorFindings = getErrorsByPrefix("NESTML_", Log.getFindings());
    nestmlErrorFindings.forEach(System.out::println);
    final String msg = "The model: " + file.getPath() + "Models contain unexpected errors: " + nestmlErrorFindings.size();
    Assert.assertTrue(msg, nestmlErrorFindings.isEmpty());
  }

  private void checkNESTMLWithSPLCocos(
      final File file,
      final Optional<ASTNESTMLCompilationUnit> root) {

    final NESTMLCoCosManager nestmlCoCosManager = new NESTMLCoCosManager();
    final NESTMLCoCoChecker checker = nestmlCoCosManager.createNESTMLCheckerWithSPLCocos();
    checker.checkAll(root.get());

    Collection<Finding> nestmlErrorFindings = getErrorsByPrefix("NESTML_", Log.getFindings());
    final String nestmlMsg = "The model: " + file.getPath() + ". Models contain unexpected "
        + "NESTML errors: " + nestmlErrorFindings.size();
    Assert.assertTrue(nestmlMsg, nestmlErrorFindings.isEmpty());

    Collection<Finding> splErrorFindings = getErrorsByPrefix("SPL_", Log.getFindings());
    final String splMsg = "The model: " + file.getPath() + ". Models contain unexpected SPL "
        + "errors: " + splErrorFindings.size();
    Assert.assertTrue(splMsg, splErrorFindings.isEmpty());
  }

}
