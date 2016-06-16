/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.ode._ast;

import com.google.common.base.Joiner;
import de.monticore.types.types._ast.ASTQualifiedName;

import java.util.List;

/**
 * HW extension of the AST class. Provides method to print the variable name.
 *
 * @author plotnikov
 */
public class ASTDerivative extends ASTDerivativeTOP {

  public ASTDerivative(
      final ASTQualifiedName name,
      final List<String> differentialOrder) {
    super(name, differentialOrder);
  }

  public ASTDerivative() {
  }

  @Override
  public String toString() {
    return name.toString() + Joiner.on("'").join(getDifferentialOrder());
  }

  public String getSimpleName() {
    return name.toString();
  }

}
