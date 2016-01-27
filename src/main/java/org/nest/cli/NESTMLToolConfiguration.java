/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.cli;

/**
 * Data class to store the tool's configuration
 *
 * @author plotnikov
 */
public class NESTMLToolConfiguration {
  private final boolean checkCoCos;
  private final String inputBasePath;
  private final String targetPath;

  private NESTMLToolConfiguration(final Builder builder) {
    this.checkCoCos = builder.checkCoCos;
    this.inputBasePath = builder.inputBasePath;
    this.targetPath = builder.targetPath;
  }

  public boolean isCheckCoCos() {
    return checkCoCos;
  }

  public String getInputBase() {
    return inputBasePath;
  }

  public String getTargetPath() {
    return targetPath;
  }

  public static class Builder {
    private boolean checkCoCos = false;
    private String inputBasePath;
    private String targetPath;

    public Builder withCoCos() {
      this.checkCoCos = true;
      return this;
    }

    public Builder withCoCos(boolean checkCoCos) {
      this.checkCoCos = checkCoCos;
      return this;
    }

    public Builder withInputBasePath(final String inputBasePath) {
      this.inputBasePath = inputBasePath;
      return this;
    }

    public Builder withTargetPath(final String targetPath) {
      this.targetPath = targetPath;
      return this;
    }

    public NESTMLToolConfiguration build() {
      return new NESTMLToolConfiguration(this);
    }

  }

}
