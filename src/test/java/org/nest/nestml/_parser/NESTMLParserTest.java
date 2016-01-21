package org.nest.nestml._parser;

import org.junit.Test;

import java.nio.file.Paths;

import static org.junit.Assert.*;

/**
 * Tests the method which set artifact and package name according to the file name and corresponding
 *
 *
 * @author plonikov
 */
public class NESTMLParserTest {
  private static final String TEST_MODEL_PATH = "src/test/resources/";
  private static final String TEST_MODEL = "src/test/resources/org/nest/nestml/symboltable/"
      + "iaf_neuron.nestml";

  @Test
  public void testNamesComputation() {
    NESTMLParser parser = new NESTMLParser(Paths.get(TEST_MODEL_PATH));
    final String packageName = parser.computePackageName(
        Paths.get(TEST_MODEL),
        Paths.get(TEST_MODEL_PATH));

    final String artifactName = parser.computeArtifactName(Paths.get(TEST_MODEL));
    assertEquals("org.nest.nestml.symboltable", packageName);
    assertEquals("iaf_neuron", artifactName);
  }

}