/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.base.ModelbasedTest;
import org.nest.nestml._ast.ASTDeclaration;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

/**
 * Tests how the plain text is converted into the NESTML ast
 *
 * @author plotnikov
 */
public class AstCreatorTest extends ModelbasedTest {

  @Test
  public void testConvertString2Alias() {
    final String testExpr = "P30 real = -Tau*tau_in*(Tau*h*exp(h/Tau) + Tau*tau_in*exp(h/Tau) - Tau*tau_in*exp"
                            + "(h/tau_in) - h*tau_in*exp(h/Tau))*exp(-h/tau_in - h/Tau)/" +
                            "(C*(Tau**2 - 2*Tau*tau_in + tau_in**2)) # PXX";
    final ASTDeclaration testant = AstCreator.createDeclaration(testExpr);
    assertNotNull(testant);
    assertEquals(1, testant.getVars().size());
    assertEquals("P30", testant.getVars().get(0).toString());
  }


}
