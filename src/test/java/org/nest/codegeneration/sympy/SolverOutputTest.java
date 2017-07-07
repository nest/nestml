/*
 * SolverResultTest.java
 *
 * This file is part of NEST.
 *
 * Copyright (C) 2004 The NEST Initiative
 *
 * NEST is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * NEST is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 */

package org.nest.codegeneration.sympy;

import org.junit.Assert;
import org.junit.Test;

/**
 * Checks that the response created by the SymPy solver is read correctly into POJO.
 * @author plotnikov
 */
public class SolverOutputTest {
  private final static String errorCase = "{\n" +
                                          "  \"status\": \"failed\", \n" +
                                          "  \"initial_values\": [], \n" +
                                          "  \"ode_var_update_instructions\": null, \n" +
                                          "  \"solver\": null, \n" +
                                          "  \"ode_var_factor\": null, \n" +
                                          "  \"const_input\": null, \n" +
                                          "  \"propagator_elements\": null, \n" +
                                          "  \"shape_state_variables\": []\n" +
                                          "}\n";


  @Test
  public void testErrorCase() {
    final SolverOutput testant = SolverOutput.fromJSON(errorCase); // must not fail
    Assert.assertNotNull(testant);
    Assert.assertEquals("failed", testant.status);
  }

  @Test
  public void testExactSolution() {
    final SolverOutput testant = SolverOutput.fromJSON(SolverJsonData.IAF_PSC_ALPHA);
    Assert.assertNotNull(testant);
    Assert.assertEquals("exact", testant.solver);
  }

}