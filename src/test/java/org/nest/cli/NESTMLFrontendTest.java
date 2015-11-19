/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.cli;

import org.apache.commons.cli.CommandLine;
import org.junit.Ignore;
import org.junit.Test;

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
    final String testModelPath = "testModelPath";
    final String targetPath = "targetPath";

    final NESTMLToolConfiguration testant = nestmlFrontend.createCLIConfiguration(new String[] {
        "--runningMode", "parseAndCheck",
        "--input", testInputModelsPath,
        "--modelPath", testModelPath,
        "--target", targetPath
    });

    assertEquals(true, testant.isCheckCoCos());
    assertEquals(testInputModelsPath, testant.getInputBasePath());
    assertEquals(testModelPath, testant.getModelPath());
    assertEquals(targetPath, testant.getTargetPath());
  }

  //@Test TODO
  public void testInvokeFrontendViaMain() throws Exception {
    NESTMLFrontend.main(new String[]{"--runningMode", "parseAndCheck", ""});
  }

  //@Test
  public void testHelpMessageViaCLI() throws Exception {
    NESTMLFrontend.main(new String[]{"--help"});
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

    ;
  }

  @Test
  public void testInputModelPath() throws Exception {
    final String inputModelsPath = "./testModels";
    CommandLine cliArguments = nestmlFrontend.parseCLIArguments(new String[] { "--input",  inputModelsPath});
    final String testant = nestmlFrontend.interpretInputModelsPathArgument(cliArguments);
    assertEquals(inputModelsPath, testant);

  }

  @Test
  public void testModelPath() throws Exception {
    final String inputModelsPath = "./testModelPath";
    CommandLine cliArguments = nestmlFrontend.parseCLIArguments(new String[] { "--modelPath",  inputModelsPath});
    final String testant = nestmlFrontend.interpretModelPathArgument(cliArguments);
    assertEquals(inputModelsPath, testant);

  }

  @Test
  public void testInputPath() throws Exception {
    final String inputModelsPath = "./testTargetPath";
    CommandLine cliArguments = nestmlFrontend.parseCLIArguments(new String[] { "--target",  inputModelsPath});
    final String testant = nestmlFrontend.interpretTargetPathArgument(cliArguments);
    assertEquals(inputModelsPath, testant);

  }

  @Ignore // CI doesn't have sympy
  @Test
  public void testRun() {

    nestmlFrontend.handleCLIArguments(new String[]{
        "src/test/resources/codegeneration/iaf_neuron_ode_module.nestml",
        "--target", "tmpOutput"});
  }

}
