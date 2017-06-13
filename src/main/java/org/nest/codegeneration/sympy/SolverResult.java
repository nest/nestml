/*
 * SolverResult.java
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

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Encapsulates solver response. Contains the following fields: status (failed, success), initial_values,
 * update_instructions, solver, ode_var_factor, const_input, propagator_elements,additional_state_variables
 */
class SolverResult {
  public String status = "";
  public List<Map.Entry<String, String>> initial_values = Lists.newArrayList();
  public List<String> update_instructions = Lists.newArrayList();
  public String solver = "";
  public Map.Entry<String, String> ode_var_factor = new HashMap.SimpleEntry<>("", "");
  public Map.Entry<String, String>  const_input = new HashMap.SimpleEntry<>("", "");
  public List<Map.Entry<String, String>> propagator_elements = Lists.newArrayList();
  public List<String> additional_state_variables = Lists.newArrayList();

  static SolverResult fromJSON(final String inJSON) {
    try {
      final ObjectMapper mapper = new ObjectMapper();
      return mapper.readValue(inJSON, SolverResult.class);

    }
    catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

}
