/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import org.junit.Ignore;
import org.junit.Test;
import org.nest.cli.NESTMLFrontend;

import java.nio.file.Paths;

/**
 * TODO
 *
 * @author plotnikov
 */
@Ignore("Don't run this tests on github")
public class NESTMLFrontendIntegrationTest {
  private final NESTMLFrontend nestmlFrontend = new NESTMLFrontend();

  @Test
  public void testRunUserDefinedOutputFolder() {
    nestmlFrontend.handleConsoleArguments(new String[] {
        "src/test/resources/command_line_base",
        "--target", Paths.get("target","tmpOutput").toString()});
  }

  @Test
  public void testInheritance() {
    nestmlFrontend.handleConsoleArguments(new String[] {
        "src/test/resources/inheritance",
        "--target", Paths.get("target","tmpOutput").toString()});
  }

  @Test
  public void testBluegenModels() {
    nestmlFrontend.handleConsoleArguments(new String[] {
        "src/test/resources/codegeneration/bluegene",
        "--target", Paths.get("target", "codegeneration/bluegene").toString()});
  }

  @Test
  public void testModelsWithInheritance() {
    nestmlFrontend.handleConsoleArguments(new String[] {
        "src/test/resources/inheritance",
        "--target", Paths.get("target", "codegeneration/inheritance").toString()});
  }
}
