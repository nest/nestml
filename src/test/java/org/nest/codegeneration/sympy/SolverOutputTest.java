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

  private final String exactSolution = "{\n" +
                                       "\"status\": \"success\", \n" +
                                       "  \"initial_values\": [\n" +
                                       "    {\n" +
                                       "      \"iv__I_shape_in__0\": \"0\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"iv__I_shape_in__1\": \"e*pA/tau_syn_in\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"iv__I_shape_ex__0\": \"0\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"iv__I_shape_ex__1\": \"e*pA/tau_syn_ex\"\n" +
                                       "    }\n" +
                                       "  ], \n" +
                                       "  \"solver\": \"exact\", \n" +
                                       "  \"ode_var_factor\": {\n" +
                                       "    \"__ode_var_factor\": \"exp(-__h/Tau)\"\n" +
                                       "  }, \n" +
                                       "  \"const_input\": {\n" +
                                       "    \"__const_input\": \"(I_e + currents)/C_m\"\n" +
                                       "  }, \n" +
                                       "  \"propagator_elements\": [\n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_in__0_0\": \"exp(-__h/tau_syn_in)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_in__1_0\": \"__h*exp(-__h/tau_syn_in)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_in__1_1\": \"exp(-__h/tau_syn_in)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_in__2_0\": \"-Tau*tau_syn_in*(Tau*__h*exp(__h/Tau) + Tau*tau_syn_in*exp(__h/Tau) - Tau*tau_syn_in*exp(__h/tau_syn_in) - __h*tau_syn_in*exp(__h/Tau))*exp(-__h/tau_syn_in - __h/Tau)/(C_m*(Tau**2 - 2*Tau*tau_syn_in + tau_syn_in**2))\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_in__2_1\": \"-Tau*tau_syn_in*(exp(__h/Tau) - exp(__h/tau_syn_in))*exp(-__h/tau_syn_in - __h/Tau)/(C_m*(Tau - tau_syn_in))\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_in__2_2\": \"exp(-__h/Tau)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_ex__0_0\": \"exp(-__h/tau_syn_ex)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_ex__1_0\": \"__h*exp(-__h/tau_syn_ex)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_ex__1_1\": \"exp(-__h/tau_syn_ex)\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_ex__2_0\": \"-Tau*tau_syn_ex*(Tau*__h*exp(__h/Tau) + Tau*tau_syn_ex*exp(__h/Tau) - Tau*tau_syn_ex*exp(__h/tau_syn_ex) - __h*tau_syn_ex*exp(__h/Tau))*exp(-__h/tau_syn_ex - __h/Tau)/(C_m*(Tau**2 - 2*Tau*tau_syn_ex + tau_syn_ex**2))\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_ex__2_1\": \"-Tau*tau_syn_ex*(exp(__h/Tau) - exp(__h/tau_syn_ex))*exp(-__h/tau_syn_ex - __h/Tau)/(C_m*(Tau - tau_syn_ex))\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"__P_I_shape_ex__2_2\": \"exp(-__h/Tau)\"\n" +
                                       "    }\n" +
                                       "  ], \n" +
                                       "  \"updates_to_shape_state_variables\": [\n" +
                                       "    {\n" +
                                       "      \"I_shape_ex__1_tmp\": \"I_shape_ex__1\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"I_shape_ex__0_tmp\": \"I_shape_ex__0\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"I_shape_ex__1_tmp\": \"I_shape_ex__0*__P_I_shape_ex__1_0 + I_shape_ex__1*__P_I_shape_ex__1_1\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"I_shape_ex__0_tmp\": \"I_shape_ex__0*__P_I_shape_ex__0_0\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"I_shape_ex__1\": \"I_shape_ex__1_tmp\"\n" +
                                       "    }, \n" +
                                       "    {\n" +
                                       "      \"I_shape_ex__0\": \"I_shape_ex__0_tmp\"\n" +
                                       "    }\n" +
                                       "  ], \n" +
                                       "  \"shape_state_variables\": [\n" +
                                       "    \"I_shape_in__0\", \n" +
                                       "    \"I_shape_in__1\", \n" +
                                       "    \"I_shape_ex__0\", \n" +
                                       "    \"I_shape_ex__1\"\n" +
                                       "  ], \n" +
                                       "  \"ode_var_update_instructions\": [\n" +
                                       "    \"V_abs = __ode_var_factor * V_abs + __const_input * (Tau - Tau*exp(-__h/Tau))\", \n" +
                                       "    \"V_abs += __I_shape_in_0*__P_I_shape_in__2_0 + __I_shape_in_1*__P_I_shape_in__2_1\", \n" +
                                       "    \"V_abs += __I_shape_ex_0*__P_I_shape_ex__2_0 + __I_shape_ex_1*__P_I_shape_ex__2_1\"\n" +
                                       "  ]" +
                                       "}";

  @Test
  public void testErrorCase() {
    final SolverOutput testant = SolverOutput.fromJSON(errorCase); // must not fail
    Assert.assertNotNull(testant);
    Assert.assertEquals("failed", testant.status);
  }

  @Test
  public void testExactSolution() {
    final SolverOutput testant = SolverOutput.fromJSON(exactSolution);
    Assert.assertNotNull(testant);
    Assert.assertEquals("exact", testant.solver);
  }

}