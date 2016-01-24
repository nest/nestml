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
  private static final String TEST_MODEL = "src/test/resources/org/nest/nestml/symboltable/"
      + "iaf_neuron.nestml";

  @Test
  public void testNamesComputation() {

    final String packageName = parser.computePackageName(
        Paths.get(TEST_MODEL),
        Paths.get(TEST_MODEL_PATH));

    final String artifactName = parser.computeArtifactName(Paths.get(TEST_MODEL));
    assertEquals("org.nest.nestml.symboltable", packageName);
    assertEquals("iaf_neuron", artifactName);
  }

  /**
   * Checks that incorrectly stored files are not processed at all.
   */
  @Test
  public void testArtifactHandling() throws IOException {
    final Optional<ASTNESTMLCompilationUnit> withoutExtension
        = parser.parse(Paths.get("test","falseFileExtension.tmp").toString());
    assertFalse(withoutExtension.isPresent());

    final Optional<ASTNESTMLCompilationUnit> wrongFolderStructure
        = parser.parse("falseFileExtension.nestml");
    assertFalse(wrongFolderStructure.isPresent());
  }

}