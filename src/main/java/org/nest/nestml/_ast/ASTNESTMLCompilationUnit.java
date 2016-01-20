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
  private String packageName = "";
  private String artifactName = "";

  public void setPackageName(final String packageName) {
    this.packageName = packageName;
  }

  public void setArtifactName(final String artifactName) {
    this.artifactName = artifactName;
  }

  protected ASTNESTMLCompilationUnit () {

  }

  protected ASTNESTMLCompilationUnit (
      java.util.List<org.nest.nestml._ast.ASTImport> imports
      ,
      java.util.List<org.nest.nestml._ast.ASTNeuron> neurons
      ,
      java.util.List<org.nest.nestml._ast.ASTComponent> components
      ,
      java.util.List<String> nEWLINEs

  ) {
    super(imports, neurons, components , nEWLINEs);
  }

  public String getArtifactName() {
    return artifactName;
  }

  public String getPackageName() {
    return packageName;
  }

  public String getFullName() {
    if (getPackageName().isEmpty()) {
      return  getArtifactName();
    }
    else {
      return getPackageName() + "." + getArtifactName();
    }

  }
}
