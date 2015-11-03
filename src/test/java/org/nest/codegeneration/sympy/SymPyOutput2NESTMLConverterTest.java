/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration.sympy;

import org.junit.Test;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.sympy.SymPyOutput2NESTMLConverter;
import org.nest.spl._ast.ASTDeclaration;

import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * Reads entries from the python output stored in the file and creates corresponding NESTML ASTs.
 *
 * @author plotnikov
 */
public class SymPyOutput2NESTMLConverterTest {
  private final static String GENERATED_MATRIX_PATH = "src/test/resources/sympy/solution.matrix.tmp";

  @Test
  public void testConvertMatrixFile() throws Exception {
    final SymPyOutput2NESTMLConverter symPyOutput2NESTMLConverter = new SymPyOutput2NESTMLConverter();
    final List<ASTAliasDecl> testant = symPyOutput2NESTMLConverter.createDeclarationASTs(GENERATED_MATRIX_PATH);
    assertEquals(9, testant.size());
  }


  @Test
  public void testReadMatrixEntriesFromFile() throws Exception {
    final SymPyOutput2NESTMLConverter symPyOutput2NESTMLConverter = new SymPyOutput2NESTMLConverter();
    List<String> testant = symPyOutput2NESTMLConverter.readMatrixElementsFromFile(GENERATED_MATRIX_PATH);
    assertEquals(9, testant.size());

  }

  @Test
  public void testConvertLine2AST() {
    final SymPyOutput2NESTMLConverter symPyOutput2NESTMLConverter = new SymPyOutput2NESTMLConverter();
    final String testExpr = "P00 real = -Tau*tau_in*(Tau*h*exp(h/Tau) + Tau*tau_in*exp(h/Tau) - Tau*tau_in*exp"
        + "(h/tau_in) - "
        + "h*tau_in*exp(h/Tau))*exp(-h/tau_in - h/Tau)/(C*(Tau**2 - 2*Tau*tau_in + tau_in**2)) # PXX";
    final ASTDeclaration testant = symPyOutput2NESTMLConverter.convert(testExpr);
    assertNotNull(testant);
    assertEquals(1, testant.getVars().size());
    assertEquals("P00", testant.getVars().get(0));
  }

}
