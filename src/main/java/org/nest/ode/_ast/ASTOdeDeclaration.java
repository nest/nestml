/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.ode._ast;

import org.antlr.runtime.misc.DoubleKeyMap;

import java.util.List;
import java.util.stream.Collectors;

/**
 * HW extension for the ODE block. Provides getter method to get shapes and equations.
 *
 * @author plotnikov
 */
public class ASTOdeDeclaration extends ASTOdeDeclarationTOP {
  public ASTOdeDeclaration() {

  }

  public ASTOdeDeclaration(
      final List<ASTEquation> equations,
      final List<String> nEWLINEs) {
    super(equations, nEWLINEs);
  }

  public List<ASTEquation> getEqs() {
    return equations
        .stream()
        .filter(equation -> equation.getLhs().getDifferentialOrder().size() == 0)
        .collect(Collectors.toList());
  }

  public List<ASTEquation> getODEs() {
    return equations
        .stream()
        .filter(equation -> equation.getLhs().getDifferentialOrder().size() > 0)
        .collect(Collectors.toList());
  }
}
