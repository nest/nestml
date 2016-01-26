/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._ast;

import java.util.Objects;
import java.util.Optional;

/**
 * TODO
 *
 * @author plotnikov
 */
public class ASTNESTMLCompilationUnit extends ASTNESTMLCompilationUnitTOP {
  private Optional<String> packageName = Optional.empty();
  private String artifactName = "";

  public void setPackageName(final String packageName) {
    Objects.requireNonNull(packageName);
    this.packageName = Optional.of(packageName);
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

  public Optional<String> getPackageName() {
    return packageName;
  }

  public String getFullName() {
    if (getPackageName().isPresent()) {
      return getPackageName().get() + "." + getArtifactName();
    }
    else {
      return  getArtifactName();
    }

  }

  /**
   * During model transformation the file is printed and read again. For this temporary folders
   * and file names are used. Therefore, this method provides the possibility to remove it technical
   * name from the model
   */
  public void removePackageName() {
    this.packageName = Optional.empty();
  }
}
