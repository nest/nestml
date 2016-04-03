/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.commons._ast;

import de.monticore.types.types._ast.ASTQualifiedName;
import de.se_rwth.commons.Names;

/**
 * HW extension of the AST class. Provides method to print the variable name.
 *
 * @author plotnikov
 */
public class ASTVariable extends ASTVariableTOP {

  public ASTVariable(ASTQualifiedName name) {
    super(name);
  }

  public ASTVariable() {

  }

  @Override
  public String toString() {
    return Names.getQualifiedName(name.getParts());
  }

}
