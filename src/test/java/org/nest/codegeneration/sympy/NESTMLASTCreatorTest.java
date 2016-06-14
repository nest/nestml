/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.nestml._ast.ASTAliasDecl;

import java.nio.file.Paths;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * Tests how the plain text is converted into the NESTML ast
 *
 * @author plotnikov
 */
public class NESTMLASTCreatorTest {

  private static final String P_30 = "P30";

  private final static String P30_FILE = "src/test/resources/codegeneration/sympy/psc/P30.tmp";

  private final NESTMLASTCreator converter = new NESTMLASTCreator();

  @Test
  public void testConvertToDeclaration() throws Exception {
    final ASTAliasDecl testant = converter.createAliases(Paths.get(P30_FILE)).get(0);
    assertEquals(testant.getDeclaration().getVars().get(0), P_30);
    assertTrue(testant.getDeclaration().getExpr().isPresent());

  }

  @Test
  public void testConvertString2Alias() {
    final String testExpr = "P30 real = -Tau*tau_in*(Tau*h*exp(h/Tau) + Tau*tau_in*exp(h/Tau) - Tau*tau_in*exp"
        + "(h/tau_in) - "
        + "h*tau_in*exp(h/Tau))*exp(-h/tau_in - h/Tau)/(C*(Tau**2 - 2*Tau*tau_in + tau_in**2)) # PXX";
    final ASTAliasDecl testant = converter.createAlias(testExpr);
    assertNotNull(testant);
    assertEquals(1, testant.getDeclaration().getVars().size());
    assertEquals(P_30, testant.getDeclaration().getVars().get(0));
  }


}
