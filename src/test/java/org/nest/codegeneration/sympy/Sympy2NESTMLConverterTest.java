package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.nestml._ast.ASTAliasDecl;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * Created by user on 20.05.15.
 */
public class Sympy2NESTMLConverterTest {
  private final static String P00_FILE = "src/test/resources/codegeneration/sympy/P00.mat";
  private final static String PSC_INITIAL_VALUE_FILE = "src/test/resources/codegeneration/sympy/pscInitialValue.mat";
  private final static String STATE_VECTOR_FILE = "src/test/resources/codegeneration/sympy/state.vector.mat";
  private final static String UPDATE_STEP_FILE = "src/test/resources/codegeneration/sympy/update.step.mat";

  final Sympy2NESTMLConverter sympy2NESTMLConverter = new Sympy2NESTMLConverter();

  @Test
  public void testP00() throws Exception {

    final ASTAliasDecl testant = sympy2NESTMLConverter.convertDeclaration(P00_FILE);
    assertEquals(testant.getDeclaration().getVars().get(0), "P00");
    assertTrue(testant.getDeclaration().getExpr().isPresent());

  }

}
