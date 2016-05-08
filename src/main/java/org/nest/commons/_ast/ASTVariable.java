/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.commons._ast;

import de.monticore.types.types._ast.ASTQualifiedName;
import de.se_rwth.commons.Names;

import java.util.List;

/**
 * HW extension of the AST class. Provides method to print the variable name.
 *
 * @author plotnikov
 */
public class ASTVariable extends ASTVariableTOP {

  public ASTVariable(
      final ASTQualifiedName name,
      final List<String> differentialOrder) {
    super(name, differentialOrder);
  }

  public ASTVariable() {
  }

  @Override
  public String toString() {
    return Names.getQualifiedName(name.getParts());
  }

}
