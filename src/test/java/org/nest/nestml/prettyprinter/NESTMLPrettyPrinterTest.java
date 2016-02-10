package org.nest.nestml.prettyprinter;

import de.se_rwth.commons.logging.Log;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.base.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.nestml._symboltable.NESTMLScopeCreator;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Processes all NESTML modles. Then, prettyprints them and parses again, to check the soundness of
 * the printed models.
 *
 * @author plotnikov
 */
public class NESTMLPrettyPrinterTest extends ModelTestBase {
  private final NESTMLParser nestmlParser = new NESTMLParser(TEST_MODEL_PATH);

  private Optional<ASTNESTMLCompilationUnit> parseStringAsSPLFile(final String fileAsString) throws IOException {
    return nestmlParser.parse(new StringReader(fileAsString));
  }

  @BeforeClass
  public static void BeforeTestsuite() {
    Log.enableFailQuick(false);
  }

  @Test
  public void testThatPrettyPrinterProducesParsableOutput() throws IOException {
    parseAndCheckNestmlModel("src/test/resources/codegeneration/iaf_neuron.nestml");
  }

  @Test
  public void testAllModelsForCocos() throws IOException {
    parseAllNESTMLModelsFromFolder("src/test/resources/org/nest/nestml/cocos");

  }

  @Test
  public void testAllModelsForParsing() throws IOException {
    parseAllNESTMLModelsFromFolder("src/test/resources/org/nest/nestml/parsing");

  }

  @Test
  public void testAllModelsForCodegeneration() throws IOException {
    parseAllNESTMLModelsFromFolder("src/test/resources/codegeneration");

  }

  private void parseAllNESTMLModelsFromFolder(final String folderPath) throws IOException {
    final File parserModelsFolder = new File(folderPath);

    for (File splModelFile : parserModelsFolder.listFiles()) {
      if (!splModelFile.isDirectory()) {
        System.out.println("Current model: " +  splModelFile.getName());
        parseAndCheckNestmlModel(splModelFile.getPath());

      }

    }

  }

  private void parseAndCheckNestmlModel(String pathToModel) throws IOException {
    System.out.println("Handles the model: " + pathToModel);

    final NESTMLPrettyPrinter splPrettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    final Optional<ASTNESTMLCompilationUnit> splModelRoot = nestmlParser.parse(pathToModel);
    assertTrue("Cannot parse the model: " + pathToModel, splModelRoot.isPresent());

    NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH);
    nestmlScopeCreator.runSymbolTableCreator(splModelRoot.get());
    splModelRoot.get().accept(splPrettyPrinter);

    //System.out.println(splPrettyPrinter.getResult());

    final Optional<ASTNESTMLCompilationUnit> prettyPrintedRoot = parseStringAsSPLFile(splPrettyPrinter.getResult());
    assertTrue(prettyPrintedRoot.isPresent());
  }

}
