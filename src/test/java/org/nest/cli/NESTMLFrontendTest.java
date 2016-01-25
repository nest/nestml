/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.cli;

import org.apache.commons.cli.CommandLine;
import org.junit.Ignore;
import org.junit.Test;

import java.nio.file.Paths;

import static org.junit.Assert.*;

/**
 * Tests various modis of the {@code NESTMLFrontend} class. For this, several combinations of
 * CLI parameters also invalid combination are provided to the frontend.
 *
 * @author plotnikov
 */
public class NESTMLFrontendTest {
  private final NESTMLFrontend nestmlFrontend = new NESTMLFrontend();

  @Test
  public void testCreationOfConfiguration() throws Exception {

    final String testInputModelsPath = "testInputModelsPath";
    final String targetPath = "targetPath";

    final NESTMLToolConfiguration testant = nestmlFrontend.createCLIConfiguration(new String[] {
        testInputModelsPath,
        "--runningMode", "parseAndCheck",
        "--target", targetPath
    });

    assertTrue(testant.isCheckCoCos());
    assertEquals(testInputModelsPath, testant.getInputBasePath());
    assertEquals(targetPath, testant.getTargetPath());
  }

  @Test(expected = RuntimeException.class)
  public void testInvalidOptions() {
    CommandLine cliArguments = nestmlFrontend.parseCLIArguments(new String[] { "--runningMode"});
    nestmlFrontend.interpretRunningModeArgument(cliArguments);
  }

  @Test
  public void testParseMode() throws Exception {
    CommandLine cliArguments = nestmlFrontend.parseCLIArguments(new String[] { "--runningMode", "parseAndCheck" });
    boolean testant = nestmlFrontend.interpretRunningModeArgument(cliArguments);
    assertTrue(testant);

    cliArguments = nestmlFrontend.parseCLIArguments(new String[] { "--runningMode", "parse" });
    testant = nestmlFrontend.interpretRunningModeArgument(cliArguments);
    assertFalse(testant);

    cliArguments = nestmlFrontend.parseCLIArguments(new String[] { });
    testant = nestmlFrontend.interpretRunningModeArgument(cliArguments);
    assertFalse(testant);

  }

  @Test
  public void testInputPath() throws Exception {
    final String inputModelsPath = "./testTargetPath";
    CommandLine cliArguments = nestmlFrontend.parseCLIArguments(
        new String[] { "--target",  inputModelsPath});
    final String testant = nestmlFrontend.interpretTargetPathArgument(cliArguments);
    assertEquals(inputModelsPath, testant);

  }

}
