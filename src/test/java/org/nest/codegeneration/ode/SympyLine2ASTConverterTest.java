package org.nest.codegeneration.ode;

import org.junit.Test;
import org.nest.DisableFailQuickMixin;
import org.nest.spl._ast.ASTDeclaration;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

public class SympyLine2ASTConverterTest extends DisableFailQuickMixin {

  @Test
  public void testConvertLine2AST() {
    final SympyLine2ASTConverter converter = new SympyLine2ASTConverter();
    final String testExpr = "P00 real = -Tau*tau_in*(Tau*h*exp(h/Tau) + Tau*tau_in*exp(h/Tau) - Tau*tau_in*exp"
        + "(h/tau_in) - "
        + "h*tau_in*exp(h/Tau))*exp(-h/tau_in - h/Tau)/(C*(Tau**2 - 2*Tau*tau_in + tau_in**2)) # PXX";
    final ASTDeclaration testant = converter.convert(testExpr);
    assertNotNull(testant);
    assertEquals(1, testant.getVars().size());
    assertEquals("P00", testant.getVars().get(0));
  }

}
