package org.nest.nestml._parser;

import de.se_rwth.commons.logging.Finding;
import de.se_rwth.commons.logging.Log;
import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.utils.AstUtils;
import org.nest.utils.LogHelper;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static org.junit.Assert.*;
import static org.nest.utils.FilesHelper.collectNESTMLModelFilenames;

/**
 * Tests the method which set artifact and package name according to the file name and corresponding
 *
 *
 * @author plonikov
 */
public class NESTMLParserTest extends ModelbasedTest {
  private static final String TEST_MODEL1 = "src/test/resources/command_line_base/"
      + "cli_example.nestml";

  private static final String TEST_MODEL2 = "src/test/resources/"
      + "command_line_base/sub/cli_example.nestml";

  private static final String TEST_MODEL_COMMENTS = "src/test/resources/comments/iaf_neuron.nestml";

  private static final String TEST_MODEL_PATH = "src/test/resources/command_line_base/";

  @Test
  public void testAllModels() {
    // ignore all models, in an folder with an 'unparsable' infix
    final List<Path> testModels = collectNESTMLModelFilenames(Paths.get("src/test/resources/"))
        .stream()
        .filter( path -> !path.toString().contains("unparsable"))
        .collect(Collectors.toList());

    for (final Path path:testModels) {
      System.out.println(path.toString());
      parseNESTMLModel(path.toString());
    }
  }

  @Test
  public void testNamesComputation() {
    final Optional<String> packageName = parser.computePackageName(
        Paths.get(TEST_MODEL1),
        Paths.get("src/test/resources/", "command_line_base"));

    final String artifactName = parser.computeArtifactName(Paths.get(TEST_MODEL1));
    assertFalse(packageName.isPresent());
    assertEquals("cli_example", artifactName);

    final Optional<String> packageName2 = parser.computePackageName(
        Paths.get(TEST_MODEL2),
        Paths.get(TEST_MODEL_PATH));
    final String artifactName2 = parser.computeArtifactName(Paths.get(TEST_MODEL2));
    assertTrue(packageName2.isPresent());
    assertEquals("sub", packageName2.get());
    assertEquals("cli_example", artifactName2);
  }

  @Test
  public void testEmptyPackage() {
    final String emptyPackage = "src/test/resources/command_line_base/cli_example.nestml";
    final Optional<String> packageName = parser.computePackageName(
        Paths.get(TEST_MODEL1),
        Paths.get(emptyPackage));

    final String artifactName = parser.computeArtifactName(Paths.get(TEST_MODEL1));
    assertFalse(packageName.isPresent());
    assertEquals("cli_example", artifactName);
  }

  /**
   * Checks that incorrectly stored files are not processed at all.
   */
  @Test
  public void testFasleArtifactHandling() throws IOException {

    final Optional<ASTNESTMLCompilationUnit> wrongFolderStructure = parser.parse("falseFileExtension.nestml");
    assertFalse(wrongFolderStructure.isPresent());
  }

  @Test
  public void testNonExistentType() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> ast = parser.parse("src/test/resources/unparsable/wrongTypes.nestml");
    assertFalse(ast.isPresent());
    List<Finding> findings = LogHelper.getModelFindings(Log.getFindings());
    assertEquals(2, findings.size());
  }

  @Test
  public void testMultipleVariablesWithSameName() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> ast = parser.parse("src/test/resources/unparsable/multipleVariablesWithSameName.nestml");
    assertTrue(ast.isPresent());
    scopeCreator.runSymbolTableCreator(ast.get());
    assertTrue(LogHelper.getModelFindings(Log.getFindings()).size() > 0);
  }

  @Test
  public void testCommentsExtraction() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> ast = parser.parse(TEST_MODEL_COMMENTS);
    assertTrue(ast.isPresent());
    final List<ASTDeclaration> declarations = AstUtils.getAll(ast.get(), ASTDeclaration.class);
    for (final ASTDeclaration declaration:declarations) {
      assertTrue(declaration.getComments().size() == 2);
      declaration.getComments().forEach(System.out::println);
    }

  }

}