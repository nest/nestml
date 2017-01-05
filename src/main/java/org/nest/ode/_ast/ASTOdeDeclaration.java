/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.ode._ast;

import java.util.List;

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
      final List<ASTShape> shapes,
      final List<ASTOdeFunction> oDEAliass,
      final List<String> nEWLINEs) {
    super(equations, shapes, oDEAliass, nEWLINEs);
  }

  @Override
  public List<ASTShape> getShapes() {
    return shapes;
  }

  public List<ASTEquation> getODEs() {
    return equations;
  }
}
