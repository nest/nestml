/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml.symboltable;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLCoCoChecker;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLCoCosManager;
import org.nest.nestml._symboltable.NESTMLScopeCreator;

import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.Optional;

import static org.nest.utils.LogHelper.getErrorsByPrefix;


/**
 * Iterates through good models and checks that there is no errors in log.
 *
 * @author (last commit) $$Author$$
 * @version $$Revision$$, $$Date$$
 * @since 0.0.1
 */
public class NESTMLCoCosManagerTest {

  public static final String TEST_MODEL_PATH = "src/test/resources/";

  @BeforeClass
  public static void initLog() {
    Log.enableFailQuick(false);
  }

  /**
   * Parses the model and returns ast.
   *
   * @throws java.io.IOException
   */
  private Optional<ASTNESTMLCompilationUnit> getAstRoot(String modelPath) throws IOException {
    final NESTMLParser p = new NESTMLParser(Paths.get(TEST_MODEL_PATH));
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
    final File modelsFolder = new File(TEST_MODEL_PATH + "/org/nest/nestml/parsing");

    final String packageName = "org.nest.nestml.parsing";

    for (final File file : modelsFolder.listFiles()) {
      System.out.println("NESTMLCoCosManagerTest.testGoodModels: " + file);

      final String modelName = removeFileExtension(file.getName(), "nestml");
      final Optional<ASTNESTMLCompilationUnit> root = getAstRoot(file.getPath());
      Assert.assertTrue(root.isPresent());

      final NESTMLScopeCreator scopeCreator = new NESTMLScopeCreator(Paths.get(TEST_MODEL_PATH));
      scopeCreator.runSymbolTableCreator(root.get());

      final String fqnModelName = packageName + "." + modelName;
      System.out.println("NESTMLCoCosManagerTest.testGoodModels: " + fqnModelName);

      checkNESTMLCocosOnly(file, root);
      checkNESTMLWithSPLCocos(file, root);

    }

    Collection<Finding> nestmlErrorFindings = getErrorsByPrefix("NESTML_", Log.getFindings());
    nestmlErrorFindings.forEach(System.out::println);
    Assert.assertTrue("Models contain unexpected errors: " + nestmlErrorFindings.size(),
        nestmlErrorFindings.isEmpty());
  }

  public void checkNESTMLCocosOnly(File file, Optional<ASTNESTMLCompilationUnit> root) {
    final NESTMLCoCosManager nestmlCoCosManager = new NESTMLCoCosManager();
    final NESTMLCoCoChecker checker = nestmlCoCosManager.createDefaultChecker();
    checker.checkAll(root.get());

    Collection<Finding> nestmlErrorFindings = getErrorsByPrefix("NESTML_", Log.getFindings());
    nestmlErrorFindings.forEach(System.out::println);
    final String msg = "The model: " + file.getPath() + "Models contain unexpected errors: " + nestmlErrorFindings.size();
    Assert.assertTrue(msg, nestmlErrorFindings.isEmpty());
  }

  public void checkNESTMLWithSPLCocos(
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

  /**
   * Given the filename, e.g test.nestml; and an extension, nestml, returns the simple name, e.g. test
   *
   */
  private String removeFileExtension(String name, String nestml) {
    if (nestml.startsWith(".")) {
      return name.substring(0, name.indexOf(nestml));
    } else {
      return name.substring(0, name.indexOf("." + nestml));
    }

  }

}
