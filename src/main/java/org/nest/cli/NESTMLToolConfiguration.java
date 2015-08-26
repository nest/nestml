package org.nest.cli;

/**
 * Created by user on 05.06.15.
 */
public class NESTMLToolConfiguration {
  private final boolean checkCoCos;


  private final String inputBasePath;
  private final String targetPath;
  private final String modelPath;

  private NESTMLToolConfiguration(final Builder builder) {
    this.checkCoCos = builder.checkCoCos;
    this.inputBasePath = builder.inputBasePath;
    this.modelPath = builder.modelPath;
    this.targetPath = builder.targetPath;
  }

  public boolean isCheckCoCos() {
    return checkCoCos;
  }

  public String getInputBasePath() {
    return inputBasePath;
  }

  public String getModelPath() {
    return modelPath;
  }

  public String getTargetPath() {
    return targetPath;
  }

  public static class Builder {
    private boolean checkCoCos = false;
    private String inputBasePath;
    private String targetPath;
    private String modelPath;

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

    public Builder withModelPath(final String modelPath) {
      this.modelPath = modelPath;
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
