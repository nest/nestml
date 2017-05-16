/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.frontend;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Data class to store the tool's configuration
 *
 * @author plotnikov
 */
public class CliConfiguration {
  private final Path modelPath;
  private final Path targetPath;
  private final String jasonLogFile;
  private boolean isTracing;
  private boolean isCodegeneration;
  private final String moduleName;

  public CliConfiguration(final Builder builder) {
    this.modelPath = builder.modelPath;
    this.targetPath = builder.targetPath;
    this.jasonLogFile = builder.jasonLogFile;
    this.isTracing = builder.isTracing;
    this.isCodegeneration = builder.isCodegeneration;
    this.moduleName = builder.moduleName;
  }


  boolean isCodegeneration() {
    return isCodegeneration;
  }

  Path getModelPath() {
    return modelPath;
  }

  Path getTargetPath() {
    return targetPath;
  }

  public boolean isTracing() {
    return isTracing;
  }

  public String getModuleName() {
    return moduleName;
  }

  public String getJsonLogFile() {
    return this.jasonLogFile;
  }

  public static class Builder {
    private Path modelPath;
    private Path targetPath;
    private String jasonLogFile = "";
    private boolean isTracing = false;
    private boolean isCodegeneration;
    public String moduleName;

    Builder withModelPath(final Path modelPath) {
      this.modelPath = modelPath;
      return this;
    }

    Builder withTargetPath(final String targetPath) {
      this.targetPath = Paths.get(targetPath);
      return this;
    }

    Builder withCodegeneration(final boolean isCodegeneration) {
      this.isCodegeneration = isCodegeneration;
      return this;
    }

    Builder withModuleName(final String moduleName) {
      this.moduleName = moduleName;
      return this;
    }

    Builder withTracing(boolean isTracing) {
      this.isTracing = isTracing;
      return this;
    }

    Builder withJsonLog(final String jasonLogFile) {
      // TODO: check that it is actually a file
      this.jasonLogFile = jasonLogFile;
      return this;
    }

    public CliConfiguration build() {
      return new CliConfiguration(this);
    }

  }

}
