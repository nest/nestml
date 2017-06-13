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
public class SolverResultTest {
  private final static String errorCase = "{\n" +
                                          "  \"status\": \"failed\", \n" +
                                          "  \"initial_values\": [], \n" +
                                          "  \"update_instructions\": null, \n" +
                                          "  \"solver\": null, \n" +
                                          "  \"ode_var_factor\": null, \n" +
                                          "  \"const_input\": null, \n" +
                                          "  \"propagator_elements\": null, \n" +
                                          "  \"additional_state_variables\": []\n" +
                                          "}\n";

  private final String exactSolution = "{\n" +
                                       "  \"status\": \"success\", \n" +
                                       "  \"solver\": \"exact\", \n" +
                                       "  \"initial_values\": [\n" +
                                       "    {\n" +
                                       "      \"__av__I_in__0\": \"0\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__av__I_in__1\": \"e/tau_syn_in\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__av__I_ex__0\": \"0\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__av__I_ex__1\": \"e/tau_syn_ex\"\n" +
                                       "    }\n" +
                                       "  ], \n" +
                                       "  \"update_instructions\": [\n" +
                                       "    \"V_m = __ode_var_factor * V_m + __const_input * (Tau - Tau*exp(-__h/Tau))\", \n" +
                                       "    \"V_m += __I_in_0*__P_I_in_2_0 + __I_in_1*__P_I_in_2_1\", \n" +
                                       "    \"V_m += __I_ex_0*__P_I_ex_2_0 + __I_ex_1*__P_I_ex_2_1\"\n" +
                                       "  ], \n" +
                                       "  \"ode_var_factor\": {\n" +
                                       "    \"__ode_var_factor\": \"exp(-__h/Tau)\"\n" +
                                       "  }, \n" +
                                       "  \"const_input\": {\n" +
                                       "    \"__const_input\": \"I_e/C_m\"\n" +
                                       "  }, \n" +
                                       " \"propagator_elements\": [\n" +
                                       "    {\n" +
                                       "      \"__P_I_in_0_0\": \"exp(-__h/tau_syn_in)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_in_1_0\": \"__h*exp(-__h/tau_syn_in)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_in_1_1\": \"exp(-__h/tau_syn_in)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_in_2_0\": \"-Tau*tau_syn_in*(Tau*__h*exp(__h/Tau) + Tau*tau_syn_in*exp(__h/Tau) - Tau*tau_syn_in*exp(__h/tau_syn_in) - __h*tau_syn_in*exp(__h/Tau))*exp(-__h/tau_syn_in - __h/Tau)/(C_m*(Tau**2 - 2*Tau*tau_syn_in + tau_syn_in**2))\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_in_2_1\": \"-Tau*tau_syn_in*(exp(__h/Tau) - exp(__h/tau_syn_in))*exp(-__h/tau_syn_in - __h/Tau)/(C_m*(Tau - tau_syn_in))\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_in_2_2\": \"exp(-__h/Tau)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_ex_0_0\": \"exp(-__h/tau_syn_ex)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_ex_1_0\": \"__h*exp(-__h/tau_syn_ex)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_ex_1_1\": \"exp(-__h/tau_syn_ex)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_ex_2_0\": \"-Tau*tau_syn_ex*(Tau*__h*exp(__h/Tau) + Tau*tau_syn_ex*exp(__h/Tau) - Tau*tau_syn_ex*exp(__h/tau_syn_ex) - __h*tau_syn_ex*exp(__h/Tau))*exp(-__h/tau_syn_ex - __h/Tau)/(C_m*(Tau**2 - 2*Tau*tau_syn_ex + tau_syn_ex**2))\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_ex_2_1\": \"-Tau*tau_syn_ex*(exp(__h/Tau) - exp(__h/tau_syn_ex))*exp(-__h/tau_syn_ex - __h/Tau)/(C_m*(Tau - tau_syn_ex))\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_ex_2_2\": \"exp(-__h/Tau)\"\n" +
                                       "    }\n" +
                                       "  ],   \n" +
                                       "  \"additional_state_variables\": [\n" +
                                       "    \"__I_in0\", \n" +
                                       "    \"__I_in1\", \n" +
                                       "    \"__I_ex0\", \n" +
                                       "    \"__I_ex1\"\n" +
                                       "  ]\n" +
                                       "}";

  @Test
  public void testErrorCase() {
    final SolverResult testant = SolverResult.fromJSON(errorCase); // must not fail
    Assert.assertNotNull(testant);

  }

  @Test
  public void testExactSolution() {
    final SolverResult testant = SolverResult.fromJSON(exactSolution); // must not fail
    Assert.assertNotNull(testant);

  }

}