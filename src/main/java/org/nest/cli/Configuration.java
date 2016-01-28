/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.cli;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Data class to store the tool's configuration
 *
 * @author plotnikov
 */
public class Configuration {
  private final boolean checkCoCos;
  private final Path inputBasePath;
  private final Path targetPath;

  private Configuration(final Builder builder) {
    this.checkCoCos = builder.checkCoCos;
    this.inputBasePath = builder.inputBasePath;
    this.targetPath = builder.targetPath;
  }

  public boolean isCheckCoCos() {
    return checkCoCos;
  }

  public Path getInputBase() {
    return inputBasePath;
  }

  public Path getTargetPath() {
    return targetPath;
  }

  public static class Builder {
    private boolean checkCoCos = false;
    private Path inputBasePath;
    private Path targetPath;

    public Builder withCoCos() {
      this.checkCoCos = true;
      return this;
    }

    public Builder withCoCos(boolean checkCoCos) {
      this.checkCoCos = checkCoCos;
      return this;
    }

    public Builder withInputBasePath(final String inputBasePath) {
      this.inputBasePath = Paths.get(inputBasePath);
      return this;
    }

    public Builder withInputBasePath(final Path inputBasePath) {
      this.inputBasePath = inputBasePath;
      return this;
    }

    public Builder withTargetPath(final String targetPath) {
      this.targetPath = Paths.get(targetPath);
      return this;
    }

    public Builder withTargetPath(final Path targetPath) {
      this.targetPath = targetPath;
      return this;
    }

    public Configuration build() {
      return new Configuration(this);
    }

  }

}
