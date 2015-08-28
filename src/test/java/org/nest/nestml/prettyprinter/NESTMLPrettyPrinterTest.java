package org.nest.nestml.prettyprinter;

import static de.se_rwth.commons.logging.Log.error;

import de.se_rwth.commons.logging.Log;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLCompilationUnitMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.nestml._symboltable.NESTMLScopeCreator;
import org.nest.symboltable.predefined.PredefinedTypesFactory;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.util.Optional;

import static org.junit.Assert.assertTrue;

/**
 * Created by user on 29.05.15.
 */
public class NESTMLPrettyPrinterTest {
  private final NESTMLCompilationUnitMCParser nestmlParser = NESTMLParserFactory
      .createNESTMLCompilationUnitMCParser();
  private static final String TEST_MODEL_PATH = "src/test/resources/";
  private static final PredefinedTypesFactory typesFactory = new PredefinedTypesFactory();

  private Optional<ASTNESTMLCompilationUnit> parseStringAsSPLFile(final String fileAsString) throws IOException {

    return nestmlParser.parse(new StringReader(fileAsString));
  }

  @BeforeClass
  public static void BeforeTestsuite() {
    Log.enableFailQuick(false);
  }

  @Test
  public void testThatPrettyPrinterProducesParsableOutput() throws IOException {
    parseAndCheckNestmlModel("src/test/resources/org/nest/nestml/parsing/iaf_neuron.nestml");
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
        parseAndCheckNestmlModel(splModelFile.getPath());

      }

    }

  }

  private void parseAndCheckNestmlModel(String pathToModel) throws IOException {
    System.out.println("Handles the model: " + pathToModel);

    final NESTMLPrettyPrinter splPrettyPrinter = NESTMLPrettyPrinterFactory.createNESTMLPrettyPrinter();
    final Optional<ASTNESTMLCompilationUnit> splModelRoot = nestmlParser.parse(pathToModel);
    assertTrue("Cannot parse the model: " + pathToModel, splModelRoot.isPresent());

    NESTMLScopeCreator nestmlScopeCreator = new NESTMLScopeCreator(TEST_MODEL_PATH, typesFactory);
    nestmlScopeCreator.runSymbolTableCreator(splModelRoot.get());
    splModelRoot.get().accept(splPrettyPrinter);

    System.out.println(splPrettyPrinter.getResult());

    final Optional<ASTNESTMLCompilationUnit> prettyPrintedRoot = parseStringAsSPLFile(splPrettyPrinter.getResult());
    assertTrue(prettyPrintedRoot.isPresent());
  }

}
