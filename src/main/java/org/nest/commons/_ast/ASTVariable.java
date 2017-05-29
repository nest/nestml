/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.commons._ast;

import com.google.common.base.Joiner;
import de.monticore.types.types._ast.ASTQualifiedName;

import java.util.List;

/**
 * HW extension of the AST class. Provides method to print the variable name.
 *
 * @author plotnikov
 */
public class ASTVariable extends ASTVariableTOP {

  public ASTVariable(
      final String name,
      final List<String> differentialOrder) {
    super(name, differentialOrder);
  }

  public ASTVariable() {
  }

  @Override
  public String toString() {
    return name + Joiner.on("'").join(getDifferentialOrder());
  }

}
