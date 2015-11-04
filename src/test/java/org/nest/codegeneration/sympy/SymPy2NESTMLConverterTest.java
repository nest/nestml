package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.nestml._ast.ASTAliasDecl;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * Created by user on 20.05.15.
 */
public class SymPy2NESTMLConverterTest {
  private final static String P00_FILE = "src/test/resources/codegeneration/sympy/P00.mat";
  private final static String PSC_INITIAL_VALUE_FILE = "src/test/resources/codegeneration/sympy/pscInitialValue.mat";
  private final static String STATE_VECTOR_FILE = "src/test/resources/codegeneration/sympy/state.vector.mat";
  private final static String UPDATE_STEP_FILE = "src/test/resources/codegeneration/sympy/update.step.mat";

  final SymPy2NESTMLConverter symPy2NESTMLConverter = new SymPy2NESTMLConverter();

  @Test
  public void testP00() throws Exception {

    final ASTAliasDecl testant = symPy2NESTMLConverter.convertToAlias(P00_FILE);
    assertEquals(testant.getDeclaration().getVars().get(0), "P00");
    assertTrue(testant.getDeclaration().getExpr().isPresent());

  }

  @Test
  public void testConvertString2Alias() {
    final String testExpr = "P00 real = -Tau*tau_in*(Tau*h*exp(h/Tau) + Tau*tau_in*exp(h/Tau) - Tau*tau_in*exp"
        + "(h/tau_in) - "
        + "h*tau_in*exp(h/Tau))*exp(-h/tau_in - h/Tau)/(C*(Tau**2 - 2*Tau*tau_in + tau_in**2)) # PXX";
    final ASTAliasDecl testant = symPy2NESTMLConverter.convertStringToAlias(testExpr);
    assertNotNull(testant);
    assertEquals(1, testant.getDeclaration().getVars().size());
    assertEquals("P00", testant.getDeclaration().getVars().get(0));
  }

}
