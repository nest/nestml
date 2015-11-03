package org.nest.sympy;

import org.junit.Test;
import org.nest.nestml._ast.ASTAliasDecl;

import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * Created by user on 20.05.15.
 */
public class Sympy2NESTMLConverterTest {
  private final static String GENERATED_MATRIX_PATH = "src/test/resources/org/nest/sympy/solution.matrix.tmp";

  final Sympy2NESTMLConverter sympy2NESTMLConverter = new Sympy2NESTMLConverter();

  @Test
  public void testConvertMatrixFile() throws Exception {

    final List<ASTAliasDecl> testant = sympy2NESTMLConverter.convertMatrixFile2NESTML(GENERATED_MATRIX_PATH);
    assertEquals(9, testant.size());
  }

  @Test
  public void testReadingFromFile() {
    List<String> testant = sympy2NESTMLConverter.readMatrixElementsFromFile(GENERATED_MATRIX_PATH);

    assertEquals(9, testant.size());
  }

}
