package org.nest.spl.symboltable;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.spl._ast.ASTSPLFile;
import org.nest.spl._cocos.SPLCoCoChecker;
import org.nest.spl._parser.SPLParser;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.Optional;

import static org.nest.utils.LogHelper.getErrorsByPrefix;

/**
 * Tests all context conditions summarized in the manager
 *
 * @author plotnikov
 */
public class SPLCoCosManagerTest {
  private static SPLParser parser = new SPLParser();
  public static final String TEST_MODEL_PATH = "src/test/resources/";

  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();
  private final SPLScopeCreator scopeCreator = new SPLScopeCreator(TEST_MODEL_PATH, typesFactory);
  @BeforeClass
  public static void initLog() {
    Log.enableFailQuick(false);
  }

  @Before
  public void setup() {
    Log.getFindings().clear();
  }

  @Test
  public void testSPLGoodModels() throws IOException {
    final File modelsFolder = new File(TEST_MODEL_PATH + "/org/nest/spl/parsing");


    for (File file : modelsFolder.listFiles()) {
      System.out.println("SPLCoCosManagerTest.testGoodModels: " + file.getName());
      final ASTSPLFile root = getAstRoot(file.getPath());
      scopeCreator.runSymbolTableCreator(root);

      final SPLCoCosManager splCoCosManager = new SPLCoCosManager(scopeCreator.getTypesFactory());
      final SPLCoCoChecker checker = splCoCosManager.createDefaultChecker();
      checker.checkAll(root);
      Collection<Finding> splErrorFindings = getErrorsByPrefix("SPL_", Log.getFindings());
      final StringBuilder errors = new StringBuilder();

      splErrorFindings.forEach(e -> errors.append(e + "\n"));

      final String errorDescription = "Model contain unexpected errors: " + splErrorFindings.size()
          + " The model: " + file.getPath() + " The errors are: " + errors;
      Assert.assertTrue(errorDescription, splErrorFindings.isEmpty());

    }

  }

  /**
   * Parses the model and returns ast.
   *
   * @throws java.io.IOException
   */
  private ASTSPLFile getAstRoot(String modelPath) throws IOException {

    final Optional<ASTSPLFile> ast = parser.parse(modelPath);
    Assert.assertTrue(ast.isPresent());
    return ast.get();
  }

}
