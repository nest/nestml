/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._ast;

/**
 * TODO
 *
 * @author plotnikov
 */
public class ASTNESTMLCompilationUnit extends ASTNESTMLCompilationUnitTOP {
  protected ASTNESTMLCompilationUnit () {

  }

  protected ASTNESTMLCompilationUnit (
      de.monticore.types.types._ast.ASTQualifiedName packageName
      ,
      org.nest.commons.commons._ast.ASTBLOCK_OPEN bLOCK_OPEN
      ,
      java.util.List<org.nest.nestml._ast.ASTImport> imports
      ,
      java.util.List<org.nest.nestml._ast.ASTNeuron> neurons
      ,
      java.util.List<org.nest.nestml._ast.ASTComponent> components
      ,
      java.util.List<String> nEWLINEs

  ) {
    super(packageName, bLOCK_OPEN, imports, neurons, components , nEWLINEs);
  }
}
