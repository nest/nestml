package org.nest.nestml.prettyprinter;

import de.se_rwth.commons.logging.Log;
import org.junit.BeforeClass;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTBlock;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._parser.NESTMLParser;
import org.nest.utils.AstUtils;
import org.nest.utils.FilesHelper;

import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.IntStream;

import static org.junit.Assert.assertTrue;

/**
 * Processes all NESTML modles. Then, prettyprints them and parses again, to check the soundness of
 * the printed models.
 *
 * @author plotnikov
 */
public class NESTMLPrettyPrinterTest extends ModelbasedTest {
  private final NESTMLParser nestmlParser = new NESTMLParser(TEST_MODEL_PATH);
  @BeforeClass
  public static void disableFailQuick() {
    Log.enableFailQuick(false);
  }

  private Optional<ASTNESTMLCompilationUnit> parseStringAsSPLFile(final String fileAsString) throws IOException {
    return nestmlParser.parse(new StringReader(fileAsString));
  }

  @BeforeClass
  public static void BeforeTestsuite() {
    Log.enableFailQuick(false);
  }

  @Test
  public void testThatPrettyPrinterProducesParsableOutput() throws IOException {
    parseAndCheckNestmlModel("models/iaf_cond_alpha_implicit.nestml");
  }

  @Test
  public void testAllModelsForCocos() throws IOException {
    parseAllNESTMLModelsFromFolder("src/test/resources/org/nest/nestml/_cocos");

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
    final List<Path> nestmlModels = FilesHelper.collectNESTMLModelFilenames(Paths.get(folderPath));
    for (final Path splModelFile : nestmlModels) {
      System.out.println("Current model: " +  splModelFile.toString());
      parseAndCheckNestmlModel(splModelFile.toString());

    }

  }

  private void parseAndCheckNestmlModel(String pathToModel) throws IOException {
    System.out.println("Handles the model: " + pathToModel);

    final NESTMLPrettyPrinter splPrettyPrinter = NESTMLPrettyPrinter.Builder.build();
    final Optional<ASTNESTMLCompilationUnit> splModelRoot = nestmlParser.parse(pathToModel);
    assertTrue("Cannot parse the model: " + pathToModel, splModelRoot.isPresent());

    splModelRoot.get().accept(splPrettyPrinter);

    final Optional<ASTNESTMLCompilationUnit> prettyPrintedRoot = parseStringAsSPLFile(splPrettyPrinter.result());
    assertTrue(prettyPrintedRoot.isPresent());
  }

  @Test
  public void testPrintingComment() throws IOException {
    final ExpressionsPrettyPrinter prettyPrinter = new ExpressionsPrettyPrinter();
    final SPLPrettyPrinter splPrettyPrinter = new SPLPrettyPrinter(prettyPrinter);

    final ASTNESTMLCompilationUnit root = parseNESTMLModel("src/test/resources/org/nest/nestml/parsing/comment.nestml");

    final Optional<ASTBlock> astBlock = AstUtils.getAny(root, ASTBlock.class);

    assertTrue(astBlock.isPresent());
    splPrettyPrinter.print(astBlock.get());
    final String printedModel = splPrettyPrinter.result();
    System.out.println(printedModel);

    Optional<ASTBlock> prettyPrintedRoot = nestmlParser.parseBlock(new StringReader(splPrettyPrinter.result()));
    assertTrue(prettyPrintedRoot.isPresent());

    IntStream.range(1, 11).forEach(
        index -> assertTrue("Comment" + index + " is missing.", printedModel.contains("Comment " + index)));

  }

}
