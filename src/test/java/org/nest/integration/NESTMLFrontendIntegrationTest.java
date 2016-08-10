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
import org.nest.utils.FilesHelper;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Tests the entire pipeline.
 *
 * @author plotnikov
 */
public class NESTMLFrontendIntegrationTest {
  private final NESTMLFrontend nestmlFrontend = new NESTMLFrontend();
  private static final Path outputPath = Paths.get("target", "integration");
  @Test
  public void testRunUserDefinedOutputFolder() {
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/command_line_base", "--target", outputPath.toString()});
  }

  @Test
  public void testInheritance() {
    FilesHelper.deleteFilesInFolder(outputPath);
    nestmlFrontend.start(new String[] {"src/test/resources/inheritance", "--target", outputPath.toString()});
  }

  @Ignore("PIP supports only 1.0.0 sympy")
  @Test
  public void testInfrastructure() {

    FilesHelper.deleteFilesInFolder(outputPath);
    final CLIConfiguration cliConfiguration = nestmlFrontend.createCLIConfiguration(new String[] {
        "src/test/resources/codegeneration/gif",
        "--target", outputPath.toString()});
    Assert.assertTrue(NESTMLFrontend.checkEnvironment(cliConfiguration));
  }

  @Test
  public void testManually() {
    final String[] args = new String[] {
        "models/aeif_cond_exp_implicit.nestml",
        "--target", outputPath.toString()};

    new NESTMLFrontend().start(args);

  }

}
