package org.nest.cli;

import org.junit.Test;

/**
 * Created by user on 05.06.15.
 */
public class CLIConfigurationExecutorTest {
  private static final String TEST_INPUT_PATH = "src/test/resources/";
  private static final String TARGET_FOLDER = "target";
  private final NESTMLToolConfiguration testConfig;
  private final CLIConfigurationExecutor executor = new CLIConfigurationExecutor();

  public CLIConfigurationExecutorTest() {
    testConfig = new NESTMLToolConfiguration.Builder()
        .withCoCos()
        .withInputBasePath(TEST_INPUT_PATH)
        .withTargetPath(TARGET_FOLDER)
        .build();
  }

  @Test
  public void testExecutionTestConfiguration() {
    executor.execute(testConfig);
  }

}
