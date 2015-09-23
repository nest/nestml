package org.nest.codegeneration.ode;

import org.junit.Test;

import java.util.List;

import static org.junit.Assert.*;

/**
 * Created by user on 20.05.15.
 */
public class SympyOutputReaderTest {
  private final static String GENERATED_MATRIX_PATH = "src/test/resources/ode/solution.matrix.tmp";

  @Test
  public void testReadMatrixEntriesFromFile() throws Exception {
    final SympyOutputReader sympyOutputReader = new SympyOutputReader();
    List<String> testant = sympyOutputReader.readMatrixElementsFromFile(GENERATED_MATRIX_PATH);

    assertEquals(9, testant.size());

  }

}
