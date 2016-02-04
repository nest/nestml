package org.nest.nestml._parser;

import org.junit.Test;
import org.nest.base.ModelTestBase;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.Optional;

import static org.junit.Assert.*;

/**
 * Tests the method which set artifact and package name according to the file name and corresponding
 *
 *
 * @author plonikov
 */
public class NESTMLParserTest extends ModelTestBase {
  private static final String TEST_MODEL1 = "/home/user/nestml/src/test/resources/command_line_base/"
      + "cli_example.nestml";

  private static final String TEST_MODEL2 = "/home/user/nestml/src/test/resources/"
      + "command_line_base/sub/cli_example.nestml";

  private static final String TEST_MODEL_PATH = "/home/user/nestml/src/test/resources/"
      + "command_line_base/";

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
    final String emptyPackage = "/home/user/nestml/src/test/resources/command_line_base/cli_example.nestml";
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
    final Optional<ASTNESTMLCompilationUnit> withoutExtension
        = parser.parse(Paths.get("test","falseFileExtension.tmp").toString());
    assertFalse(withoutExtension.isPresent());

    final Optional<ASTNESTMLCompilationUnit> wrongFolderStructure
        = parser.parse("falseFileExtension.nestml");
    assertFalse(wrongFolderStructure.isPresent());
  }

}