/*
 * Copyright (c) 2015 RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.codegeneration;

import org.junit.Test;

import java.nio.file.Paths;

import static org.junit.Assert.assertEquals;

/**
 * Generates entire NEST implementation for several NESTML models.
 *
 * @author plotnikov
 */
public class SolverTypeTest {
  private final static String SOLVER_TYPE_FILE = "src/test/resources/codegeneration/sympy/psc/solverType.property";

  @Test
  public void testLoadTypeFromFile() {
    final SolverType result = SolverType.fromFile(Paths.get(SOLVER_TYPE_FILE));
    assertEquals(SolverType.EXACT, result);
  }

}