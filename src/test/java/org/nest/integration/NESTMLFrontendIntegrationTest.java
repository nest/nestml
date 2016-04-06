/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.integration;

import org.junit.Assert;
import org.junit.Ignore;
import org.junit.Test;
import org.nest.frontend.CLIConfiguration;
import org.nest.frontend.NESTMLFrontend;

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
    nestmlFrontend.start(new String[] {
        "src/test/resources/command_line_base",
        "--target", Paths.get("target","tmpOutput").toString()});
  }

  @Test
  public void testInheritance() {
    nestmlFrontend.start(new String[] {
        "src/test/resources/inheritance",
        "--target", Paths.get("target","tmpOutput").toString()});
  }

  @Test
  public void testBluegeneModels() {
    nestmlFrontend.start(new String[] {
        "src/test/resources/codegeneration/bluegene",
        "--target", Paths.get("target", "codegeneration/bluegene").toString()});
  }

  @Test
  public void testModelsWithInheritance() {
    nestmlFrontend.start(new String[] {
        "src/test/resources/inheritance",
        "--target", Paths.get("target", "codegeneration/inheritance").toString()});
  }

  @Test
  public void testIzhikevichModel() {
    nestmlFrontend.start(new String[] {
        "src/test/resources/codegeneration/izhikevich",
        "--target", Paths.get("target", "codegeneration/izhikevich").toString()});
  }

  @Test
  public void testGIFModel() {
    nestmlFrontend.start(new String[] {
        "src/test/resources/codegeneration/gif",
        "--target", Paths.get("target", "codegeneration/gif").toString()});
  }

  @Test
  public void testInfrastructure() {
    final CLIConfiguration cliConfiguration = nestmlFrontend.createCLIConfiguration(new String[] {
        "src/test/resources/codegeneration/gif",
        "--target", Paths.get("target", "codegeneration/gif").toString()});
    Assert.assertTrue(NESTMLFrontend.checkEnvironment(cliConfiguration));
  }
}
