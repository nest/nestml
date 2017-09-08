/*
 * SolverInput.java
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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import org.nest.nestml._ast.ASTEquation;
import org.nest.nestml._ast.ASTEquationsBlock;
import org.nest.nestml._ast.ASTOdeFunction;
import org.nest.nestml._ast.ASTShape;
import org.nest.nestml.prettyprinter.ExpressionsPrettyPrinter;
import org.nest.nestml.prettyprinter.NESTMLPrettyPrinter;

import java.util.List;
import java.util.stream.Collectors;

/**
  Captures the ODE block for the processing in the SymPy. Generates corresponding json representation.
 */
class SolverInput {
  public final List<String> functions;
  public final List<String> shapes;
  public final String ode;
  private final ExpressionsPrettyPrinter printer = new ExpressionsPrettyPrinter();

  SolverInput(final ASTEquationsBlock odeBlock) {
    ASTEquationsBlock tmp = odeBlock.deepClone();
    tmp = OdeTransformer.replaceSumCalls(tmp);

    ode = printEquation(tmp.getODEs().get(0));

    functions = tmp.getOdeFunctions()
        .stream()
        .map(this::printOdeFunction)
        .collect(Collectors.toList());

    shapes = tmp.getShapes()
        .stream()
        .map(this::printShape)
        .collect(Collectors.toList());
  }

  public SolverInput(final List<ASTShape> shapes) {
    this.functions = Lists.newArrayList();
    this.ode = null;
    this.shapes = shapes
        .stream()
        .map(this::printShape)
        .collect(Collectors.toList());

  }

  /**
   * This method is used in freemaker template. Therefore, it must remain public.
   */
  private String printEquation(final ASTEquation astEquation) {

    return astEquation.getLhs() + " = " + printer.print(astEquation.getRhs());
  }

  /**
  * This method is currently used in the serialization int the JSON format
  */
  private String printOdeFunction(final ASTOdeFunction astOdeAlias) {
    final String initExpression = printer.print(astOdeAlias.getExpr());

    return astOdeAlias.getVariableName() + " = " + initExpression;
  }

  private String printShape(final ASTShape astShape) {
    return astShape.getLhs() + " = " + printer.print(astShape.getRhs());
  }


  String toJSON() {
    final ObjectMapper mapper = new ObjectMapper();
    try {
      return mapper.writerWithDefaultPrettyPrinter().writeValueAsString(this);
    }
    catch (JsonProcessingException e) {
      throw new RuntimeException("The construction of the JSON output. Internal error.", e);
    }

  }

}
